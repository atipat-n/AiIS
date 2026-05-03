import re

app_js_path = r"d:\Ai_thesis\app\static\app.js"
style_css_path = r"d:\Ai_thesis\app\static\style.css"

with open(app_js_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update updateAISummary
old_updateAISummary = """function updateAISummary(key, label, feedback) {
    aiSummaries[key] = { label, feedback };
    const area = document.getElementById('ai-summary-area');

    let html = '';
    for (const [, data] of Object.entries(aiSummaries)) {
        html += `<div class="ai-feedback" style="margin-bottom:8px;">
            <div class="ai-feedback-label">🤖 ${escapeHtml(data.label)}</div>
            <div>${data.feedback}</div>
        </div>`;
    }

    area.innerHTML = html;
}"""

new_updateAISummary = """function updateAISummary(key, label, items) {
    aiSummaries[key] = { label, errorCount: items.length, fullHtml: buildTableHTML(items) };
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
            <td style="text-align:right; font-weight:600; color:${data.errorCount > 0 ? 'var(--error)' : 'var(--success)'};">${data.errorCount} จุด</td>
        </tr>`;
    }
    html += `</tbody></table>`;
    area.innerHTML = html;
}"""

content = content.replace(old_updateAISummary, new_updateAISummary)

# 2. Update renderSummaryModal to use fullHtml
old_modal_ai = """    if (Object.keys(aiSummaries).length > 0) {
        html += `<h3 style="color:var(--kku-gold); margin-top:32px; margin-bottom:16px;">🤖 AI Soft Rules Feedback</h3>`;
        for (const [, data] of Object.entries(aiSummaries)) {
            html += `<div style="background:rgba(255,255,255,0.02); padding:16px; border:1px solid rgba(255,255,255,0.05); border-radius:var(--radius-sm); margin-bottom:12px;">
                <h4 style="margin-bottom:8px; color:var(--text-muted);">${escapeHtml(data.label)}</h4>
                <div style="line-height:1.6; font-size:14px;">${data.feedback}</div>
            </div>`;
        }
    }"""

new_modal_ai = """    if (Object.keys(aiSummaries).length > 0) {
        html += `<h3 style="color:var(--kku-gold); margin-top:32px; margin-bottom:16px;">🤖 AI Soft Rules Feedback</h3>`;
        for (const [, data] of Object.entries(aiSummaries)) {
            html += `<div style="background:rgba(255,255,255,0.02); padding:16px; border:1px solid rgba(255,255,255,0.05); border-radius:var(--radius-sm); margin-bottom:12px;">
                <h4 style="margin-bottom:8px; color:var(--text-muted);">${escapeHtml(data.label)}</h4>
                <div style="line-height:1.6; font-size:14px;">${data.fullHtml}</div>
            </div>`;
        }
    }"""
content = content.replace(old_modal_ai, new_modal_ai)

# 3. Fix uploadSlot
old_uploadSlot = """        const data = await res.json();
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


        slotState[n] = {
            uploaded: true,
            status: data.status,
            errors: data.error_count,
            warnings: data.warning_count,
            name: data.slot_name,
        };

        if (data.status === 'passed') {
            statusEl.className = 'slot-status status-passed';
            statusEl.textContent = '✅ ผ่าน';
            progEl.className = 'progress-dot done';
        } else {
            statusEl.className = 'slot-status status-failed';
            statusEl.textContent = `❌ ${data.error_count} errors, ${data.warning_count} warnings`;
            progEl.className = 'progress-dot error';
        }

        resultEl.innerHTML = renderSlotResult(data);
        collectErrors(`Slot ${n}: ${data.slot_name}`, data.hard_rules_errors);
        if (data.cross_check) renderCrossCheck(data.cross_check);
        if (data.ai_soft_rules_feedback) {
            updateAISummary(`slot-${n}`, data.slot_name, data.ai_soft_rules_feedback);
        }"""

new_uploadSlot = """        const data = await res.json();
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

        resultEl.innerHTML = renderSlotResult(data);
        collectErrors(`Slot ${n}: ${data.slot_name}`, data.hard_rules_errors);
        if (data.cross_check) renderCrossCheck(data.cross_check);
        
        // Pass the raw AI JSON array to the summary
        updateAISummary(`slot-${n}`, data.slot_name, allJsonObjects);"""

content = content.replace(old_uploadSlot, new_uploadSlot)

# 4. Fix uploadChapter
old_uploadChapter = """        const data = await res.json();
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


        chapterState[ch] = {
            uploaded: true,
            status: data.status,
            errors: data.error_count,
            warnings: data.warning_count,
        };

        if (data.status === 'passed') {
            statusEl.className = 'slot-status status-passed';
            statusEl.textContent = '✅';
            chProgEl.className = 'chapter-dot done';
        } else {
            statusEl.className = 'slot-status status-failed';
            statusEl.textContent = `❌ ${data.error_count}`;
            chProgEl.className = 'chapter-dot error';
        }

        let resultHtml = renderSlotResult(data);
        if (data.citations_found !== undefined) {
            resultHtml += `<div class="ai-feedback" style="margin-top:8px;">
                <div class="ai-feedback-label">🔗 Citations Found</div>
                <div>พบการอ้างอิงในบทนี้: ${data.citations_found} | รวมทั้งหมด: ${data.total_citations}</div>
            </div>`;
        }
        resultEl.innerHTML = resultHtml;

        const chNames = { 1: 'บทที่ 1', 2: 'บทที่ 2', 3: 'บทที่ 3', 4: 'บทที่ 4', 5: 'บทที่ 5' };
        collectErrors(`Slot 4.${ch}: ${chNames[ch]}`, data.hard_rules_errors);

        updateSlot4MainStatus(mainStatusEl, mainProgEl);

        if (data.cross_check) renderCrossCheck(data.cross_check);
        if (data.ai_soft_rules_feedback) {
            updateAISummary(`ch-${ch}`, chNames[ch], data.ai_soft_rules_feedback);
        }"""

new_uploadChapter = """        const data = await res.json();
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

        let resultHtml = renderSlotResult(data);
        if (data.citations_found !== undefined) {
            resultHtml += `<div class="ai-feedback" style="margin-top:8px;">
                <div class="ai-feedback-label">🔗 Citations Found</div>
                <div>พบการอ้างอิงในบทนี้: ${data.citations_found} | รวมทั้งหมด: ${data.total_citations}</div>
            </div>`;
        }
        resultEl.innerHTML = resultHtml;

        const chNames = { 1: 'บทที่ 1', 2: 'บทที่ 2', 3: 'บทที่ 3', 4: 'บทที่ 4', 5: 'บทที่ 5' };
        collectErrors(`Slot 4.${ch}: ${chNames[ch]}`, data.hard_rules_errors);

        updateSlot4MainStatus(mainStatusEl, mainProgEl);

        if (data.cross_check) renderCrossCheck(data.cross_check);
        
        // Pass the raw AI JSON array to the summary
        updateAISummary(`ch-${ch}`, chNames[ch], allJsonObjects);"""

content = content.replace(old_uploadChapter, new_uploadChapter)

with open(app_js_path, "w", encoding="utf-8") as f:
    f.write(content)

with open(style_css_path, "a", encoding="utf-8") as f:
    f.write('''\n
/* ══════════════════════════════════════════════ */
/* AI Summary Container                           */
/* ══════════════════════════════════════════════ */
#ai-summary-area {
    max-height: 300px;
    overflow-y: auto;
    padding-right: 4px;
}

#ai-summary-area::-webkit-scrollbar {
    width: 6px;
}

#ai-summary-area::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.02);
}

#ai-summary-area::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
}

/* ══════════════════════════════════════════════ */
/* AI Summary Table                               */
/* ══════════════════════════════════════════════ */
.ai-summary-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    color: var(--text-primary);
}
.ai-summary-table th {
    text-align: left;
    padding: 8px 0;
    color: var(--kku-gold);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.ai-summary-table td {
    padding: 10px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
''')

print("Frontend task 2 and 3 patched successfully.")
