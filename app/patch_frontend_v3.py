import re

app_js_path = r"d:\Ai_thesis\app\static\app.js"
style_css_path = r"d:\Ai_thesis\app\static\style.css"

with open(app_js_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update renderSlotResult
old_renderSlotResult = """function renderSlotResult(data) {
    let html = '';

    if (data.status === 'passed') {
        html += `<div class="success-msg">✅ ผ่านการตรวจสอบ — ไม่พบข้อผิดพลาด</div>`;
    } else {
        const errCount = data.hard_rules_errors.filter(e => e.severity === 'error').length;
        const warnCount = data.hard_rules_errors.filter(e => e.severity === 'warning').length;
        html += `<div class="error-list">
            <div class="error-item" style="display:flex; justify-content:space-between; align-items:center;">
                <span>พบ ${errCount} ข้อผิดพลาด, ${warnCount} ข้อควรระวัง</span>
                <button class="btn-expand" onclick="openSummaryModal()">🔍 ดูรายละเอียด</button>
            </div>
        </div>`;
    }

    return html;
}"""

new_renderSlotResult = """function renderSlotResult(data) {
    let html = '';

    if (data.status === 'passed') {
        html += `<div class="success-msg">✅ ผ่านการตรวจสอบ — ไม่พบข้อผิดพลาด</div>`;
    } else {
        html += `<div class="error-list">
            <div class="error-item" style="display:flex; justify-content:space-between; align-items:center;">
                <span>พบ ${data.error_count} ข้อผิดพลาด, ${data.warning_count} ข้อควรระวัง</span>
                <button class="btn-expand" onclick="openSummaryModal()">🔍 ดูรายละเอียด</button>
            </div>
        </div>`;
    }

    return html;
}"""
content = content.replace(old_renderSlotResult, new_renderSlotResult)


# 2. Update updateAISummary to accept totalErrors
old_updateAISummary = """function updateAISummary(key, label, items) {
    aiSummaries[key] = { label, errorCount: items.length, fullHtml: buildTableHTML(items) };"""

new_updateAISummary = """function updateAISummary(key, label, items, totalErrors) {
    aiSummaries[key] = { label, errorCount: totalErrors, fullHtml: buildTableHTML(items) };"""
content = content.replace(old_updateAISummary, new_updateAISummary)


# 3. Update callers of updateAISummary
content = content.replace("updateAISummary(`slot-${n}`, data.slot_name, allJsonObjects);", "updateAISummary(`slot-${n}`, data.slot_name, allJsonObjects, totalErrors);")
content = content.replace("updateAISummary(`ch-${ch}`, chNames[ch], allJsonObjects);", "updateAISummary(`ch-${ch}`, chNames[ch], allJsonObjects, totalErrors);")


# 4. Update buildTableHTML
old_buildTableHTML = """function buildTableHTML(items) {
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
}"""

new_buildTableHTML = """function buildTableHTML(items) {
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
                <div style="margin-bottom:6px;">
                    <span class="badge-ai">🤖 AI Check</span>
                    <span class="badge-error">🔴 ข้อบกพร่อง</span>
                </div>
                ${escapeHtml(item.issue || '')}
            </td>
            <td>${escapeHtml(item.fix || '')}</td>
        </tr>`;
    }
    html += `</tbody></table>`;
    return html;
}"""
content = content.replace(old_buildTableHTML, new_buildTableHTML)


# 5. Update renderSummaryModal Hard Rules
old_hardRulesLoop = """        for (const err of allErrors) {
            const icon = err.severity === 'error' ? '❌' : '⚠️';
            html += `<tr>
                <td style="white-space:nowrap;">
                    <strong>${escapeHtml(err._source)}</strong><br>
                    <span style="color:var(--text-secondary); font-size:12px;">${escapeHtml(err.location)}</span>
                </td>
                <td>${icon} ${escapeHtml(err.issue)}</td>
                <td>${escapeHtml(err.detail)}</td>
            </tr>`;
        }"""

new_hardRulesLoop = """        for (const err of allErrors) {
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
        }"""
content = content.replace(old_hardRulesLoop, new_hardRulesLoop)


with open(app_js_path, "w", encoding="utf-8") as f:
    f.write(content)

with open(style_css_path, "a", encoding="utf-8") as f:
    f.write('''\n
/* ══════════════════════════════════════════════ */
/* Modal Popup Tags (Visual Indicators)           */
/* ══════════════════════════════════════════════ */
.badge-error {
    color: #e74c3c;
    font-weight: 600;
    border: 1px solid rgba(231, 76, 60, 0.3);
    background: rgba(231, 76, 60, 0.1);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    display: inline-block;
}

.badge-warning {
    color: #f1c40f;
    font-weight: 600;
    border: 1px solid rgba(241, 196, 15, 0.3);
    background: rgba(241, 196, 15, 0.1);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    display: inline-block;
}

.badge-ai {
    color: #9b59b6;
    font-weight: 600;
    border: 1px solid rgba(155, 89, 182, 0.3);
    background: rgba(155, 89, 182, 0.1);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    display: inline-block;
    margin-right: 4px;
}
''')

print("Frontend patch 3 completed.")
