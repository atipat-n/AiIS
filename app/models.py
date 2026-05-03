"""
Pydantic models for KKU Thesis AI Checker Pro Version.
Defines data structures for API responses and session state.

v3 Architecture: JSON-only feedback (no Virtual Red Pen .docx generation).
"""

from pydantic import BaseModel
from typing import Optional


class HardRuleError(BaseModel):
    """A single hard-rule error with precise location information."""
    location: str       # e.g. "Page 1, Paragraph 3" or "Section 1"
    issue: str          # Short label e.g. "Wrong Margin", "Wrong Font"
    detail: str         # Full detail e.g. "Found Top Margin 1.0 inch. Expected 1.5 inch."
    severity: str = "error"  # "error" or "warning"
    rule_type: str = ""      # "margin", "font", "logo", "title_size"


class SlotResult(BaseModel):
    """Result of checking a single upload slot — v3 JSON-structured feedback."""
    slot_number: int
    slot_name: str
    status: str                          # "passed" | "issues_found"
    hard_rules_errors: list[HardRuleError] = []
    ai_soft_rules_feedback: Optional[str] = None
    error_count: int = 0
    warning_count: int = 0
    full_text: str = ""


class CrossCheckResult(BaseModel):
    """Citation cross-check result between Slot 4 and Slot 5."""
    cited_but_not_referenced: list[str] = []
    referenced_but_not_cited: list[str] = []
    matched: list[str] = []
    total_in_text: int = 0
    total_in_references: int = 0
    is_complete: bool = False  # True only when both Slot 4 and 5 are uploaded


class SessionData:
    """
    In-memory session holding all slot results and citation data.
    Keyed by a UUID session_id generated on first upload.
    """

    def __init__(self):
        self.slot_results: dict = {}  # keys: int (1,2,3,5) or str ("4.1"-"4.5")
        self.in_text_citations: set[str] = set()
        self.reference_authors: set[str] = set()
        self.chapter_citations: dict[int, set[str]] = {}  # per-chapter citations
        self.cross_check: Optional[CrossCheckResult] = None
        # TOC matching state
        self.toc_headings: list[str] = []                    # extracted from Slot 3
        self.content_headings: dict[int, list[str]] = {}     # per-chapter headings from Slot 4
