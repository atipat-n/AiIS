"""
AI Soft Rules Service — ai_service.py
Google Gemini integration for KKU Thesis AI Checker.
Chunking & Iterative Extraction architecture.
"""

import google.generativeai as genai
import time

# ──────────────────────────────────────────────
# ⚠️ REPLACE THIS WITH YOUR REAL GEMINI API KEY
# ──────────────────────────────────────────────
GEMINI_API_KEY = "AIzaSyByAlVSBgR6zoId8M7gOOeh_5YRHbyieoo"
genai.configure(api_key=GEMINI_API_KEY)


# ──────────────────────────────────────────────
# Slot-specific system prompts
# ──────────────────────────────────────────────
SLOT_PROMPTS = {
    1: (
        "คุณคือผู้เชี่ยวชาญด้านการตรวจรูปแบบสารนิพนธ์ มข. "
        "ตรวจสอบส่วนหน้า (ปกนอก ปกใน ใบรับรอง) ว่ามีองค์ประกอบครบถ้วน "
        "ได้แก่ ชื่อเรื่อง ชื่อผู้เขียน ชื่อสถาบัน ปีการศึกษา คำนำหน้านาม"
    ),
    2: (
        "คุณคือผู้เชี่ยวชาญด้านการตรวจบทคัดย่อสารนิพนธ์ "
        "ตรวจสอบโครงสร้างบทคัดย่อ: ต้องมีวัตถุประสงค์ ระเบียบวิธีวิจัย ผลการวิจัย "
        "และข้อสรุป ความยาวไม่เกิน 1 หน้า ทั้งภาษาไทยและภาษาอังกฤษ"
    ),
    3: (
        "คุณคือผู้เชี่ยวชาญด้านการตรวจสารบัญสารนิพนธ์ "
        "ตรวจสอบว่าสารบัญมีหัวข้อครบถ้วน เลขหน้าถูกต้อง "
        "รูปแบบการจัดเรียงหัวข้อใหญ่และหัวข้อย่อยเป็นไปตามมาตรฐาน"
    ),
    5: (
        "คุณคือผู้เชี่ยวชาญด้านการตรวจบรรณานุกรม "
        "ตรวจสอบรูปแบบการอ้างอิงตาม APA 7th Edition "
        "ทั้งรูปแบบภาษาไทยและภาษาอังกฤษ เรียงลำดับตัวอักษร"
    ),
}

# ──────────────────────────────────────────────
# Chapter-specific prompts for Slot 4 sub-slots
# (Micro-RAG per Chapter)
# ──────────────────────────────────────────────
CHAPTER_PROMPTS = {
    1: (
        "คุณคือผู้เชี่ยวชาญด้านการตรวจบทที่ 1 บทนำ ของสารนิพนธ์ "
        "ตรวจสอบความสอดคล้องระหว่างวัตถุประสงค์การวิจัยกับคำถามการวิจัย "
        "ตรวจความชัดเจนของปัญหาวิจัย ขอบเขต และข้อจำกัดของการศึกษา "
        "Focus: alignment between objectives and research questions"
    ),
    2: (
        "คุณคือผู้เชี่ยวชาญด้านการตรวจบทที่ 2 ทบทวนวรรณกรรม ของสารนิพนธ์ "
        "ตรวจสอบความเชื่อมโยงของทฤษฎี ความหนาแน่นของการอ้างอิง "
        "และรูปแบบการอ้างอิงในเนื้อหาว่าถูกต้องตาม APA 7th Edition "
        "Focus: theoretical connections and dense citation formatting"
    ),
    3: (
        "คุณคือผู้เชี่ยวชาญด้านการตรวจบทที่ 3 ระเบียบวิธีวิจัย ของสารนิพนธ์ "
        "ตรวจสอบการเขียนเชิงกระบวนการ การใช้กาลเวลาที่เหมาะสม "
        "ความสมบูรณ์ของขั้นตอนการวิจัย ประชากร กลุ่มตัวอย่าง เครื่องมือ "
        "Focus: procedural writing and appropriate tense usage"
    ),
    4: (
        "คุณคือผู้เชี่ยวชาญด้านการตรวจบทที่ 4 ผลการวิจัย ของสารนิพนธ์ "
        "ตรวจสอบการรายงานข้อมูลเชิงวัตถุวิสัย ไม่มีความคิดเห็นส่วนตัว "
        "การนำเสนอตาราง กราฟ สถิติ ต้องชัดเจนและไม่แทรกอคติ "
        "Focus: objective reporting of data without personal bias or opinions"
    ),
    5: (
        "คุณคือผู้เชี่ยวชาญด้านการตรวจบทที่ 5 สรุปและอภิปราย ของสารนิพนธ์ "
        "ตรวจสอบว่าบทสรุปตอบวัตถุประสงค์การวิจัยครบถ้วน "
        "การอภิปรายมีเหตุผลสอดคล้อง มีข้อเสนอแนะที่ชัดเจน "
        "Focus: answering research objectives and logical discussion"
    ),
}

METICULOUS_PROMPT = (
    "You are a highly detailed and meticulous academic auditor. "
    "Analyze this specific section of the IS document with extreme care. "
    "Do not rush. Identify every single formatting, grammatical, or contextual error. "
    "You MUST return ONLY a raw JSON array of objects without any markdown wrappers (no ```json). "
    "Each object must have exactly these keys: 'location', 'issue', 'fix'. "
    "If no errors are found, return exactly []. "
    "Example format:\n"
    "[\n"
    "  {\"location\": \"ย่อหน้าที่ 1 บรรทัดที่ 2\", \"issue\": \"สะกดคำผิด\", \"fix\": \"แก้ไข 'อณุญาติ' เป็น 'อนุญาต'\"}\n"
    "]"
)



_MODEL_NAMES = ["gemini-1.5-flash", "gemini-3.1-flash-lite-preview"]


def _generate_with_fallback(prompt: str) -> str:
    """Try Gemini models in preference order and return the first successful response."""
    last_err: Exception = RuntimeError("No models configured")
    for name in _MODEL_NAMES:
        try:
            model = genai.GenerativeModel(name)
            return model.generate_content(prompt).text
        except Exception as e:
            last_err = e
    raise last_err


def call_kku_llm(prompt: str, chunk_text: str, slot_number: int = 1, chapter: int = 0) -> str:
    """
    Send a single chunk to Google Gemini for meticulous soft-rule analysis.
    Raises exception on API errors.
    """
    if slot_number == 4 and chapter in CHAPTER_PROMPTS:
        domain_prompt = CHAPTER_PROMPTS[chapter]
    else:
        domain_prompt = SLOT_PROMPTS.get(slot_number, SLOT_PROMPTS.get(1, ""))

    system_prompt = domain_prompt + "\n\n" + METICULOUS_PROMPT
    
    full_prompt = (
        system_prompt
        + "\n\n[ข้อความที่จะตรวจสอบ]:\n"
        + chunk_text
        + "\n\n"
        + prompt
    )
    
    return _generate_with_fallback(full_prompt)
