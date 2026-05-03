import re

app_js_path = r"d:\Ai_thesis\app\static\app.js"
style_css_path = r"d:\Ai_thesis\app\static\style.css"

with open(app_js_path, "r", encoding="utf-8") as f:
    app_js = f.read()

with open(style_css_path, "r", encoding="utf-8") as f:
    style_css = f.read()

# 1. Update renderSlotResult
app_js = app_js.replace(
    "function renderSlotResult(data) {",
    "function renderSlotResult(data, sourceKey, sourceName) {"
)
app_js = app_js.replace(
    """<button class="btn-expand" onclick="openSummaryModal()">🔍 ดูรายละเอียด</button>""",
    """<button class="btn-expand" onclick="openSummaryModal('${sourceKey}', '${escapeHtml(sourceName)}')">🔍 ดูรายละเอียด</button>"""
)

# 2. Update uploadSlot calls
app_js = app_js.replace(
    """        resultEl.innerHTML = renderSlotResult(data);
        collectErrors(`Slot ${n}: ${data.slot_name}`, data.hard_rules_errors);""",
    """        const sourceKey = `slot-${n}`;
        const sourceName = `Slot ${n}: ${data.slot_name}`;
        resultEl.innerHTML = renderSlotResult(data, sourceKey, sourceName);
        collectErrors(sourceName, data.hard_rules_errors);"""
)

# 3. Update uploadChapter calls
app_js = app_js.replace(
    """        let resultHtml = renderSlotResult(data);
        if (data.citations_found !== undefined) {""",
    """        const sourceKey = `ch-${ch}`;
        const chNames = { 1: 'บทที่ 1', 2: 'บทที่ 2', 3: 'บทที่ 3', 4: 'บทที่ 4', 5: 'บทที่ 5' };
        const sourceName = `Slot 4.${ch}: ${chNames[ch]}`;
        let resultHtml = renderSlotResult(data, sourceKey, sourceName);
        if (data.citations_found !== undefined) {"""
)
app_js = app_js.replace(
    """        const chNames = { 1: 'บทที่ 1', 2: 'บทที่ 2', 3: 'บทที่ 3', 4: 'บทที่ 4', 5: 'บทที่ 5' };
        collectErrors(`Slot 4.${ch}: ${chNames[ch]}`, data.hard_rules_errors);""",
    """        collectErrors(sourceName, data.hard_rules_errors);"""
)

# 4. Update updateAISummary
old_updateAISummary = """function updateAISummary(key, label, items, totalErrors) {
    aiSummaries[key] = { label, errorCount: totalErrors, fullHtml: buildTableHTML(items) };
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
new_updateAISummary = """function updateAISummary(key, label, items, totalErrors) {
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
}"""
app_js = app_js.replace(old_updateAISummary, new_updateAISummary)

# 5. Update buildTableHTML
old_buildTableHTML = """            <td>
                <div style="margin-bottom:6px;">
                    <span class="badge-ai">🤖 AI Check</span>
                    <span class="badge-error">🔴 ข้อบกพร่อง</span>
                </div>
                ${escapeHtml(item.issue || '')}
            </td>"""
new_buildTableHTML = """            <td>
                ${escapeHtml(item.issue || '')}
                <div style="margin-top:8px; text-align:right;">
                    <span class="badge-ai">🤖 AI Check</span>
                    <span class="badge-error">🔴 ข้อบกพร่อง</span>
                </div>
            </td>"""
app_js = app_js.replace(old_buildTableHTML, new_buildTableHTML)

# 6. Update openSummaryModal and renderSummaryModal
old_modals = """function openSummaryModal() {
    const overlay = document.getElementById('summary-overlay');
    overlay.classList.remove('hidden');
    renderSummaryModal();
}

function closeSummaryModal() {
    const overlay = document.getElementById('summary-overlay');
    overlay.classList.add('hidden');
}

function renderSummaryModal() {
    const body = document.getElementById('summary-modal-body');
    const stats = document.getElementById('summary-stats');

    if (allErrors.length === 0 && Object.keys(aiSummaries).length === 0) {
        body.innerHTML = `<div class="empty-state">
            <div class="empty-icon">🎉</div>
            <p>ไม่พบข้อผิดพลาดใดๆ</p>
        </div>`;
        stats.innerHTML = '';
        return;
    }

    let errCount = 0;
    let warnCount = 0;
    allErrors.forEach(e => {
        if (e.severity === 'error') errCount++;
        else warnCount++;
    });

    stats.innerHTML = `
        <div style="display:flex; gap:24px; color:white;">
            <div><strong>🛑 Errors:</strong> <span style="color:var(--error);">${errCount}</span></div>
            <div><strong>⚠️ Warnings:</strong> <span style="color:var(--warning);">${warnCount}</span></div>
        </div>
    `;

    let html = '';

    if (allErrors.length > 0) {
        html += `<h3 style="color:var(--kku-gold); margin-bottom:16px;">🛑 Hard Rules Feedback</h3>`;
        html += `<table class="modal-table">
            <thead>
                <tr>
                    <th>Location / Source</th>
                    <th>Issue</th>
                    <th>Detail</th>
                </tr>
            </thead>
            <tbody>`;
        for (const err of allErrors) {
            let badge = err.severity === 'error' 
                ? `<span class="badge-error">🔴 Error</span>` 
                : `<span class="badge-warning">⚠️ Warning</span>`;
            html += `<tr>
                <td style="white-space:nowrap;">
                    <strong>${escapeHtml(err._source)}</strong><br>
                    <span style="color:var(--text-secondary); font-size:12px;">${escapeHtml(err.location)}</span>
                </td>
                <td>
                    <div style="margin-bottom:6px;">${badge}</div>
                    ${escapeHtml(err.issue)}
                </td>
                <td>${escapeHtml(err.detail)}</td>
            </tr>`;
        }
        html += `</tbody></table>`;
    }

    if (Object.keys(aiSummaries).length > 0) {
        html += `<h3 style="color:var(--kku-gold); margin-top:32px; margin-bottom:16px;">🤖 AI Soft Rules Feedback</h3>`;
        for (const [, data] of Object.entries(aiSummaries)) {
            html += `<div style="background:rgba(255,255,255,0.02); padding:16px; border:1px solid rgba(255,255,255,0.05); border-radius:var(--radius-sm); margin-bottom:12px;">
                <h4 style="margin-bottom:8px; color:var(--text-muted);">${escapeHtml(data.label)}</h4>
                <div style="line-height:1.6; font-size:14px;">${data.fullHtml}</div>
            </div>`;
        }
    }

    body.innerHTML = html;
}"""

new_modals = """function openSummaryModal(sourceKey, sourceName) {
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
            <div><strong>🛑 Errors:</strong> <span style="color:var(--error);">${errCount}</span></div>
            <div><strong>⚠️ Warnings:</strong> <span style="color:var(--warning);">${warnCount}</span></div>
        </div>
    `;

    let html = '';

    if (filteredErrors.length > 0) {
        html += `<h3 style="color:var(--kku-gold); margin-bottom:16px;">🛑 Hard Rules Feedback</h3>`;
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
}"""
app_js = app_js.replace(old_modals, new_modals)

# 7. Update style.css overlay
old_overlay = """.summary-overlay {
    position: fixed;
    inset: 0;
    z-index: 9999;
    background: rgba(0, 0, 0, 0.85);
    backdrop-filter: blur(12px);
    display: flex;"""

new_overlay = """.summary-overlay {
    position: fixed;
    inset: 0;
    z-index: 9999;
    background-color: rgba(15, 23, 42, 0.75) !important;
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
    display: flex;"""
style_css = style_css.replace(old_overlay, new_overlay)

with open(app_js_path, "w", encoding="utf-8") as f:
    f.write(app_js)

with open(style_css_path, "w", encoding="utf-8") as f:
    f.write(style_css)

print("Modal popup refactored successfully.")
