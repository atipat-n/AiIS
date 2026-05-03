"""
Citation Cross-Check Engine — citation_engine.py
Extracts in-text citations from Slot 4 and reference authors from Slot 5,
then compares them to find mismatches.
"""

import re
from models import CrossCheckResult


# ──────────────────────────────────────────────
# Regex patterns
# ──────────────────────────────────────────────

EN_CITATION_PATTERN = re.compile(
    r'\(\s*([A-Za-z][A-Za-z\s&,\.]+?)\s*,\s*(\d{4})\s*\)', re.UNICODE
)
TH_CITATION_PATTERN = re.compile(
    r'\(\s*([ก-๏\u0E00-\u0E7F][ก-๏\u0E00-\u0E7F\s]+?)\s*,\s*(\d{4})\s*\)', re.UNICODE
)
EN_REF_PATTERN = re.compile(
    r'^([A-Za-z][A-Za-z\-\']+(?:\s*,\s*[A-Za-z\.\s]+)?)', re.MULTILINE | re.UNICODE
)
TH_REF_PATTERN = re.compile(
    r'^([ก-๏\u0E00-\u0E7F][ก-๏\u0E00-\u0E7F\s]+?)(?:\s*[\.\(])', re.MULTILINE | re.UNICODE
)


def _normalize(name: str) -> str:
    name = re.sub(r'\s+', ' ', name.strip()).rstrip('.,').lower()
    return name


def _split_authors(s: str) -> list[str]:
    parts = re.split(r'\s*[&]\s*|\s+and\s+|\s*,\s*', s)
    return [p.strip() for p in parts if p.strip() and len(p.strip()) > 1]


def extract_in_text_citations(text: str) -> set[str]:
    """Extract in-text citation authors from Slot 4 content."""
    authors = set()
    for match in EN_CITATION_PATTERN.finditer(text):
        for name in _split_authors(match.group(1)):
            n = _normalize(name)
            if n:
                authors.add(n)
    for match in TH_CITATION_PATTERN.finditer(text):
        n = _normalize(match.group(1))
        if n:
            authors.add(n)
    return authors


def extract_reference_authors(text: str) -> set[str]:
    """Extract author names from Slot 5 references."""
    authors = set()
    for match in EN_REF_PATTERN.finditer(text):
        surname = match.group(1).split(",")[0].strip()
        n = _normalize(surname)
        if n and len(n) > 1:
            authors.add(n)
    for match in TH_REF_PATTERN.finditer(text):
        n = _normalize(match.group(1))
        if n and len(n) > 1:
            authors.add(n)
    return authors


def cross_check(in_text: set[str], refs: set[str]) -> CrossCheckResult:
    """Compare in-text citations against reference list."""
    return CrossCheckResult(
        cited_but_not_referenced=sorted(in_text - refs),
        referenced_but_not_cited=sorted(refs - in_text),
        matched=sorted(in_text & refs),
        total_in_text=len(in_text),
        total_in_references=len(refs),
        is_complete=True,
    )
