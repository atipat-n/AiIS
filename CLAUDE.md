# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**MBA IS AI Checker Pro** is an intelligent thesis formatting verification system for Khon Kaen University's MBA Independent Study (IS) program. It validates 5 document slots against strict formatting rules (Hard Rules) and performs contextual content analysis using Google Gemini AI.

**Key Features:**
- Dual-layer validation: structural hard rules (margins, fonts, sequences) + AI soft rules (contextual, academic tone)
- 5-slot upload system: Front Matter, Abstract, TOC, Main Content (5 chapters), References
- Background task processing with polling architecture to handle long-running operations
- Bilingual i18n system (Thai/English) with dark/light theme support
- Citation cross-check between in-text citations (Slot 4) and reference list (Slot 5)

## Technology Stack

**Backend:**
- FastAPI 0.115.0 (REST API framework)
- Python 3.x with `python-docx` for .docx parsing
- Google Generative AI (Gemini 1.5 Flash / 3.1 Flash Lite) for AI analysis
- `python-dotenv` for environment configuration
- Uvicorn for ASGI server

**Frontend:**
- Vanilla HTML/CSS/JavaScript (no build step)
- Kanit font (Thai typography)
- CSS Variables for dark/light theming
- Custom i18n system via data attributes + JS dictionary

## Directory Structure

```
D:\Ai_thesis\
├── app/
│   ├── main.py                      # FastAPI server, 5-slot + chapter endpoints
│   ├── models.py                    # Pydantic models (HardRuleError, SlotResult, etc.)
│   ├── document_processor.py        # Hard rules: margins, fonts, title checks, logo
│   ├── ai_service.py                # Gemini integration, chunking, prompt templates
│   ├── citation_engine.py           # Citation extraction & cross-check logic
│   ├── sequence_checker.py          # Table/figure sequence validation
│   ├── typo_scanner.py              # Dictionary-based Thai typo/slang detection
│   ├── requirements.txt             # Python dependencies
│   ├── .env                         # (NOT in git) GEMINI_API_KEY
│   └── static/
│       ├── index.html               # UI markup (3-column layout)
│       ├── app.js                   # Client-side state, polling, drag-drop
│       ├── style.css                # CSS variables, responsive grid, themes
│       ├── i18n.js                  # Thai/English translations dictionary
│       └── assets/
│           └── mba_kku_logo.png
├── agent.md                         # High-level architecture & rules (predecessor to CLAUDE.md)
├── .gitignore                       # Excludes .env, venv, cache
└── [test files]
```

## Running the Application

### Setup

```bash
# Create virtual environment
python -m venv app\.venv
app\.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r app/requirements.txt

# Create .env file with API key (required!)
echo GEMINI_API_KEY=your_key_here > app\.env
```

### Start the Server

```bash
# Development with auto-reload
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

Access the UI at `http://localhost:8000`

### Run Tests

Test files exist but are minimal. To test functionality:

```bash
# Test polling mechanism
python app/test_polling.py

# Test slot processing
python app/test_all_slots.py
```

## Architecture Patterns

### 1. Background Task Processing (Async Without Blocking)

All document analysis operations are **asynchronous and non-blocking**:

- **Upload Endpoint** (`POST /api/slot/{slot_number}`):
  - Receives file, generates UUID `task_id`
  - Immediately returns `{"status": "processing", "task_id": "..."}`
  - Spawns `BackgroundTasks` worker thread

- **Status Endpoint** (`GET /api/status/{task_id}`):
  - Frontend polls every 2 seconds
  - Returns `{"status": "processing", "result": null}` while running
  - Returns `{"status": "completed", "result": {...}}` when done

- **Backend Worker** (`process_slot_background`, `process_chapter_background`):
  - 5-second delay before processing (allows browser disconnect handling)
  - Runs hard rules + AI analysis in sequence
  - Stores result in `background_tasks_store[task_id]`

**Why?** Long document analysis + Gemini API calls can timeout browser connections. This pattern ensures stability.

### 2. Hard Rules vs. Soft Rules (Two-Layer Validation)

**Hard Rules** (deterministic, physical properties):
- Margins: `SLOT_MARGINS` dict with ±0.15" tolerance
- Fonts: Only `{TH Sarabun New, TH SarabunPSK, TH Sarabun PSK}`
- Title formatting: 18pt, Bold, Centered
- Table/Figure sequence numbering (Chapter.Sequence format)
- Required keywords (Front Matter only)
- Typos: Dictionary-based scanning (4 categories in `typo_scanner.py`)

Checked in **`document_processor.py`** → returns `list[HardRuleError]` (deterministic)

**Soft Rules** (contextual, AI-driven):
- Academic tone (vs. spoken language, pronouns)
- Structural completeness (Abstract has objectives, methodology, results, conclusion)
- Citation density & formatting (APA 7th Edition)
- Content coherence per chapter

Checked in **`ai_service.py`** → Gemini analyzes chunked text, returns JSON array

### 3. Chunking & Iterative Extraction

Document text is split into 2000-char chunks to handle API limits:

```python
chunks = split_into_chunks(full_text, 2000)
for chunk in chunks:
    result_json_str = call_kku_llm(prompt, chunk, slot_number, chapter)
    parsed = parse_gemini_json(result_json_str)
    all_json_objects.extend(parsed)
```

Each chunk is analyzed independently, results aggregated. This handles large documents and recovers gracefully from partial failures.

### 4. Session Management (In-Memory)

Session state is stored in `sessions: dict[str, SessionData]`:

- Key: UUID `session_id` (generated client-side via `crypto.randomUUID()`)
- Value: `SessionData` object holding:
  - `slot_results`: Dictionary of upload results per slot
  - `in_text_citations`: Set of author names cited in Slot 4
  - `reference_authors`: Set of authors in Slot 5 reference list
  - `cross_check`: `CrossCheckResult` (cited but not referenced, vice versa)
  - `toc_headings` / `content_headings`: For TOC matching

**Limitation:** Sessions are lost on server restart. For production, replace with Redis or database.

### 5. Citation Cross-Check Engine

**Flow:**
1. Upload Slot 4 (Main Content) → Extract citations via regex: `(Author, YYYY)` patterns
2. Upload Slot 5 (References) → Extract author surnames via regex
3. Compare sets:
   - `cited_but_not_referenced`: In Slot 4 but missing from Slot 5
   - `referenced_but_not_cited`: In Slot 5 but not cited in Slot 4
   - `matched`: Present in both

**Key:** Uses regex for Thai (`ก-๏฀-๿`) + English author extraction, case-insensitive normalization.

### 6. Frontend Architecture (Vanilla JS, No Build Step)

**3-Column Layout:**
1. **Left Panel:** Instructions (how to use system)
2. **Middle Panel:** 5-slot upload UI + progress dots
3. **Right Panel:** AI Analysis summary + citation cross-check

**State Management:**
- Global `slotState` / `chapterState` objects track upload status per slot
- `allErrors` array collects all errors for full checklist modal
- No Redux/Vuex — direct DOM manipulation via `document.getElementById()`

**Polling Loop** (`uploadSlot(n)` → `pollTaskStatus(taskId)`):
```javascript
// Poll every 2 seconds until status === "completed" or "error"
const interval = setInterval(() => {
  fetch(`/api/status/${taskId}`).then(r => r.json()).then(data => {
    if (data.status === "completed") {
      clearInterval(interval);
      displayResults(data.result);
    }
  });
}, 2000);
```

### 7. i18n System (Thai/English Toggling)

**No build step needed:**
- `i18n.js` contains translations dictionary: `translations = { th: {...}, en: {...} }`
- HTML uses `data-i18n="header.title"` attributes
- JavaScript toggle button calls `switchLanguage("en")` or `switchLanguage("th")`
- `applyTranslations()` walks DOM, finds attributes, replaces `innerHTML`

**Adding new translations:** Edit `i18n.js`, add key to both `th` and `en` objects, use `data-i18n="key"` in HTML.

### 8. Theme System (Dark/Light Mode)

CSS Variables approach:
- `:root` defines light mode colors: `--bg-primary`, `--text-main`, `--accent`, etc.
- `body.dark-mode` overrides with dark palette
- Toggle button adds/removes `dark-mode` class, persists to `localStorage`

**Custom Accent:** MBA official color is `#e0633b` (orange-red).

## Key Files & Their Responsibilities

| File | Purpose |
|------|---------|
| `main.py` | FastAPI server, session mgmt, endpoints, background task dispatch |
| `models.py` | Pydantic schemas: HardRuleError, SlotResult, CrossCheckResult, SessionData |
| `document_processor.py` | Hard rules: margins, fonts, titles, keywords, text extraction |
| `ai_service.py` | Gemini API wrapper, chunking, slot/chapter-specific prompts |
| `citation_engine.py` | Citation regex extraction, author normalization, cross-check logic |
| `sequence_checker.py` | Table/Figure sequence validation per chapter |
| `typo_scanner.py` | Dictionary-based Thai slang/typo detection (4 categories) |
| `app.js` | Client state, polling, file handling, result display |
| `style.css` | CSS variables, 3-column grid, responsive design |
| `i18n.js` | Translation dictionary + language switching logic |

## Important Rules & Constraints

### Backend Rules
- **API Keys:** Always load from `.env` via `dotenv.load_dotenv()`. Never hardcode.
- **Temperature:** Gemini calls use `temperature=0.0` for deterministic outputs (set in prompts).
- **Chunking:** Always split large documents to avoid API limits. 2000 chars is safe.
- **No Blocking:** All heavy operations must use `BackgroundTasks`. Synchronous calls will timeout.

### Frontend Rules
- **Grid Layout:** 3-column responsive layout must be preserved. Use CSS Grid, not Flexbox for main sections.
- **CSS Variables:** All colors use custom properties. Dark/Light toggle must work via `:root` and `body.dark-mode`.
- **i18n:** All UI text must have `data-i18n` attributes. Add translations to both `th` and `en` in `i18n.js`.
- **No Build Step:** Avoid imports/exports, build tools, module bundlers. Keep it vanilla.
- **Drag & Drop:** File upload areas support both click and drag-drop. Validate file type (`.docx` only).

### Formatting Standards
- **Margins:** Slot 1 has 2.5" top, others 1.5". Tolerance ±0.15".
- **Fonts:** Only Thai Sarabun (3 variants allowed, case-sensitive).
- **Titles:** 18pt, Bold, Centered.
- **Table/Figure Numbering:** Format `ตารางที่ 1.1` or `ภาพที่ 1.1` (Chapter.Sequence).
- **Citations:** APA 7th Edition, both Thai & English formats supported.

## Adding New Features

### New Hard Rule
1. Add validation function to `document_processor.py`
2. Call it from `process_slot()` function
3. Return `list[HardRuleError]` with location, issue, detail, severity

### New AI Analysis
1. Add slot/chapter-specific prompt to `SLOT_PROMPTS` or `CHAPTER_PROMPTS` in `ai_service.py`
2. Update prompt to instruct Gemini to return JSON array: `[{"location": "...", "issue": "...", "fix": "..."}]`
3. Call `call_kku_llm()` in background worker, parse JSON via `parse_gemini_json()`

### New Frontend Panel
1. Add HTML to `index.html` with `data-i18n` attributes
2. Add translations to both `th` and `en` in `i18n.js`
3. Add CSS to `style.css` (use CSS variables for colors)
4. Wire up JavaScript event listeners in `app.js`

## Debugging Tips

**"GEMINI_API_KEY not found"**
- Create `app/.env` with `GEMINI_API_KEY=your_actual_key`

**Frontend shows "⏳ Processing" forever**
- Check browser console for polling errors
- Verify `/api/status/{taskId}` endpoint returns valid JSON
- Check if backend worker is actually running (look for print statements)

**Citation cross-check shows wrong counts**
- Regex patterns may not match all author name formats
- Edit `EN_CITATION_PATTERN`, `TH_CITATION_PATTERN` in `citation_engine.py`
- Test with `extract_in_text_citations()` and `extract_reference_authors()` directly

**Hard rule checks miss errors**
- Verify tolerance values (`MARGIN_TOLERANCE`, font name matching is case-sensitive)
- Add debug print to understand which checks are running

## Git Workflow

Recent commits show incremental feature additions (theme toggle, i18n, sequence checker, queue architecture). Follow this pattern:

- Keep commits focused on one feature/fix
- Prefix: `feat:` (new feature), `fix:` (bug fix), `refactor:` (code improvement)
- Always exclude `.env`, `venv/`, `__pycache__/` via `.gitignore`
