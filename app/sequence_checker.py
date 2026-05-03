import re
from docx import Document
from models import HardRuleError

TABLE_PATTERN = re.compile(r'^(?:ตารางที่|Table)\s*(\d+)\.(\d+)')
FIGURE_PATTERN = re.compile(r'^(?:ภาพที่|รูปที่|Figure)\s*(\d+)\.(\d+)')

def check_table_figure_sequences(doc: Document, chapter: int) -> list[HardRuleError]:
    """
    Checks the sequence numbering of Tables and Figures within a chapter.
    Expects format like "ตารางที่ 1.1" or "ภาพที่ 1.1".
    """
    errors = []
    
    expected_table_seq = 1
    expected_figure_seq = 1
    
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if not text:
            continue
            
        # Check Table
        match_table = TABLE_PATTERN.search(text)
        if match_table:
            found_chapter = int(match_table.group(1))
            found_seq = int(match_table.group(2))
            
            if found_chapter != chapter:
                errors.append(HardRuleError(
                    location=f"Paragraph {i+1}",
                    issue="เลขบทของตารางผิด (Wrong Chapter in Table)",
                    detail=f"พบ '{match_table.group(0)}' ในเอกสารบทที่ {chapter}",
                    severity="error",
                    rule_type="sequence",
                ))
            
            if found_seq != expected_table_seq:
                errors.append(HardRuleError(
                    location=f"Paragraph {i+1}",
                    issue="ลำดับตารางข้ามหรือไม่ต่อเนื่อง (Table Sequence Mismatch)",
                    detail=f"พบ '{match_table.group(0)}' แต่ลำดับที่ควรจะเป็นคือ {found_chapter}.{expected_table_seq}",
                    severity="error",
                    rule_type="sequence",
                ))
                # Sync expected to avoid cascading errors
                expected_table_seq = found_seq + 1
            else:
                expected_table_seq += 1
                
        # Check Figure
        match_figure = FIGURE_PATTERN.search(text)
        if match_figure:
            found_chapter = int(match_figure.group(1))
            found_seq = int(match_figure.group(2))
            
            if found_chapter != chapter:
                errors.append(HardRuleError(
                    location=f"Paragraph {i+1}",
                    issue="เลขบทของภาพผิด (Wrong Chapter in Figure)",
                    detail=f"พบ '{match_figure.group(0)}' ในเอกสารบทที่ {chapter}",
                    severity="error",
                    rule_type="sequence",
                ))
            
            if found_seq != expected_figure_seq:
                errors.append(HardRuleError(
                    location=f"Paragraph {i+1}",
                    issue="ลำดับภาพข้ามหรือไม่ต่อเนื่อง (Figure Sequence Mismatch)",
                    detail=f"พบ '{match_figure.group(0)}' แต่ลำดับที่ควรจะเป็นคือ {found_chapter}.{expected_figure_seq}",
                    severity="error",
                    rule_type="sequence",
                ))
                expected_figure_seq = found_seq + 1
            else:
                expected_figure_seq += 1
                
    return errors
