### 1. Project Context
- **Name:** MBA KKU IS AI Checker Pro
- **Goal:** An automated system to verify 5 specific slots of MBA Independent Study (IS) documents against strict KKU formatting rules (Hard Rules) and contextual accuracy (using Gemini 1.5 Pro).

### 2. Tech Stack
- **Backend:** Python (with packages like `python-docx`, `python-dotenv`, `google-generativeai`).
- **Frontend:** Pure Vanilla HTML, CSS, and JavaScript (No build steps or heavy JS frameworks).

### 3. Architecture & Styling Rules
- **UI/UX:** 3-column responsive layout.
- **Styling:** CSS Variables for persistent Dark/Light mode toggle. Official MBA accent color is `#e0633b`. Global font is 'Kanit'.
- **Localization:** Custom Vanilla JS `i18n` system (data attributes + JS dictionary) for TH/EN toggling.
- **Rule:** Future frontend changes MUST respect the existing grid layout, CSS variables, and i18n structure.

### 4. Backend & AI Rules
- **Security:** API keys MUST be read from the `.env` file. Never hardcode keys.
- **AI Constraints:** Set Gemini API `temperature: 0.0` for deterministic outputs. AI evaluates content/context; `python-docx` handles physical measurements (margins, fonts).
- **Rule:** Default to "Additive Changes" rather than destructive refactoring.

### 5. Queue & Polling Architecture (Async Processing)
- **Task Management:** Heavy docx and AI processing operations must run completely in the background to avoid browser connection timeouts. 
- **Backend Flow:** Upload endpoints (`/api/slot/{n}`) generate a UUID (`task_id`), immediately spawn a FastAPI `BackgroundTasks` thread, and return `{"status": "processing", "task_id": "..."}`.
- **Frontend Flow:** The `app.js` UI switches to a loading state and aggressively polls the `/api/status/{task_id}` endpoint every 2 seconds. The polling loop only breaks when the backend returns a status of `completed` (delivering the full `result` JSON) or `error`.
- **Rule:** Do not revert to synchronous requests for document analysis. All long-running operations must comply with this polling pattern.
