"""
KKU Thesis AI Checker — Pro Version (v4.1)
Main FastAPI application with 5-slot upload endpoints.
Slot 4 has 5 sub-slots (4.1-4.5) for Chapters 1-5.

v4.1: Restored sequence checker, TOC matcher, typo scanner, removed PDF.
"""

import io
import uuid
from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from docx import Document

from models import SessionData, SlotResult, HardRuleError, CrossCheckResult
from document_processor import (
    process_slot, extract_text, SLOT_NAMES,
    extract_toc_headings, extract_content_headings, match_toc_vs_content,
)
from sequence_checker import check_table_figure_sequences
from citation_engine import extract_in_text_citations, extract_reference_authors, cross_check
from ai_service import call_kku_llm


# ──────────────────────────────────────────────
# App setup
# ──────────────────────────────────────────────

app = FastAPI(
    title="KKU Thesis AI Checker Pro",
    description="ระบบตรวจสอบรูปแบบวิทยานิพนธ์อัตโนมัติ มหาวิทยาลัยขอนแก่น",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store
sessions: dict[str, SessionData] = {}


def get_or_create_session(session_id: str) -> SessionData:
    if session_id not in sessions:
        sessions[session_id] = SessionData()
    return sessions[session_id]


# ──────────────────────────────────────────────
# Chapter names for Slot 4 sub-slots
# ──────────────────────────────────────────────

CHAPTER_NAMES = {
    1: "บทที่ 1 บทนำ (Introduction)",
    2: "บทที่ 2 ทบทวนวรรณกรรม (Literature Review)",
    3: "บทที่ 3 ระเบียบวิธีวิจัย (Methodology)",
    4: "บทที่ 4 ผลการวิจัย (Results)",
    5: "บทที่ 5 สรุปและอภิปราย (Conclusion)",
}


def _build_result(slot_number: int, slot_name: str, errors: list[HardRuleError],
                  ai_feedback: str, full_text: str) -> SlotResult:
    """Build a standardized SlotResult from check outputs."""
    error_count = sum(1 for e in errors if e.severity == "error")
    warning_count = sum(1 for e in errors if e.severity == "warning")

    return SlotResult(
        slot_number=slot_number,
        slot_name=slot_name,
        status="passed" if len(errors) == 0 else "issues_found",
        hard_rules_errors=errors,
        ai_soft_rules_feedback=ai_feedback,
        error_count=error_count,
        warning_count=warning_count,
        full_text=full_text,
    )


# ──────────────────────────────────────────────
# Slot upload endpoint (slots 1, 2, 3, 5)
# ──────────────────────────────────────────────

@app.post("/api/slot/{slot_number}")
async def upload_slot(
    slot_number: int,
    file: UploadFile = File(...),
    session_id: str = Query(...),
):
    """
    Upload a .docx file for a specific slot (1, 2, 3, or 5).
    Returns structured JSON with hard_rules_errors and ai_soft_rules_feedback.
    """
    if slot_number not in (1, 2, 3, 5):
        raise HTTPException(400, "ใช้ /api/slot/4/{chapter} สำหรับเนื้อหาบทที่ 1-5")

    if not file.filename.endswith(".docx"):
        raise HTTPException(400, "กรุณาอัปโหลดไฟล์ .docx เท่านั้น")

    session = get_or_create_session(session_id)
    file_bytes = await file.read()

    try:
        doc = Document(io.BytesIO(file_bytes))
    except Exception as e:
        raise HTTPException(400, f"ไม่สามารถอ่านไฟล์ .docx ได้: {str(e)}")

    # ── 1. Hard Rules Check ──
    errors = process_slot(doc, slot_number)

    # ── 2. Extract text ──
    full_text = extract_text(doc)

    # ── 3. Slot-specific logic ──
    if slot_number == 3:
        # TOC: extract headings and store in session
        session.toc_headings = extract_toc_headings(doc)

    if slot_number == 5:
        # References: extract authors for citation cross-check
        session.reference_authors = extract_reference_authors(full_text)

    # Auto cross-check if both slots are available
    if session.in_text_citations and session.reference_authors:
        session.cross_check = cross_check(
            session.in_text_citations,
            session.reference_authors,
        )

    # ── 4. AI Soft Rules (chunked) ──
    # Handled by frontend now.

    # ── 5. Build structured result ──
    result = _build_result(
        slot_number=slot_number,
        slot_name=SLOT_NAMES.get(slot_number, "Unknown"),
        errors=errors,
        ai_feedback=None,
        full_text=full_text,
    )

    session.slot_results[slot_number] = result

    # Build response
    response = result.model_dump()
    response["total_chunks"] = 0

    # Include TOC heading count for Slot 3
    if slot_number == 3:
        response["toc_headings_count"] = len(session.toc_headings)

    if session.cross_check:
        response["cross_check"] = session.cross_check.model_dump()

    return response


# ──────────────────────────────────────────────
# Slot 4 Sub-slot (Chapters 1-5)
# ──────────────────────────────────────────────

@app.post("/api/slot/4/{chapter}")
async def upload_slot4_chapter(
    chapter: int,
    file: UploadFile = File(...),
    session_id: str = Query(...),
):
    """
    Upload a .docx file for Slot 4, specific chapter (1-5).
    Hard rules (margins/fonts) are checked.
    Citations are extracted and aggregated across all chapters.
    AI feedback uses chapter-specific prompts.
    """
    if chapter not in range(1, 6):
        raise HTTPException(400, "Chapter must be between 1 and 5")

    if not file.filename.endswith(".docx"):
        raise HTTPException(400, "กรุณาอัปโหลดไฟล์ .docx เท่านั้น")

    session = get_or_create_session(session_id)
    file_bytes = await file.read()

    try:
        doc = Document(io.BytesIO(file_bytes))
    except Exception as e:
        raise HTTPException(400, f"ไม่สามารถอ่านไฟล์ .docx ได้: {str(e)}")

    # ── 1. Hard Rules Check (margins + fonts + typos) ──
    errors = process_slot(doc, 4)

    # ── 2. Sequence Checker — table/figure numbering ──
    errors.extend(check_table_figure_sequences(doc, chapter))

    # ── 3. Extract text ──
    full_text = extract_text(doc)

    # ── 4. TOC Matcher — compare headings against stored TOC ──
    content_headings = extract_content_headings(doc)
    session.content_headings[chapter] = content_headings

    if session.toc_headings:
        errors.extend(match_toc_vs_content(
            session.toc_headings,
            content_headings,
        ))

    # ── 5. Citation extraction — aggregate across all chapters ──
    chapter_citations = extract_in_text_citations(full_text)
    session.chapter_citations[chapter] = chapter_citations

    # Aggregate all chapter citations into the main set
    all_citations = set()
    for ch_cites in session.chapter_citations.values():
        all_citations |= ch_cites
    session.in_text_citations = all_citations

    # Auto cross-check if references are also available
    if session.in_text_citations and session.reference_authors:
        session.cross_check = cross_check(
            session.in_text_citations,
            session.reference_authors,
        )

    # ── 4. AI Soft Rules (chapter-specific prompt, chunked) ──
    # Handled by frontend now.
    chapter_name = CHAPTER_NAMES.get(chapter, f"บทที่ {chapter}")

    # ── 5. Build structured result ──
    result = _build_result(
        slot_number=4,
        slot_name=chapter_name,
        errors=errors,
        ai_feedback=None,
        full_text=full_text,
    )

    sub_slot_key = f"4.{chapter}"
    session.slot_results[sub_slot_key] = result

    # Build response
    response = result.model_dump()
    response["chapter"] = chapter
    response["sub_slot"] = sub_slot_key
    response["citations_found"] = len(chapter_citations)
    response["total_citations"] = len(session.in_text_citations)
    response["content_headings_found"] = len(content_headings)
    response["toc_available"] = len(session.toc_headings) > 0
    response["total_chunks"] = 0


    if session.cross_check:
        response["cross_check"] = session.cross_check.model_dump()

    return response


# ──────────────────────────────────────────────
# Cross-check endpoint
# ──────────────────────────────────────────────

@app.get("/api/crosscheck/{session_id}")
async def get_crosscheck(session_id: str):
    """Get the citation cross-check results for this session."""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(404, "ไม่พบเซสชันนี้")

    if not session.cross_check:
        return CrossCheckResult(is_complete=False).model_dump()

    return session.cross_check.model_dump()


# ──────────────────────────────────────────────
# AI Chunk Endpoint
# ──────────────────────────────────────────────

class ChunkRequest(BaseModel):
    chunk_text: str
    slot_number: int
    chapter: int = 0
    chunk_index: int
    total_chunks: int

@app.post("/api/ai_chunk")
async def process_ai_chunk(req: ChunkRequest):
    try:
        if req.slot_number == 4:
            prompt = f"ตรวจสอบเอกสาร: {CHAPTER_NAMES.get(req.chapter, f'บทที่ {req.chapter}')}"
        else:
            prompt = f"ตรวจสอบเอกสารส่วน: {SLOT_NAMES.get(req.slot_number, 'Unknown')}"
            
        result_json_str = call_kku_llm(
            prompt=prompt,
            chunk_text=req.chunk_text,
            slot_number=req.slot_number,
            chapter=req.chapter
        )
        return {"success": True, "data": result_json_str}
    except Exception as e:
        err_str = str(e)
        if "429" in err_str or "Quota" in err_str:
            return {"success": False, "error": "429_QUOTA", "message": err_str}
        return {"success": False, "error": "API_ERROR", "message": err_str}


# ──────────────────────────────────────────────
# Session status
# ──────────────────────────────────────────────

@app.get("/api/session/{session_id}")
async def get_session_status(session_id: str):
    """Get the overall session status (which slots have been uploaded)."""
    session = sessions.get(session_id)
    if not session:
        return {"slots_completed": [], "has_crosscheck": False}

    return {
        "slots_completed": list(session.slot_results.keys()),
        "has_crosscheck": session.cross_check is not None,
    }


# ──────────────────────────────────────────────
# Serve static frontend
# ──────────────────────────────────────────────

app.mount("/", StaticFiles(directory="static", html=True), name="static")


# ──────────────────────────────────────────────
# Run
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
