/**
 * KKU Thesis AI Checker Pro v4 — Frontend Logic
 * Chunking & Iterative Extraction architecture with live progress bar.
 */

// ══════════════════════════════════════════════
// Configuration
// ══════════════════════════════════════════════

const API_BASE = window.location.origin;
const SESSION_ID = crypto.randomUUID ? crypto.randomUUID() : generateUUID();

// State
const slotState = {
    1: { uploaded: false, status: null, errors: 0, warnings: 0, name: 'ส่วนหน้า' },
    2: { uploaded: false, status: null, errors: 0, warnings: 0, name: 'บทคัดย่อ' },
    3: { uploaded: false, status: null, errors: 0, warnings: 0, name: 'สารบัญ' },
    5: { uploaded: false, status: null, errors: 0, warnings: 0, name: 'บรรณานุกรม' },
};

const chapterState = {
    1: { uploaded: false, status: null, errors: 0, warnings: 0 },
    2: { uploaded: false, status: null, errors: 0, warnings: 0 },
    3: { uploaded: false, status: null, errors: 0, warnings: 0 },
    4: { uploaded: false, status: null, errors: 0, warnings: 0 },
    5: { uploaded: false, status: null, errors: 0, warnings: 0 },
};

// All errors collected across all scans — for the right panel
let allErrors = [];

const BTN_LABELS = {
    1: '🔍 สแกนส่วนหน้า',
    2: '🔍 สแกนบทคัดย่อ',
    3: '🔍 สแกนสารบัญ',
    5: '🔍 สแกนบรรณานุกรม',
};

const CH_BTN_LABELS = {
    1: '🔍 สแกนบทที่ 1',
    2: '🔍 สแกนบทที่ 2',
    3: '🔍 สแกนบทที่ 3',
    4: '🔍 สแกนบทที่ 4',
    5: '🔍 สแกนบทที่ 5',
};


// ══════════════════════════════════════════════
// Initialization
// ══════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('session-display').textContent = SESSION_ID.substring(0, 12) + '...';

    for (const i of [1, 2, 3, 5]) {
        setupDragDrop(`upload-area-${i}`, `file-${i}`, () => onFileSelect(i));
    }
    for (let ch = 1; ch <= 5; ch++) {
        setupDragDrop(`upload-area-4-${ch}`, `file-4-${ch}`, () => onChapterFileSelect(ch));
    }
    toggleSlot(1);
});

function setupDragDrop(areaId, inputId, callback) {
    const area = document.getElementById(areaId);
    if (!area) return;
    area.addEventListener('dragover', (e) => { e.preventDefault(); area.classList.add('dragover'); });
    area.addEventListener('dragleave', () => { area.classList.remove('dragover'); });
    area.addEventListener('drop', (e) => {
        e.preventDefault();
        area.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file && file.name.endsWith('.docx')) {
            const input = document.getElementById(inputId);
            const dt = new DataTransfer();
            dt.items.add(file);
            input.files = dt.files;
            callback();
        } else {
            alert('⚠️ กรุณาอัปโหลดเฉพาะไฟล์ .docx');
        }
    });
}

function closeDisclaimer() {
    const overlay = document.getElementById('disclaimer-overlay');
    overlay.classList.add('closing');
    setTimeout(() => {
        overlay.classList.add('hidden');
        overlay.classList.remove('closing');
    }, 280);
}


// ══════════════════════════════════════════════
// Accordion toggles
// ══════════════════════════════════════════════

function toggleSlot(n) {
    const item = document.getElementById(`slot-item-${n}`);
    const isOpen = item.classList.contains('open');
    document.querySelectorAll('.slot-item').forEach(el => el.classList.remove('open', 'active'));
    if (!isOpen) item.classList.add('open', 'active');
}

function toggleSubSlot(ch) {
    const subSlot = document.getElementById(`sub-slot-4-${ch}`);
    const isOpen = subSlot.classList.contains('open');
    document.querySelectorAll('.sub-slot').forEach(el => el.classList.remove('open'));
    if (!isOpen) subSlot.classList.add('open');
}


// ══════════════════════════════════════════════
// File selection
// ══════════════════════════════════════════════

function onFileSelect(n) {
    const input = document.getElementById(`file-${n}`);
    const nameEl = document.getElementById(`fname-${n}`);
    const btn = document.getElementById(`btn-${n}`);
    if (input.files.length > 0) {
        nameEl.textContent = '📎 ' + input.files[0].name;
        btn.disabled = false;
    } else {
        nameEl.textContent = '';
        btn.disabled = true;
    }
}

function onChapterFileSelect(ch) {
    const input = document.getElementById(`file-4-${ch}`);
    const nameEl = document.getElementById(`fname-4-${ch}`);
    const btn = document.getElementById(`btn-4-${ch}`);
    if (input.files.length > 0) {
        nameEl.textContent = '📎 ' + input.files[0].name;
        btn.disabled = false;
    } else {
        nameEl.textContent = '';
        btn.disabled = true;
    }
}


// ══════════════════════════════════════════════
// Progress bar helpers
// ══════════════════════════════════════════════

function startProgressAnimation(fillEl, statusEl) {
    let pct = 0;
    fillEl.style.transition = 'width 0.6s ease';
    fillEl.style.width = '0%';
    return setInterval(() => {
        if (pct < 88) {
            pct += Math.random() * 3 + 1;
            if (pct > 88) pct = 88;
            fillEl.style.width = pct.toFixed(1) + '%';
            const part = Math.ceil((pct / 88) * 3);
            statusEl.textContent = `กำลังสแกนส่วนที่ ${part}... (${Math.round(pct)}%)`;
        }
    }, 600);
}

function finishProgressAnimation(timer, fillEl, statusEl, totalChunks, onDone) {
    clearInterval(timer);
    fillEl.style.transition = 'width 0.5s ease';
    fillEl.style.width = '100%';
    statusEl.textContent = `✅ วิเคราะห์ครบ ${totalChunks} ส่วนแล้ว (100%)`;
    setTimeout(() => { if (onDone) onDone(); }, 1500);
}


// ══════════════════════════════════════════════
// Upload main slot (1, 2, 3, 5)
// ══════════════════════════════════════════════

async function uploadSlot(n) {
    const input = document.getElementById(`file-${n}`);
    const btn = document.getElementById(`btn-${n}`);
    const btnText = btn.querySelector('.btn-text');
    const statusEl = document.getElementById(`status-${n}`);
    const resultEl = document.getElementById(`result-${n}`);
    const progEl = document.getElementById(`prog-${n}`);
    const chunkWrap = document.getElementById(`chunk-prog-${n}`);
    const chunkFill = document.getElementById(`chunk-fill-${n}`);
    const chunkStatus = document.getElementById(`chunk-status-${n}`);

    if (!input.files[0]) return;

    btn.classList.add('loading');
    btn.disabled = true;
    btnText.textContent = '🔍 กำลังวิเคราะห์อย่างละเอียด (ห้ามปิดหน้าต่าง)...';
    statusEl.className = 'slot-status status-scanning';
    statusEl.textContent = '⏳ กำลังสแกน...';
    progEl.className = 'progress-dot scanning';
    resultEl.innerHTML = '';

    chunkWrap.classList.remove('hidden');
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
                let basePct = (i / chunks.length) * 100;
                let contrib = (1 / chunks.length) * 100;
                
                chunkStatus.textContent = `กำลังวิเคราะห์ส่วนที่ ${i + 1}/${chunks.length}...`;
                chunkFill.style.width = basePct + '%';
                
                let currentProg = 0;
                let progTimer = setInterval(() => {
                    if (currentProg < 0.85) {
                        currentProg += Math.random() * 0.05 + 0.02;
                        if (currentProg > 0.85) currentProg = 0.85;
                        chunkFill.style.width = (basePct + (currentProg * contrib)) + '%';
                    }
                }, 500);
                
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
                
                clearInterval(progTimer);
                
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
                
                chunkFill.style.width = (basePct + contrib) + '%';
                
                if (i < chunks.length - 1) {
                    await runCountdown(15, "⏳ กำลังพักคูลดาวน์ AI เพื่อป้องกันโควต้าเต็ม... ส่งข้อมูลถัดไปใน {X} วินาที", chunkStatus);
                }
            }
        }
        
        chunkFill.style.width = '100%';
        chunkStatus.textContent = `✅ วิเคราะห์ครบ ${chunks.length} ส่วนแล้ว (100%)`;
        setTimeout(() => { chunkWrap.classList.add('hidden'); }, 1500);

        // Sync AI Errors to Slot Badges (Ghost Errors fix)
        let totalErrors = data.error_count + allJsonObjects.length;
        data.status = (totalErrors === 0 && data.warning_count === 0) ? 'passed' : 'issues_found';
        data.error_count = totalErrors;

        slotState[n] = {
            uploaded: true,
            status: data.status,
            errors: totalErrors,
            warnings: data.warning_count,
            name: data.slot_name,
        };

        if (totalErrors === 0 && data.warning_count === 0) {
            statusEl.className = 'slot-status status-passed';
            statusEl.textContent = '✅ ผ่าน';
            progEl.className = 'progress-dot done';
        } else {
            statusEl.className = 'slot-status status-failed';
            statusEl.textContent = `❌ ${totalErrors} errors, ${data.warning_count} warnings`;
            progEl.className = 'progress-dot error';
        }

        const sourceKey = `slot-${n}`;
        const sourceName = `Slot ${n}: ${data.slot_name}`;
        resultEl.innerHTML = renderSlotResult(data, sourceKey, sourceName);
        collectErrors(sourceName, data.hard_rules_errors);
        if (data.cross_check) renderCrossCheck(data.cross_check);
        
        // Pass the raw AI JSON array to the summary
        updateAISummary(`slot-${n}`, data.slot_name, allJsonObjects, totalErrors);

    } catch (err) {
        
        chunkWrap.classList.add('hidden');
        statusEl.className = 'slot-status status-failed';
        statusEl.textContent = '❌ ผิดพลาด';
        progEl.className = 'progress-dot error';
        resultEl.innerHTML = renderApiError(err.message);
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
        btnText.textContent = BTN_LABELS[n] || '🔍 สแกน';
    }
}


// ══════════════════════════════════════════════
// Upload chapter sub-slot (Slot 4, Chapters 1-5)
// ══════════════════════════════════════════════

async function uploadChapter(ch) {
    const input = document.getElementById(`file-4-${ch}`);
    const btn = document.getElementById(`btn-4-${ch}`);
    const btnText = btn.querySelector('.btn-text');
    const statusEl = document.getElementById(`status-4-${ch}`);
    const resultEl = document.getElementById(`result-4-${ch}`);
    const chProgEl = document.getElementById(`ch-prog-${ch}`);
    const mainStatusEl = document.getElementById('status-4');
    const mainProgEl = document.getElementById('prog-4');
    const chunkWrap = document.getElementById(`chunk-prog-4-${ch}`);
    const chunkFill = document.getElementById(`chunk-fill-4-${ch}`);
    const chunkStatus = document.getElementById(`chunk-status-4-${ch}`);

    if (!input.files[0]) return;

    btn.classList.add('loading');
    btn.disabled = true;
    btnText.textContent = '🔍 กำลังวิเคราะห์อย่างละเอียด (ห้ามปิดหน้าต่าง)...';
    statusEl.className = 'slot-status status-scanning';
    statusEl.textContent = '⏳';
    chProgEl.className = 'chapter-dot scanning';
    resultEl.innerHTML = '';

    chunkWrap.classList.remove('hidden');
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
                let basePct = (i / chunks.length) * 100;
                let contrib = (1 / chunks.length) * 100;
                
                chunkStatus.textContent = `กำลังวิเคราะห์ส่วนที่ ${i + 1}/${chunks.length}...`;
                chunkFill.style.width = basePct + '%';
                
                let currentProg = 0;
                let progTimer = setInterval(() => {
                    if (currentProg < 0.85) {
                        currentProg += Math.random() * 0.05 + 0.02;
                        if (currentProg > 0.85) currentProg = 0.85;
                        chunkFill.style.width = (basePct + (currentProg * contrib)) + '%';
                    }
                }, 500);
                
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
                
                clearInterval(progTimer);
                
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
                
                chunkFill.style.width = (basePct + contrib) + '%';
                
                if (i < chunks.length - 1) {
                    await runCountdown(15, "⏳ กำลังพักคูลดาวน์ AI เพื่อป้องกันโควต้าเต็ม... ส่งข้อมูลถัดไปใน {X} วินาที", chunkStatus);
                }
            }
        }
        
        chunkFill.style.width = '100%';
        chunkStatus.textContent = `✅ วิเคราะห์ครบ ${chunks.length} ส่วนแล้ว (100%)`;
        setTimeout(() => { chunkWrap.classList.add('hidden'); }, 1500);

        // Sync AI Errors to Slot Badges (Ghost Errors fix)
        let totalErrors = data.error_count + allJsonObjects.length;
        data.status = (totalErrors === 0 && data.warning_count === 0) ? 'passed' : 'issues_found';
        data.error_count = totalErrors;

        chapterState[ch] = {
            uploaded: true,
            status: data.status,
            errors: totalErrors,
            warnings: data.warning_count,
        };

        if (totalErrors === 0 && data.warning_count === 0) {
            statusEl.className = 'slot-status status-passed';
            statusEl.textContent = '✅';
            chProgEl.className = 'chapter-dot done';
        } else {
            statusEl.className = 'slot-status status-failed';
            statusEl.textContent = `❌ ${totalErrors}`;
            chProgEl.className = 'chapter-dot error';
        }

        const sourceKey = `ch-${ch}`;
        const chNames = { 1: 'บทที่ 1', 2: 'บทที่ 2', 3: 'บทที่ 3', 4: 'บทที่ 4', 5: 'บทที่ 5' };
        const sourceName = `Slot 4.${ch}: ${chNames[ch]}`;
        let resultHtml = renderSlotResult(data, sourceKey, sourceName);
        if (data.citations_found !== undefined) {
            resultHtml += `<div class="ai-feedback" style="margin-top:8px;">
                <div class="ai-feedback-label">🔗 Citations Found</div>
                <div>พบการอ้างอิงในบทนี้: ${data.citations_found} | รวมทั้งหมด: ${data.total_citations}</div>
            </div>`;
        }
        resultEl.innerHTML = resultHtml;

        collectErrors(sourceName, data.hard_rules_errors);

        updateSlot4MainStatus(mainStatusEl, mainProgEl);

        if (data.cross_check) renderCrossCheck(data.cross_check);
        
        // Pass the raw AI JSON array to the summary
        updateAISummary(`ch-${ch}`, chNames[ch], allJsonObjects, totalErrors);

    } catch (err) {
        
        chunkWrap.classList.add('hidden');
        statusEl.className = 'slot-status status-failed';
        statusEl.textContent = '❌';
        chProgEl.className = 'chapter-dot error';
        resultEl.innerHTML = renderApiError(err.message);
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
        btnText.textContent = CH_BTN_LABELS[ch] || '🔍 สแกน';
    }
}

function updateSlot4MainStatus(statusEl, progEl) {
    const uploaded = Object.values(chapterState).filter(s => s.uploaded);
    const failed = Object.values(chapterState).filter(s => s.uploaded && s.status === 'issues_found');

    if (uploaded.length === 0) {
        statusEl.className = 'slot-status status-pending';
        statusEl.textContent = '⏳ รอตรวจ';
        progEl.className = 'progress-dot';
    } else if (failed.length > 0) {
        statusEl.className = 'slot-status status-failed';
        statusEl.textContent = `❌ ${uploaded.length}/5 บท (${failed.length} มีปัญหา)`;
        progEl.className = 'progress-dot error';
    } else if (uploaded.length === 5) {
        statusEl.className = 'slot-status status-passed';
        statusEl.textContent = '✅ ครบ 5 บท';
        progEl.className = 'progress-dot done';
    } else {
        statusEl.className = 'slot-status status-scanning';
        statusEl.textContent = `⏳ ${uploaded.length}/5 บท`;
        progEl.className = 'progress-dot scanning';
    }
}


// ══════════════════════════════════════════════
// Inline slot result rendering (left panel)
// ══════════════════════════════════════════════

function renderSlotResult(data, sourceKey, sourceName) {
    let html = '';

    if (data.status === 'passed') {
        html += `<div class="success-msg">✅ ผ่านการตรวจสอบ — ไม่พบข้อผิดพลาด</div>`;
    } else {
        html += `<div class="error-list">
            <div class="error-item" style="display:flex; justify-content:space-between; align-items:center;">
                <span>พบ ${data.error_count} ข้อผิดพลาด, ${data.warning_count} ข้อควรระวัง</span>
                <button class="btn-expand" onclick="openSummaryModal('${sourceKey}', '${escapeHtml(sourceName)}')">🔍 ดูรายละเอียด</button>
            </div>
        </div>`;
    }

    return html;
}

function renderApiError(message) {
    return `<div class="error-list">
        <div class="error-item"><span class="err-icon">⚠️</span><span>${escapeHtml(message)}</span></div>
    </div>`;
}


// ══════════════════════════════════════════════
// SUMMARY MODAL
// ══════════════════════════════════════════════

function collectErrors(source, errors) {
    allErrors = allErrors.filter(e => e._source !== source);
    for (const err of errors) {
        allErrors.push({ ...err, _source: source });
    }
}

function openSummaryModal(sourceKey, sourceName) {
    const overlay = document.getElementById('summary-overlay');
    overlay.classList.remove('hidden');
    renderSummaryModal(sourceKey, sourceName);
}

function closeSummaryModal() {
    const overlay = document.getElementById('summary-overlay');
    overlay.classList.add('hidden');
}

function renderSummaryModal(sourceKey, sourceName) {
    const body = document.getElementById('summary-modal-body');
    const stats = document.getElementById('summary-stats');

    const filteredErrors = sourceName ? allErrors.filter(e => e._source === sourceName) : allErrors;
    const filteredAI = sourceKey ? (aiSummaries[sourceKey] ? { [sourceKey]: aiSummaries[sourceKey] } : {}) : aiSummaries;

    if (filteredErrors.length === 0 && Object.keys(filteredAI).length === 0) {
        body.innerHTML = `<div class="empty-state">
            <div class="empty-icon">🎉</div>
            <p>ไม่พบข้อผิดพลาดใดๆ</p>
        </div>`;
        stats.innerHTML = '';
        return;
    }

    let errCount = 0;
    let warnCount = 0;
    
    filteredErrors.forEach(e => {
        if (e.severity === 'error') errCount++;
        else warnCount++;
    });
    
    for (const [, data] of Object.entries(filteredAI)) {
        errCount += data.aiErrorCount;
    }

    stats.innerHTML = `
        <div style="display:flex; gap:24px; color:white;">
            <div><strong>🔴 Errors:</strong> <span style="color:var(--error);">${errCount}</span></div>
            <div><strong>⚠️ Warnings:</strong> <span style="color:var(--warning);">${warnCount}</span></div>
        </div>
    `;

    let html = '';

    if (filteredErrors.length > 0) {
        html += `<h3 style="color:var(--kku-gold); margin-bottom:16px;">🔴 Hard Rules Feedback</h3>`;
        html += `<table class="modal-table">
            <thead>
                <tr>
                    <th>Location / Source</th>
                    <th>Issue</th>
                    <th>Detail</th>
                </tr>
            </thead>
            <tbody>`;
        for (const err of filteredErrors) {
            let badge = err.severity === 'error' 
                ? `<span class="badge-error">🔴 Error</span>` 
                : `<span class="badge-warning">⚠️ Warning</span>`;
            html += `<tr>
                <td style="white-space:nowrap;">
                    <strong>${escapeHtml(err._source)}</strong><br>
                    <span style="color:var(--text-secondary); font-size:12px;">${escapeHtml(err.location)}</span>
                </td>
                <td>
                    ${escapeHtml(err.issue)}
                    <div style="margin-top:8px; text-align:right;">${badge}</div>
                </td>
                <td>${escapeHtml(err.detail)}</td>
            </tr>`;
        }
        html += `</tbody></table>`;
    }

    if (Object.keys(filteredAI).length > 0) {
        html += `<h3 style="color:var(--kku-gold); margin-top:32px; margin-bottom:16px;">🤖 AI Soft Rules Feedback</h3>`;
        for (const [, data] of Object.entries(filteredAI)) {
            html += `<div style="background:rgba(255,255,255,0.02); padding:16px; border:1px solid rgba(255,255,255,0.05); border-radius:var(--radius-sm); margin-bottom:12px;">
                <h4 style="margin-bottom:8px; color:var(--text-muted);">${escapeHtml(data.label)}</h4>
                <div style="line-height:1.6; font-size:14px;">${data.fullHtml}</div>
            </div>`;
        }
    }

    body.innerHTML = html;
}


// ══════════════════════════════════════════════
// RIGHT PANEL: Cross-Check
// ══════════════════════════════════════════════

function renderCrossCheck(cc) {
    const area = document.getElementById('crosscheck-area');

    if (!cc.is_complete) {
        area.innerHTML = `<div class="empty-state">
            <div class="empty-icon">🔍</div>
            <p>อัปโหลด Slot 4 และ Slot 5 ให้ครบเพื่อเปิดใช้งาน</p>
        </div>`;
        return;
    }

    let html = '';

    html += `<div class="crosscheck-row matched">
        <span class="crosscheck-label">✅ อ้างอิงตรงกัน (Matched)</span>
        <span class="crosscheck-count">${cc.matched.length}</span>
    </div>`;

    html += `<div class="crosscheck-row missing">
        <span class="crosscheck-label">❌ ในเนื้อหาแต่ไม่มีในบรรณานุกรม</span>
        <span class="crosscheck-count">${cc.cited_but_not_referenced.length}</span>
    </div>`;

    html += `<div class="crosscheck-row extra">
        <span class="crosscheck-label">⚠️ ในบรรณานุกรมแต่ไม่ได้อ้างอิง</span>
        <span class="crosscheck-count">${cc.referenced_but_not_cited.length}</span>
    </div>`;

    if (cc.cited_but_not_referenced.length > 0) {
        html += `<div style="margin-top:12px;"><div style="font-size:12px;font-weight:600;color:var(--error);margin-bottom:6px;">
            ❌ ผู้แต่งที่อ้างอิงในเนื้อหาแต่ไม่พบในบรรณานุกรม:</div>
            <ul class="unmatched-list">`;
        for (const name of cc.cited_but_not_referenced) html += `<li>🔸 ${escapeHtml(name)}</li>`;
        html += `</ul></div>`;
    }

    if (cc.referenced_but_not_cited.length > 0) {
        html += `<div style="margin-top:12px;"><div style="font-size:12px;font-weight:600;color:var(--warning);margin-bottom:6px;">
            ⚠️ ผู้แต่งในบรรณานุกรมที่ไม่ได้ถูกอ้างอิง:</div>
            <ul class="unmatched-list">`;
        for (const name of cc.referenced_but_not_cited) html += `<li>🔹 ${escapeHtml(name)}</li>`;
        html += `</ul></div>`;
    }

    if (cc.matched.length > 0 && cc.cited_but_not_referenced.length === 0 && cc.referenced_but_not_cited.length === 0) {
        html += `<div class="success-msg" style="margin-top:12px;">🎉 ยอดเยี่ยม! การอ้างอิงทุกรายการตรงกัน</div>`;
    }

    area.innerHTML = html;
}


// ══════════════════════════════════════════════
// RIGHT PANEL: AI Summary
// ══════════════════════════════════════════════

const aiSummaries = {};

function updateAISummary(key, label, items, totalErrors) {
    aiSummaries[key] = { label, totalErrors: totalErrors, aiErrorCount: items.length, fullHtml: buildTableHTML(items) };
    const area = document.getElementById('ai-summary-area');

    let html = `<table class="ai-summary-table">
        <thead>
            <tr>
                <th>ส่วนที่ (Slot Name)</th>
                <th style="text-align:right;">จำนวนข้อผิดพลาด</th>
            </tr>
        </thead>
        <tbody>`;
    for (const [, data] of Object.entries(aiSummaries)) {
        html += `<tr>
            <td>${escapeHtml(data.label)}</td>
            <td style="text-align:right; font-weight:600; color:${data.totalErrors > 0 ? 'var(--error)' : 'var(--success)'};">${data.totalErrors} จุด</td>
        </tr>`;
    }
    html += `</tbody></table>`;
    area.innerHTML = html;
}


// ══════════════════════════════════════════════
// Utilities
// ══════════════════════════════════════════════

function splitIntoChunks(text, chunkSize = 2000) {
    if (!text) return [""];
    const chunks = [];
    const paragraphs = text.split('\n\n');
    let current = '';
    for (const para of paragraphs) {
        if (current.length + para.length + 2 > chunkSize && current) {
            chunks.push(current.trim());
            current = para;
        } else {
            current = current ? (current + '\n\n' + para) : para;
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
            <td>
                ${escapeHtml(item.issue || '')}
                <div style="margin-top:8px; text-align:right;">
                    <span class="badge-ai">🤖 AI Check</span>
                    <span class="badge-error">🔴 ข้อบกพร่อง</span>
                </div>
            </td>
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

// ══════════════════════════════════════════════

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
        const r = (Math.random() * 16) | 0;
        return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
    });
}


// ══════════════════════════════════════════════
// PDF Export
// ══════════════════════════════════════════════

async function exportPDF() {
    const btn = document.getElementById('btn-export-pdf');
    btn.disabled = true;
    btn.textContent = '⏳ กำลังสร้าง PDF...';

    document.querySelectorAll('.slot-item').forEach(el => el.classList.add('open'));
    document.querySelectorAll('.sub-slot').forEach(el => el.classList.add('open'));
    document.body.classList.add('exporting-pdf');

    await new Promise(r => setTimeout(r, 300));

    try {
        const dashboard = document.querySelector('.dashboard');
        const opt = {
            margin: [10, 10, 10, 10],
            filename: `KKU_Thesis_Report_${new Date().toISOString().slice(0, 10)}.pdf`,
            image: { type: 'jpeg', quality: 0.95 },
            html2canvas: { scale: 2, useCORS: true, scrollY: 0 },
            jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
            pagebreak: { mode: ['avoid-all', 'css', 'legacy'] },
        };

        await html2pdf().set(opt).from(dashboard).save();
    } catch (err) {
        console.error('PDF export failed:', err);
        alert('❌ ไม่สามารถสร้าง PDF ได้: ' + err.message);
    } finally {
        document.body.classList.remove('exporting-pdf');
        btn.disabled = false;
        btn.textContent = '📥 Export Report (PDF)';
    }
}
