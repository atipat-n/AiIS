"""
Fast Typo & Slang Scanner — typo_scanner.py (v2 — Massive Expansion)
Dictionary-based scanner for forbidden words in academic Thai writing.
NO AI/LLM — pure string matching.

Four categories:
  A) Pronouns (strictly forbidden in academic tone)
  B) Spoken/Slang/Informal & Filler words
  C) Logical Transitions to Avoid (overused/ambiguous — flag for review)
  D) Common Thai Misspellings (flag & suggest correction)
"""

from docx import Document
from models import HardRuleError


# ══════════════════════════════════════════════
# Category A: Forbidden Pronouns (Non-Academic)
# ══════════════════════════════════════════════

CATEGORY_A_PRONOUNS: dict[str, str] = {
    "ผม":       "สรรพนามบุรุษที่ 1 — ห้ามใช้ในงานวิชาการ ควรใช้ 'ผู้วิจัย'",
    "ดิฉัน":     "สรรพนามบุรุษที่ 1 — ห้ามใช้ในงานวิชาการ ควรใช้ 'ผู้วิจัย'",
    "หนู":       "สรรพนามบุรุษที่ 1 — ห้ามใช้ในงานวิชาการ",
    "ข้าพเจ้า":  "สรรพนามบุรุษที่ 1 — ควรใช้ 'ผู้วิจัย' แทน",
    "พวกเรา":   "สรรพนามบุรุษที่ 1 พหูพจน์ — ห้ามใช้ในงานวิชาการ",
    "เรา":       "สรรพนามบุรุษที่ 1 — ควรใช้ 'ผู้วิจัย' แทน",
    "คุณ":       "สรรพนามบุรุษที่ 2 — ห้ามใช้ในงานวิชาการ",
    "ท่าน":      "สรรพนามบุรุษที่ 2 — ห้ามใช้ในงานวิชาการ",
    "กระผม":    "สรรพนามบุรุษที่ 1 — ห้ามใช้ในงานวิชาการ",
    "มึง":       "สรรพนามหยาบคาย — ห้ามใช้ในงานวิชาการอย่างเด็ดขาด",
    "กู":        "สรรพนามหยาบคาย — ห้ามใช้ในงานวิชาการอย่างเด็ดขาด",
    "แก":       "สรรพนามบุรุษที่ 2 ไม่สุภาพ — ห้ามใช้ในงานวิชาการ",
    "เค้า":      "สรรพนามบุรุษที่ 3 ภาษาพูด — ควรใช้ 'เขา' หรือระบุชื่อ",
}


# ══════════════════════════════════════════════
# Category B: Spoken/Slang & Filler Words
# ══════════════════════════════════════════════

CATEGORY_B_INFORMAL: dict[str, str] = {
    # ── ภาษาพูดทั่วไป ──
    "เยอะแยะ":       "ภาษาพูด — ควรใช้ 'จำนวนมาก' หรือ 'หลากหลาย'",
    "แบบว่า":         "ภาษาพูด/สแลง — ควรตัดออก",
    "คือว่า":          "ภาษาพูด — ควรใช้ 'กล่าวคือ' หรือตัดออก",
    "คือแบบ":         "ภาษาพูด/สแลง — ควรตัดออก",
    "โอเค":           "คำทับศัพท์ไม่เป็นทางการ — ควรใช้ 'ตกลง' หรือ 'เห็นด้วย'",
    "จริงๆแล้ว":      "ภาษาพูด — ควรตัดออกหรือใช้ 'แท้จริงแล้ว'",
    "ก็คือ":           "ภาษาพูด — ควรใช้ 'คือ' หรือ 'ได้แก่'",
    "อันนี้":          "ภาษาพูด — ควรใช้ 'สิ่งนี้' หรือระบุให้ชัดเจน",
    "ประมาณว่า":     "ภาษาพูด — ควรตัดออก",
    "ถือว่า":          "ภาษาพูด — ควรใช้ 'จัดว่า' หรือ 'ถือเป็น'",
    "นับว่า":          "ภาษาพูด — ควรใช้ 'จัดว่า'",
    # ── คำซ้ำ/ย่อ ──
    "เรื่อยๆ":         "ภาษาพูด — ควรใช้ 'อย่างต่อเนื่อง'",
    "บ่อยๆ":          "ภาษาพูด — ควรใช้ 'บ่อยครั้ง' หรือ 'เป็นประจำ'",
    "มากๆ":           "ภาษาพูด — ควรใช้ 'อย่างมาก' หรือ 'เป็นอย่างยิ่ง'",
    "สุดๆ":            "ภาษาพูด/สแลง — ควรใช้ 'อย่างยิ่ง'",
    # ── สแลง/ศัพท์โซเชียล ──
    "แอบ":             "ภาษาพูด (ในความหมายเชิงอารมณ์) — ไม่เหมาะสม",
    "ปัง":              "สแลง — ไม่เหมาะสมในงานวิชาการ",
    "ขิต":              "สแลง — ไม่เหมาะสมในงานวิชาการ",
    "ยืนหนึ่ง":         "สแลง — ไม่เหมาะสมในงานวิชาการ",
    "ตัวแม่":           "สแลง — ไม่เหมาะสมในงานวิชาการ",
    "เต็มคาราเบล":    "สแลง — ไม่เหมาะสมในงานวิชาการ",
    "ฟิน":              "สแลง — ไม่เหมาะสมในงานวิชาการ",
    "อิน":              "สแลง (ในความหมาย 'อินมาก') — ไม่เหมาะสม",
    "เลิศ":             "ภาษาพูดเชิงอารมณ์ — ไม่เหมาะในบริบทวิชาการ",
    "ดีงาม":           "สแลง — ไม่เหมาะสมในงานวิชาการ",
    "อะไรอย่างเงี้ย":  "ภาษาพูดอย่างยิ่ง — ห้ามใช้ในงานวิชาการ",
    "ไรงี้":            "ภาษาพูดอย่างยิ่ง — ห้ามใช้ในงานวิชาการ",
    # ── คำลงท้าย/อนุภาค ──
    "นะ":              "คำลงท้ายภาษาพูด — ห้ามใช้ในงานวิชาการ",
    "ค่ะ":             "คำลงท้ายภาษาพูด — ห้ามใช้ในงานเขียนวิชาการ",
    "ครับ":            "คำลงท้ายภาษาพูด — ห้ามใช้ในงานเขียนวิชาการ",
    "จ้ะ":             "คำลงท้ายภาษาพูด — ห้ามใช้ในงานวิชาการ",
    "ป่ะ":             "คำลงท้ายภาษาพูด — ห้ามใช้ในงานวิชาการ",
    "มั้ง":            "คำลงท้ายภาษาพูด — ห้ามใช้ในงานวิชาการ",
}


# ══════════════════════════════════════════════
# Category C: Logical Transitions to Avoid
# (Overused/Ambiguous — flag for manual review)
# ══════════════════════════════════════════════

CATEGORY_C_TRANSITIONS: dict[str, str] = {
    "ซึ่ง":          "คำเชื่อมที่มักใช้มากเกินไป — พิจารณาตัดออกหรือเรียบเรียงใหม่",
    "ทว่า":          "คำเชื่อมเชิงวรรณกรรม — ควรใช้ 'แต่' หรือ 'อย่างไรก็ตาม'",
    "ถึงแม้ว่า":     "คำเชื่อมภาษาพูด — ควรใช้ 'แม้ว่า' หรือ 'ถึงแม้'",
    "ยังไงก็ตาม":   "ภาษาพูด — ควรใช้ 'อย่างไรก็ตาม'",
}


# ══════════════════════════════════════════════
# Category D: Common Thai Misspellings → Corrections
# ══════════════════════════════════════════════

CATEGORY_D_MISSPELLINGS: dict[str, str] = {
    # ── คำผิดทั่วไป ──
    "อนุญาติ":         "อนุญาต",
    "สังเกตุ":          "สังเกต",
    "ปรากฎ":           "ปรากฏ",
    "กฏหมาย":          "กฎหมาย",
    "ผูกพันธ์":         "ผูกพัน",
    "ลายเซ็นต์":       "ลายเซ็น",
    "โอกาศ":           "โอกาส",
    # ── คำที่มักสะกดผิด ──
    "ศรีษะ":            "ศีรษะ",
    "ผลลัพท์":          "ผลลัพธ์",
    # ── ทับศัพท์ผิด ──
    "อีเมลล์":          "อีเมล",
    "เว็ปไซต์":         "เว็บไซต์",
    "เวปไซต์":          "เว็บไซต์",
    "ซอฟแวร์":          "ซอฟต์แวร์",
    # ── คำสับสน ──
    "กระเพรา":          "กะเพรา",
    "ประทะ":            "ปะทะ",
    "ไอศครีม":           "ไอศกรีม",
}


# ══════════════════════════════════════════════
# Main scanner function
# ══════════════════════════════════════════════

def scan_typos(doc: Document) -> list[HardRuleError]:
    """
    Scan all paragraphs for forbidden pronouns, informal words,
    overused transitions, and common misspellings.
    Returns HardRuleError list with paragraph locations.
    """
    errors = []
    seen: set[tuple[int, str]] = set()   # (para_index, word) — deduplicate

    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if not text or len(text) < 2:
            continue

        preview = text[:60] + ("..." if len(text) > 60 else "")

        # ── Category A: Pronouns ──
        for word, reason in CATEGORY_A_PRONOUNS.items():
            if word in text and (i, word) not in seen:
                seen.add((i, word))
                errors.append(HardRuleError(
                    location=f"Paragraph {i+1}",
                    issue=f"พบสรรพนามต้องห้าม: '{word}'",
                    detail=f"{reason} — \"{preview}\"",
                    severity="warning",
                    rule_type="typo_pronoun",
                ))

        # ── Category B: Informal/Slang/Filler ──
        for word, reason in CATEGORY_B_INFORMAL.items():
            if word in text and (i, word) not in seen:
                seen.add((i, word))
                errors.append(HardRuleError(
                    location=f"Paragraph {i+1}",
                    issue=f"พบคำไม่เป็นทางการ: '{word}'",
                    detail=f"{reason} — \"{preview}\"",
                    severity="warning",
                    rule_type="typo_informal",
                ))

        # ── Category C: Overused Transitions ──
        for word, reason in CATEGORY_C_TRANSITIONS.items():
            if word in text and (i, word) not in seen:
                seen.add((i, word))
                errors.append(HardRuleError(
                    location=f"Paragraph {i+1}",
                    issue=f"พบคำเชื่อมที่ควรระวัง: '{word}'",
                    detail=f"{reason} — \"{preview}\"",
                    severity="warning",
                    rule_type="typo_transition",
                ))

        # ── Category D: Misspellings ──
        for wrong, correct in CATEGORY_D_MISSPELLINGS.items():
            if wrong in text and (i, wrong) not in seen:
                seen.add((i, wrong))
                errors.append(HardRuleError(
                    location=f"Paragraph {i+1}",
                    issue=f"พบคำสะกดผิด: '{wrong}'",
                    detail=f"แนะนำแก้ไขเป็น: '{correct}' — \"{preview}\"",
                    severity="error",
                    rule_type="typo_spelling",
                ))

    return errors
