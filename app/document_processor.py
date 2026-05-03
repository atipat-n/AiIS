"""
Hard Rules Checker — document_processor.py
Validates margins, fonts, title sizes, and logo in .docx files
based on KKU thesis formatting guidelines.

v3: Returns HardRuleError with location/issue/detail format.
"""

import io
import re
from docx import Document
from docx.shared import Inches, Pt, Emu
from PIL import Image
from models import HardRuleError


# ──────────────────────────────────────────────
# Margin definitions per slot
# ──────────────────────────────────────────────

SLOT_MARGINS = {
    1: {"Top": 2.5, "Left": 1.5, "Bottom": 1.0, "Right": 1.0},  # Front Matter (logo page)
    4: {"Top": 1.5, "Left": 1.5, "Bottom": 1.0, "Right": 1.0},  # Main Content
}

MARGIN_TOLERANCE = 0.1  # inches


def check_margins(doc: Document, slot_number: int) -> list[HardRuleError]:
    """
    Check document margins against the expected values for the given slot.
    Returns a list of HardRuleError for any violations.
    """
    expected = SLOT_MARGINS.get(slot_number)
    if expected is None:
        return []

    errors = []
    section = doc.sections[0]

    actual = {
        "Top": section.top_margin.inches,
        "Bottom": section.bottom_margin.inches,
        "Left": section.left_margin.inches,
        "Right": section.right_margin.inches,
    }

    for side, expected_val in expected.items():
        actual_val = actual[side]
        if abs(actual_val - expected_val) > MARGIN_TOLERANCE:
            errors.append(HardRuleError(
                location="Section 1, Page Setup",
                issue=f"ระยะขอบ{_thai_side(side)}ผิด (Wrong {side} Margin)",
                detail=(
                    f"พบ {actual_val:.2f} นิ้ว (Found {actual_val:.2f} inch). "
                    f"ค่าที่ถูกต้อง: {expected_val:.1f} นิ้ว (Expected {expected_val:.1f} inch)"
                ),
                severity="error",
                rule_type="margin",
            ))

    return errors


def _thai_side(side: str) -> str:
    return {"Top": "บน", "Bottom": "ล่าง", "Left": "ซ้าย", "Right": "ขวา"}.get(side, side)


# ──────────────────────────────────────────────
# Font checks
# ──────────────────────────────────────────────

EXPECTED_FONT = "TH Sarabun New"


def check_fonts(doc: Document) -> list[HardRuleError]:
    """
    Check that all runs use TH Sarabun New (or inherit it from the style).
    Flags the first occurrence per paragraph of a wrong font.
    """
    errors = []
    flagged_paras = set()

    for i, para in enumerate(doc.paragraphs):
        if not para.text.strip():
            continue
        for run in para.runs:
            font_name = run.font.name
            # Skip runs where font is inherited (None) — assume correct
            if font_name is not None and font_name != EXPECTED_FONT:
                if i not in flagged_paras:
                    flagged_paras.add(i)
                    preview = para.text.strip()[:60]
                    errors.append(HardRuleError(
                        location=f"Paragraph {i+1}",
                        issue=f"ฟอนต์ผิด (Wrong Font)",
                        detail=(
                            f"ใช้ฟอนต์ '{font_name}' ในย่อหน้า: \"{preview}...\" "
                            f"(ควรใช้ '{EXPECTED_FONT}')"
                        ),
                        severity="error",
                        rule_type="font",
                    ))
    return errors


# ──────────────────────────────────────────────
# Title size check (Slot 1 only)
# ──────────────────────────────────────────────

def check_title_size(doc: Document) -> list[HardRuleError]:
    """
    Front Matter: the thesis title (first non-empty paragraph) must be
    16pt bold or 18pt bold using TH Sarabun New.
    """
    errors = []
    for i, para in enumerate(doc.paragraphs):
        if not para.text.strip():
            continue
        # This is the first non-empty paragraph — treat as title
        has_valid_size = False
        is_bold = False
        found_sizes = []
        for run in para.runs:
            size = run.font.size
            if size is not None:
                pt_val = size.pt
                found_sizes.append(pt_val)
                if pt_val in (16, 18):
                    has_valid_size = True
                if run.font.bold:
                    is_bold = True

        preview = para.text.strip()[:50]
        size_str = ", ".join(f"{s:.0f}pt" for s in found_sizes) if found_sizes else "ไม่ระบุ"

        if not has_valid_size:
            errors.append(HardRuleError(
                location=f"Paragraph {i+1} (Title)",
                issue="ขนาดหัวข้อผิด (Wrong Title Size)",
                detail=(
                    f"หัวข้อ: \"{preview}\" — ขนาดที่พบ: {size_str} "
                    f"(ควรเป็น 16pt หรือ 18pt ตัวหนา)"
                ),
                severity="error",
                rule_type="title_size",
            ))
        elif not is_bold:
            errors.append(HardRuleError(
                location=f"Paragraph {i+1} (Title)",
                issue="หัวข้อไม่เป็นตัวหนา (Title Not Bold)",
                detail=(
                    f"หัวข้อ: \"{preview}\" — ขนาดถูกต้อง ({size_str}) "
                    f"แต่ต้องตั้งค่าเป็นตัวหนา (Bold)"
                ),
                severity="warning",
                rule_type="title_size",
            ))
        break  # Only check the first non-empty paragraph

    return errors


# ──────────────────────────────────────────────
# Logo validation (Slot 1 only)
# ──────────────────────────────────────────────

EXPECTED_LOGO_HEIGHT_CM = 1.8
EXPECTED_LOGO_WIDTH_CM = 1.1
LOGO_TOLERANCE_CM = 0.3
DEFAULT_DPI = 96


def check_logo(doc: Document) -> list[HardRuleError]:
    """
    Extract the first image from the document, then check:
    1. It should be grayscale (not RGB/RGBA).
    2. Its dimensions should be approximately 1.8cm H × 1.1cm W.
    """
    errors = []

    # python-docx stores images in inline shapes and as relationship targets
    images = []
    for rel in doc.part.rels.values():
        if "image" in rel.reltype:
            images.append(rel.target_part.blob)

    if not images:
        errors.append(HardRuleError(
            location="Cover Page",
            issue="ไม่พบตรามหาวิทยาลัย (Logo Missing)",
            detail="ไม่พบรูปภาพตรามหาวิทยาลัยในเอกสาร ควรมีตราอยู่ที่หน้าปก",
            severity="error",
            rule_type="logo",
        ))
        return errors

    # Validate the first image
    img_bytes = images[0]
    try:
        img = Image.open(io.BytesIO(img_bytes))
    except Exception:
        errors.append(HardRuleError(
            location="Cover Page, Image 1",
            issue="อ่านรูปภาพไม่ได้ (Unreadable Image)",
            detail="ไม่สามารถอ่านรูปภาพตรามหาวิทยาลัยที่ฝังในเอกสารได้",
            severity="error",
            rule_type="logo",
        ))
        return errors

    # 1. Check color mode (should be grayscale 'L', not 'RGB' or 'RGBA')
    if img.mode not in ("L", "LA", "1"):
        errors.append(HardRuleError(
            location="Cover Page, Image 1",
            issue="ตราเป็นภาพสี (Logo Not Grayscale)",
            detail=(
                f"ตรามหาวิทยาลัยเป็นภาพโหมด '{img.mode}' (สี) "
                f"ควรเป็นภาพขาวดำ Grayscale (โหมด 'L')"
            ),
            severity="error",
            rule_type="logo",
        ))

    # 2. Check dimensions (convert pixels to cm)
    dpi = img.info.get("dpi", (DEFAULT_DPI, DEFAULT_DPI))
    dpi_x, dpi_y = dpi if isinstance(dpi, tuple) else (dpi, dpi)

    width_cm = (img.width / dpi_x) * 2.54
    height_cm = (img.height / dpi_y) * 2.54

    if abs(height_cm - EXPECTED_LOGO_HEIGHT_CM) > LOGO_TOLERANCE_CM:
        errors.append(HardRuleError(
            location="Cover Page, Image 1",
            issue="ความสูงตราผิด (Wrong Logo Height)",
            detail=(
                f"ความสูงตรามหาวิทยาลัย: {height_cm:.2f} ซม. "
                f"(ควรประมาณ {EXPECTED_LOGO_HEIGHT_CM} ซม.)"
            ),
            severity="warning",
            rule_type="logo",
        ))

    if abs(width_cm - EXPECTED_LOGO_WIDTH_CM) > LOGO_TOLERANCE_CM:
        errors.append(HardRuleError(
            location="Cover Page, Image 1",
            issue="ความกว้างตราผิด (Wrong Logo Width)",
            detail=(
                f"ความกว้างตรามหาวิทยาลัย: {width_cm:.2f} ซม. "
                f"(ควรประมาณ {EXPECTED_LOGO_WIDTH_CM} ซม.)"
            ),
            severity="warning",
            rule_type="logo",
        ))

    return errors


# ──────────────────────────────────────────────
# Extract full text from document
# ──────────────────────────────────────────────

def extract_text(doc: Document) -> str:
    """Extract all non-empty paragraph text from the document."""
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())


# ──────────────────────────────────────────────
# TOC Heading Extraction (Slot 3)
# ──────────────────────────────────────────────

_TOC_STRIP_RE = re.compile(r'[\.\-–—\s\t]+\d+\s*$')

def extract_toc_headings(doc: Document) -> list[str]:
    """
    Extract heading texts from a Table of Contents document.
    Strips trailing dot-leaders, tabs, and page numbers.
    """
    headings = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text or len(text) < 3:
            continue
        clean = _TOC_STRIP_RE.sub('', text).strip()
        clean = clean.replace('\t', ' ').strip()
        if clean and len(clean) >= 3:
            headings.append(clean)
    return headings

# ──────────────────────────────────────────────
# Content Heading Extraction (Slot 4 chapters)
# ──────────────────────────────────────────────

def extract_content_headings(doc: Document) -> list[str]:
    """
    Extract headings from content by detecting:
    1. Paragraphs with Heading styles (Heading 1, Heading 2, etc.)
    2. Paragraphs where ALL runs are bold
    """
    headings = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text or len(text) < 3:
            continue

        # Method 1: Heading style
        if para.style and para.style.name and para.style.name.startswith('Heading'):
            headings.append(text)
            continue

        # Method 2: All non-empty runs are bold (skip long body text)
        runs_with_text = [r for r in para.runs if r.text.strip()]
        if runs_with_text and all(r.bold for r in runs_with_text):
            if len(text) < 120:
                headings.append(text)

    return headings

# ──────────────────────────────────────────────
# TOC vs Content Matcher
# ──────────────────────────────────────────────

def match_toc_vs_content(
    toc_headings: list[str],
    content_headings: list[str],
) -> list[HardRuleError]:
    """
    Compare content headings against TOC headings.
    Flags content headings that don't appear in the TOC list.
    """
    if not toc_headings:
        return []

    errors = []
    toc_set = {h.strip() for h in toc_headings}

    for heading in content_headings:
        clean = heading.strip()
        if clean not in toc_set:
            errors.append(HardRuleError(
                location="Content Heading",
                issue="หัวข้อไม่ตรงกับสารบัญ (TOC Mismatch)",
                detail=(
                    f"หัวข้อ \"{clean[:80]}\" ในเนื้อหาไม่ตรงกับรายการในสารบัญ "
                    f"— กรุณาตรวจสอบการสะกดและอัปเดตสารบัญให้ตรงกัน"
                ),
                severity="warning",
                rule_type="toc_mismatch",
            ))

    return errors

# ──────────────────────────────────────────────
# Main entry point per slot
# ──────────────────────────────────────────────

SLOT_NAMES = {
    1: "ส่วนหน้า (Front Matter)",
    2: "บทคัดย่อ (Abstract)",
    3: "สารบัญ (Table of Contents)",
    4: "เนื้อหา (Main Content)",
    5: "บรรณานุกรม (References)",
}


def process_slot(doc: Document, slot_number: int) -> list[HardRuleError]:
    """
    Run all applicable hard-rule checks for the given slot.
    Returns a combined list of HardRuleError with location/issue/detail.
    """
    errors = []

    # Slot 1: Front Matter -> Needs margins, fonts, title size, logo
    if slot_number == 1:
        errors.extend(check_margins(doc, 1))
        errors.extend(check_fonts(doc))
        errors.extend(check_title_size(doc))
        errors.extend(check_logo(doc))

    # Slot 4: Main Content -> Needs margins, fonts
    elif slot_number == 4:
        errors.extend(check_margins(doc, 4))
        errors.extend(check_fonts(doc))

    return errors
