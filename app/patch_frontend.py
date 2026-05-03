import re
import os

app_js_path = r"d:\Ai_thesis\app\static\app.js"
style_css_path = r"d:\Ai_thesis\app\static\style.css"

with open(app_js_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add new utility functions
utils = """
function splitIntoChunks(text, chunkSize = 2000) {
    if (!text) return [""];
    const chunks = [];
    const paragraphs = text.split('\\n\\n');
    let current = '';
    for (const para of paragraphs) {
        if (current.length + para.length + 2 > chunkSize && current) {
            chunks.push(current.trim());
            current = para;
        } else {
            current = current ? (current + '\\n\\n' + para) : para;
        }
    }
    if (current.trim()) chunks.push(current.trim());
    return chunks.length ? chunks : [text.substring(0, chunkSize)];
}

function parseGeminiJSON(str) {
    try {
        let clean = str.replace(/```json/gi, '').replace(/```/g, '').trim();
        return JSON.parse(clean);
    } catch (e) {
        console.error("Failed to parse Gemini JSON:", str);
        return [];
    }
}

function buildTableHTML(items) {
    if (!items || items.length === 0) return '<div class="success-msg">✅ ไม่พบข้อผิดพลาดจาก AI Soft Rules</div>';
    let html = `<table class="ai-table">
        <thead>
            <tr>
                <th>ตำแหน่ง / หน้า</th>
                <th>รายละเอียดข้อผิดพลาด</th>
                <th>แนวทางแก้ไข</th>
            </tr>
        </thead>
        <tbody>`;
    for (let item of items) {
        html += `<tr>
            <td style="white-space:nowrap;">${escapeHtml(item.location || '')}</td>
            <td>${escapeHtml(item.issue || '')}</td>
            <td>${escapeHtml(item.fix || '')}</td>
        </tr>`;
    }
    html += `</tbody></table>`;
    return html;
}

function runCountdown(seconds, messageTemplate, statusEl) {
    return new Promise(resolve => {
        let count = seconds;
        statusEl.textContent = messageTemplate.replace('{X}', count);
        let timer = setInterval(() => {
            count--;
            if (count <= 0) {
                clearInterval(timer);
                resolve();
            } else {
                statusEl.textContent = messageTemplate.replace('{X}', count);
            }
        }, 1000);
    });
}
"""

content = content.replace("// ══════════════════════════════════════════════\n// Utilities", "// ══════════════════════════════════════════════\n// Utilities\n// ══════════════════════════════════════════════\n" + utils)

# 2. Update uploadSlot
old_uploadSlot_logic = """    chunkWrap.classList.remove('hidden');
    chunkStatus.textContent = 'กำลังวิเคราะห์อย่างละเอียด...';
    const progressTimer = startProgressAnimation(chunkFill, chunkStatus);

    const formData = new FormData();
    formData.append('file', input.files[0]);

    try {
        const res = await fetch(`${API_BASE}/api/slot/${n}?session_id=${SESSION_ID}`, {
            method: 'POST', body: formData,
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `HTTP ${res.status}`);
        }

        const data = await res.json();

        finishProgressAnimation(progressTimer, chunkFill, chunkStatus, data.total_chunks || 1, () => {
            chunkWrap.classList.add('hidden');
        });"""

new_uploadSlot_logic = """    chunkWrap.classList.remove('hidden');
    chunkFill.style.transition = 'width 0.3s ease';
    chunkFill.style.width = '0%';
    chunkStatus.textContent = 'กำลังแยกวิเคราะห์ไฟล์...';

    const formData = new FormData();
    formData.append('file', input.files[0]);

    try {
        const res = await fetch(`${API_BASE}/api/slot/${n}?session_id=${SESSION_ID}`, {
            method: 'POST', body: formData,
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `HTTP ${res.status}`);
        }

        const data = await res.json();
        const chunks = splitIntoChunks(data.full_text || "", 2000);
        let allJsonObjects = [];

        for (let i = 0; i < chunks.length; i++) {
            let chunk = chunks[i];
            let success = false;
            
            while (!success) {
                chunkStatus.textContent = `กำลังวิเคราะห์ส่วนที่ ${i + 1}/${chunks.length}...`;
                chunkFill.style.width = ((i / chunks.length) * 100) + '%';
                
                let aiRes = await fetch(`${API_BASE}/api/ai_chunk`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        chunk_text: chunk,
                        slot_number: n,
                        chapter: 0,
                        chunk_index: i + 1,
                        total_chunks: chunks.length
                    })
                });
                
                let aiData = await aiRes.json();
                
                if (!aiData.success) {
                    if (aiData.error === '429_QUOTA') {
                        await runCountdown(30, "⚠️ โควต้า AI ของ Google เต็มชั่วคราว! กำลังรอคูลดาวน์ระบบ... พยายามส่งใหม่ใน {X} วินาที", chunkStatus);
                        continue;
                    } else {
                        throw new Error(aiData.message);
                    }
                }
                
                let parsedArray = parseGeminiJSON(aiData.data);
                if (Array.isArray(parsedArray)) {
                    allJsonObjects.push(...parsedArray);
                }
                success = true;
                
                chunkFill.style.width = (((i+1) / chunks.length) * 100) + '%';
                
                if (i < chunks.length - 1) {
                    await runCountdown(15, "⏳ กำลังพักคูลดาวน์ AI เพื่อป้องกันโควต้าเต็ม... ส่งข้อมูลถัดไปใน {X} วินาที", chunkStatus);
                }
            }
        }
        
        chunkStatus.textContent = `✅ วิเคราะห์ครบ ${chunks.length} ส่วนแล้ว (100%)`;
        setTimeout(() => { chunkWrap.classList.add('hidden'); }, 1500);

        data.ai_soft_rules_feedback = buildTableHTML(allJsonObjects);
"""
content = content.replace(old_uploadSlot_logic, new_uploadSlot_logic)

# 3. Update uploadChapter
old_uploadChapter_logic = """    chunkWrap.classList.remove('hidden');
    chunkStatus.textContent = 'กำลังวิเคราะห์อย่างละเอียด...';
    const progressTimer = startProgressAnimation(chunkFill, chunkStatus);

    const formData = new FormData();
    formData.append('file', input.files[0]);

    try {
        const res = await fetch(`${API_BASE}/api/slot/4/${ch}?session_id=${SESSION_ID}`, {
            method: 'POST', body: formData,
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `HTTP ${res.status}`);
        }

        const data = await res.json();

        finishProgressAnimation(progressTimer, chunkFill, chunkStatus, data.total_chunks || 1, () => {
            chunkWrap.classList.add('hidden');
        });"""

new_uploadChapter_logic = """    chunkWrap.classList.remove('hidden');
    chunkFill.style.transition = 'width 0.3s ease';
    chunkFill.style.width = '0%';
    chunkStatus.textContent = 'กำลังแยกวิเคราะห์ไฟล์...';

    const formData = new FormData();
    formData.append('file', input.files[0]);

    try {
        const res = await fetch(`${API_BASE}/api/slot/4/${ch}?session_id=${SESSION_ID}`, {
            method: 'POST', body: formData,
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `HTTP ${res.status}`);
        }

        const data = await res.json();
        const chunks = splitIntoChunks(data.full_text || "", 2000);
        let allJsonObjects = [];

        for (let i = 0; i < chunks.length; i++) {
            let chunk = chunks[i];
            let success = false;
            
            while (!success) {
                chunkStatus.textContent = `กำลังวิเคราะห์ส่วนที่ ${i + 1}/${chunks.length}...`;
                chunkFill.style.width = ((i / chunks.length) * 100) + '%';
                
                let aiRes = await fetch(`${API_BASE}/api/ai_chunk`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        chunk_text: chunk,
                        slot_number: 4,
                        chapter: ch,
                        chunk_index: i + 1,
                        total_chunks: chunks.length
                    })
                });
                
                let aiData = await aiRes.json();
                
                if (!aiData.success) {
                    if (aiData.error === '429_QUOTA') {
                        await runCountdown(30, "⚠️ โควต้า AI ของ Google เต็มชั่วคราว! กำลังรอคูลดาวน์ระบบ... พยายามส่งใหม่ใน {X} วินาที", chunkStatus);
                        continue;
                    } else {
                        throw new Error(aiData.message);
                    }
                }
                
                let parsedArray = parseGeminiJSON(aiData.data);
                if (Array.isArray(parsedArray)) {
                    allJsonObjects.push(...parsedArray);
                }
                success = true;
                
                chunkFill.style.width = (((i+1) / chunks.length) * 100) + '%';
                
                if (i < chunks.length - 1) {
                    await runCountdown(15, "⏳ กำลังพักคูลดาวน์ AI เพื่อป้องกันโควต้าเต็ม... ส่งข้อมูลถัดไปใน {X} วินาที", chunkStatus);
                }
            }
        }
        
        chunkStatus.textContent = `✅ วิเคราะห์ครบ ${chunks.length} ส่วนแล้ว (100%)`;
        setTimeout(() => { chunkWrap.classList.add('hidden'); }, 1500);

        data.ai_soft_rules_feedback = buildTableHTML(allJsonObjects);
"""
content = content.replace(old_uploadChapter_logic, new_uploadChapter_logic)

# Remove progressTimer usages in catch blocks
content = content.replace("clearInterval(progressTimer);", "")

# 4. Do not escapeHtml for AI feedback
content = content.replace("<div>${escapeHtml(data.feedback)}</div>", "<div>${data.feedback}</div>")
content = content.replace('<div style="line-height:1.6; font-size:14px;">${escapeHtml(data.feedback)}</div>', '<div style="line-height:1.6; font-size:14px;">${data.feedback}</div>')

with open(app_js_path, "w", encoding="utf-8") as f:
    f.write(content)

with open(style_css_path, "a", encoding="utf-8") as f:
    f.write('''\n
/* ══════════════════════════════════════════════ */
/* AI Table Styles                                */
/* ══════════════════════════════════════════════ */
.ai-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
    font-size: 13px;
    color: var(--text);
}
.ai-table th {
    background: rgba(255, 255, 255, 0.05);
    color: var(--kku-gold);
    text-align: left;
    padding: 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.ai-table td {
    padding: 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    vertical-align: top;
}
.ai-table tr:hover {
    background: rgba(255, 255, 255, 0.02);
}
''')

print("Frontend patched successfully.")
