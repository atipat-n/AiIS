import os

path = r'd:\Ai_thesis\app\static\index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

replacements = {
    '<h1>MBA IS AI Checker <span>Pro</span></h1>': '<h1 data-i18n="header.title">MBA IS AI Checker <span>Pro</span></h1>',
    '<p class="header-subtitle">ระบบตรวจสอบรูปแบบสารนิพนธ์อัจฉริยะ มหาวิทยาลัยขอนแก่น</p>': '<p class="header-subtitle" data-i18n="header.subtitle">ระบบตรวจสอบรูปแบบสารนิพนธ์อัจฉริยะ มหาวิทยาลัยขอนแก่น</p>',
    '<div class="warning-banner">⚠️ ระบบอาจมีความคลาดเคลื่อน (AI Error) โปรดยึดตามคู่มือ MBA และคำแนะนำของอาจารย์ผู้ตรวจเป็นหลัก</div>': '<div class="warning-banner" data-i18n="banner.warning">⚠️ ระบบอาจมีความคลาดเคลื่อน (AI Error) โปรดยึดตามคู่มือ MBA และคำแนะนำของอาจารย์ผู้ตรวจเป็นหลัก</div>',
    '<h2>ขั้นตอนการใช้งาน</h2>': '<h2 data-i18n="sidebar.howToUse">ขั้นตอนการใช้งาน</h2>',
    '<li><strong>อัปโหลดเอกสาร:</strong> อัปโหลดไฟล์เอกสาร (เฉพาะ .docx) ลงในระบบ โดยแยกอัปโหลดตามช่องที่กำหนดไว้ทั้ง 5 ส่วน (เช่น ส่วนปก, ส่วนเนื้อหา, บรรณานุกรม)</li>': '<li data-i18n="sidebar.step1"><strong>อัปโหลดเอกสาร:</strong> อัปโหลดไฟล์เอกสาร (เฉพาะ .docx) ลงในระบบ โดยแยกอัปโหลดตามช่องที่กำหนดไว้ทั้ง 5 ส่วน (เช่น ส่วนปก, ส่วนเนื้อหา, บรรณานุกรม)</li>',
    '<li><strong>ระบบประมวลผล:</strong> กดปุ่ม "ตรวจสอบ" ระบบจะทำการสแกนและวิเคราะห์เอกสารของคุณอย่างละเอียด ทั้งในด้านรูปแบบโครงสร้าง (Hard Rules) และบริบทของเนื้อหา (AI) ในเวลาไม่กี่วินาที</li>': '<li data-i18n="sidebar.step2"><strong>ระบบประมวลผล:</strong> กดปุ่ม "ตรวจสอบ" ระบบจะทำการสแกนและวิเคราะห์เอกสารของคุณอย่างละเอียด ทั้งในด้านรูปแบบโครงสร้าง (Hard Rules) และบริบทของเนื้อหา (AI) ในเวลาไม่กี่วินาที</li>',
    '<li><strong>ตรวจสอบและแก้ไข:</strong> ระบบจะแสดงผลการตรวจสอบ พร้อมชี้เป้าหมายจุดที่พบข้อผิดพลาดอย่างชัดเจน (เช่น ระยะขอบผิดระเบียบ, การกั้นหน้าคลาดเคลื่อน, หรือพบคำสะกดผิด) ผู้ใช้สามารถนำข้อเสนอแนะไปปรับแก้ไขในเอกสารต้นฉบับได้ทันที</li>': '<li data-i18n="sidebar.step3"><strong>ตรวจสอบและแก้ไข:</strong> ระบบจะแสดงผลการตรวจสอบ พร้อมชี้เป้าหมายจุดที่พบข้อผิดพลาดอย่างชัดเจน (เช่น ระยะขอบผิดระเบียบ, การกั้นหน้าคลาดเคลื่อน, หรือพบคำสะกดผิด) ผู้ใช้สามารถนำข้อเสนอแนะไปปรับแก้ไขในเอกสารต้นฉบับได้ทันที</li>',
    '<div class="warning-title">⚠️ คำเตือน</div>': '<div class="warning-title" data-i18n="sidebar.warningTitle">⚠️ คำเตือน</div>',
    '<p>กรุณาตรวจสอบความถูกต้องกับอาจารย์ที่ปรึกษาอีกครั้ง ระบบนี้เป็นเพียงผู้ช่วยคัดกรองเบื้องต้น</p>': '<p data-i18n="sidebar.warningText">กรุณาตรวจสอบความถูกต้องกับอาจารย์ที่ปรึกษาอีกครั้ง ระบบนี้เป็นเพียงผู้ช่วยคัดกรองเบื้องต้น</p>',
    '<h2>อัปโหลดเอกสาร (5 ส่วน)</h2>': '<h2 data-i18n="upload.title">อัปโหลดเอกสาร (5 ส่วน)</h2>',
    '<div class="slot-title">ส่วนหน้า (Front Matter)</div>': '<div class="slot-title" data-i18n="upload.slot1Title">ส่วนหน้า (Front Matter)</div>',
    '<div class="slot-subtitle">ปกนอก ปกใน ใบรับรอง กิตติกรรมประกาศ</div>': '<div class="slot-subtitle" data-i18n="upload.slot1Sub">ปกนอก ปกใน ใบรับรอง กิตติกรรมประกาศ</div>',
    '<div class="slot-title">บทคัดย่อ (Abstract)</div>': '<div class="slot-title" data-i18n="upload.slot2Title">บทคัดย่อ (Abstract)</div>',
    '<div class="slot-subtitle">บทคัดย่อภาษาไทยและภาษาอังกฤษ</div>': '<div class="slot-subtitle" data-i18n="upload.slot2Sub">บทคัดย่อภาษาไทยและภาษาอังกฤษ</div>',
    '<div class="slot-title">สารบัญ (Table of Contents)</div>': '<div class="slot-title" data-i18n="upload.slot3Title">สารบัญ (Table of Contents)</div>',
    '<div class="slot-subtitle">สารบัญเนื้อหา สารบัญตาราง สารบัญภาพ</div>': '<div class="slot-subtitle" data-i18n="upload.slot3Sub">สารบัญเนื้อหา สารบัญตาราง สารบัญภาพ</div>',
    '<div class="slot-title">เนื้อหา (Main Content)</div>': '<div class="slot-title" data-i18n="upload.slot4Title">เนื้อหา (Main Content)</div>',
    '<div class="slot-subtitle">บทที่ 1-5 เนื้อหาหลักของวิทยานิพนธ์</div>': '<div class="slot-subtitle" data-i18n="upload.slot4Sub">บทที่ 1-5 เนื้อหาหลักของวิทยานิพนธ์</div>',
    '<div class="slot-title">บรรณานุกรม (References)</div>': '<div class="slot-title" data-i18n="upload.slot5Title">บรรณานุกรม (References)</div>',
    '<div class="slot-subtitle">รายการอ้างอิง APA 7th Edition</div>': '<div class="slot-subtitle" data-i18n="upload.slot5Sub">รายการอ้างอิง APA 7th Edition</div>',
    '<span class="sub-slot-title">บทที่ 1 บทนำ (Introduction)</span>': '<span class="sub-slot-title" data-i18n="upload.ch1Title">บทที่ 1 บทนำ (Introduction)</span>',
    '<span class="sub-slot-title">บทที่ 2 ทบทวนวรรณกรรม (Literature Review)</span>': '<span class="sub-slot-title" data-i18n="upload.ch2Title">บทที่ 2 ทบทวนวรรณกรรม (Literature Review)</span>',
    '<span class="sub-slot-title">บทที่ 3 ระเบียบวิธีวิจัย (Methodology)</span>': '<span class="sub-slot-title" data-i18n="upload.ch3Title">บทที่ 3 ระเบียบวิธีวิจัย (Methodology)</span>',
    '<span class="sub-slot-title">บทที่ 4 ผลการวิจัย (Results)</span>': '<span class="sub-slot-title" data-i18n="upload.ch4Title">บทที่ 4 ผลการวิจัย (Results)</span>',
    '<span class="sub-slot-title">บทที่ 5 สรุปและอภิปราย (Conclusion)</span>': '<span class="sub-slot-title" data-i18n="upload.ch5Title">บทที่ 5 สรุปและอภิปราย (Conclusion)</span>',
    '<p>ลากไฟล์มาวางหรือคลิกเพื่อเลือก</p>': '<p data-i18n="upload.dragDrop1">ลากไฟล์มาวางหรือคลิกเพื่อเลือก</p>',
    '<p>อัปโหลดบทที่ 1</p>': '<p data-i18n="upload.dragDrop2">อัปโหลดบทที่ 1</p>',
    '<p>อัปโหลดบทที่ 2</p>': '<p data-i18n="upload.dragDrop3">อัปโหลดบทที่ 2</p>',
    '<p>อัปโหลดบทที่ 3</p>': '<p data-i18n="upload.dragDrop4">อัปโหลดบทที่ 3</p>',
    '<p>อัปโหลดบทที่ 4</p>': '<p data-i18n="upload.dragDrop5">อัปโหลดบทที่ 4</p>',
    '<p>อัปโหลดบทที่ 5</p>': '<p data-i18n="upload.dragDrop6">อัปโหลดบทที่ 5</p>',
    '<span class="slot-status status-pending" id="status-1">⏳ รอตรวจ</span>': '<span class="slot-status status-pending" id="status-1" data-i18n="upload.statusPending">⏳ รอตรวจ</span>',
    '<span class="slot-status status-pending" id="status-2">⏳ รอตรวจ</span>': '<span class="slot-status status-pending" id="status-2" data-i18n="upload.statusPending">⏳ รอตรวจ</span>',
    '<span class="slot-status status-pending" id="status-3">⏳ รอตรวจ</span>': '<span class="slot-status status-pending" id="status-3" data-i18n="upload.statusPending">⏳ รอตรวจ</span>',
    '<span class="slot-status status-pending" id="status-4">⏳ รอตรวจ</span>': '<span class="slot-status status-pending" id="status-4" data-i18n="upload.statusPending">⏳ รอตรวจ</span>',
    '<span class="slot-status status-pending" id="status-5">⏳ รอตรวจ</span>': '<span class="slot-status status-pending" id="status-5" data-i18n="upload.statusPending">⏳ รอตรวจ</span>',
    '<span class="btn-text">🔍 สแกนส่วนหน้า</span>': '<span class="btn-text" data-i18n="btn.scan1">🔍 สแกนส่วนหน้า</span>',
    '<span class="btn-text">🔍 สแกนบทคัดย่อ</span>': '<span class="btn-text" data-i18n="btn.scan2">🔍 สแกนบทคัดย่อ</span>',
    '<span class="btn-text">🔍 สแกนสารบัญ</span>': '<span class="btn-text" data-i18n="btn.scan3">🔍 สแกนสารบัญ</span>',
    '<span class="btn-text">🔍 สแกนบทที่ 1</span>': '<span class="btn-text" data-i18n="btn.scan4_1">🔍 สแกนบทที่ 1</span>',
    '<span class="btn-text">🔍 สแกนบทที่ 2</span>': '<span class="btn-text" data-i18n="btn.scan4_2">🔍 สแกนบทที่ 2</span>',
    '<span class="btn-text">🔍 สแกนบทที่ 3</span>': '<span class="btn-text" data-i18n="btn.scan4_3">🔍 สแกนบทที่ 3</span>',
    '<span class="btn-text">🔍 สแกนบทที่ 4</span>': '<span class="btn-text" data-i18n="btn.scan4_4">🔍 สแกนบทที่ 4</span>',
    '<span class="btn-text">🔍 สแกนบทที่ 5</span>': '<span class="btn-text" data-i18n="btn.scan4_5">🔍 สแกนบทที่ 5</span>',
    '<span class="btn-text">🔍 สแกนบรรณานุกรม</span>': '<span class="btn-text" data-i18n="btn.scan5">🔍 สแกนบรรณานุกรม</span>',
    '<h2>AI Analysis & Cross-Check</h2>': '<h2 data-i18n="insights.title">AI Analysis & Cross-Check</h2>',
    '<div class="insight-title">🔗 Citation Cross-Check</div>': '<div class="insight-title" data-i18n="insights.citationTitle">🔗 Citation Cross-Check</div>',
    '<p>อัปโหลด Slot 4 (เนื้อหา) และ Slot 5 (บรรณานุกรม)<br>เพื่อเปิดใช้การตรวจสอบอ้างอิงข้ามส่วน</p>': '<p data-i18n="insights.citationEmpty">อัปโหลด Slot 4 (เนื้อหา) และ Slot 5 (บรรณานุกรม)<br>เพื่อเปิดใช้การตรวจสอบอ้างอิงข้ามส่วน</p>',
    '<div class="insight-title">🤖 AI Analysis Summary</div>': '<div class="insight-title" data-i18n="insights.aiTitle">🤖 AI Analysis Summary</div>',
    '<p>ผลวิเคราะห์จาก AI จะปรากฏที่นี่<br>หลังอัปโหลดเอกสารแต่ละส่วน</p>': '<p data-i18n="insights.aiEmpty">ผลวิเคราะห์จาก AI จะปรากฏที่นี่<br>หลังอัปโหลดเอกสารแต่ละส่วน</p>',
    '<p>© 2026 MBA IS AI Checker Pro — <a href="https://mba.kku.ac.th" target="_blank">วิทยาลัยบัณฑิตศึกษาการจัดการ\n                มหาวิทยาลัยขอนแก่น</a></p>': '<p data-i18n="footer.text">© 2026 MBA IS AI Checker Pro — <a href="https://mba.kku.ac.th" target="_blank">วิทยาลัยบัณฑิตศึกษาการจัดการ มหาวิทยาลัยขอนแก่น</a></p>',
    '<h2>รายการที่ต้องแก้ไขทั้งหมด (Full Error Checklist)</h2>': '<h2 data-i18n="modal.checklistTitle">รายการที่ต้องแก้ไขทั้งหมด (Full Error Checklist)</h2>',
    '<span class="modal-ai-disclaimer-text">ข้อควรระวัง: ผลการตรวจสอบและข้อเสนอแนะจาก AI อาจคลาดเคลื่อน หรือมีการเปลี่ยนแปลงคำแนะนำในแต่ละครั้ง โปรดใช้วิจารณญาณส่วนบุคคลในการพิจารณาแก้ไขเอกสารของท่าน</span>': '<span class="modal-ai-disclaimer-text" data-i18n="modal.aiWarning">ข้อควรระวัง: ผลการตรวจสอบและข้อเสนอแนะจาก AI อาจคลาดเคลื่อน หรือมีการเปลี่ยนแปลงคำแนะนำในแต่ละครั้ง โปรดใช้วิจารณญาณส่วนบุคคลในการพิจารณาแก้ไขเอกสารของท่าน</span>',
    '<p>ยังไม่มีผลการตรวจสอบ</p>': '<p data-i18n="modal.empty">ยังไม่มีผลการตรวจสอบ</p>',
    '<h2 class="modal-title">คำเตือนการใช้งานระบบ</h2>': '<h2 class="modal-title" data-i18n="disclaimer.title">คำเตือนการใช้งานระบบ</h2>',
    '<p>ห้ามเชื่อถือการทำงานของระบบ 100% เนื่องจากการทำงานของ AI\n                    และระบบสกัดข้อมูลอาจมีความคลาดเคลื่อนหรือทำงานผิดพลาด (AI Error) ได้ในทางเทคนิค</p>': '<p data-i18n="disclaimer.text1">ห้ามเชื่อถือการทำงานของระบบ 100% เนื่องจากการทำงานของ AI และระบบสกัดข้อมูลอาจมีความคลาดเคลื่อนหรือทำงานผิดพลาด (AI Error) ได้ในทางเทคนิค</p>',
    '<p>ระบบนี้เป็นเพียง<strong>ผู้ช่วยคัดกรองเบื้องต้น</strong>เท่านั้น นักศึกษาต้องศึกษาและปฏิบัติตาม\n                    <strong>"กฎระเบียบการทำเล่มวิทยานิพนธ์/การศึกษาอิสระของหลักสูตร MBA"</strong> อย่างเคร่งครัด\n                    และต้องผ่านการตรวจสอบจากอาจารย์ที่ปรึกษาและผู้ตรวจรูปแบบของมหาวิทยาลัยเสมอ\n                </p>': '<p data-i18n="disclaimer.text2">ระบบนี้เป็นเพียง<strong>ผู้ช่วยคัดกรองเบื้องต้น</strong>เท่านั้น นักศึกษาต้องศึกษาและปฏิบัติตาม <strong>"กฎระเบียบการทำเล่มวิทยานิพนธ์/การศึกษาอิสระของหลักสูตร MBA"</strong> อย่างเคร่งครัด และต้องผ่านการตรวจสอบจากอาจารย์ที่ปรึกษาและผู้ตรวจรูปแบบของมหาวิทยาลัยเสมอ</p>',
    '<button class="modal-accept-btn" id="modal-accept-btn" onclick="closeDisclaimer()">รับทราบและเข้าใช้งาน (I\n                Understand)</button>': '<button class="modal-accept-btn" id="modal-accept-btn" onclick="closeDisclaimer()" data-i18n="disclaimer.btn">รับทราบและเข้าใช้งาน (I Understand)</button>',
}

for k, v in replacements.items():
    html = html.replace(k, v)

# Update Toggle Buttons to include Lang Toggle side-by-side
toggle_old = '''                <!-- Dark Mode Toggle -->
                <button id="theme-toggle" class="theme-toggle-btn" aria-label="Toggle Dark Mode">
                    <span class="sun-icon">☀️</span>
                    <span class="moon-icon">🌙</span>
                </button>'''

toggle_new = '''                <div style="display:flex; gap:8px;">
                    <!-- Lang Toggle -->
                    <button id="lang-toggle" class="theme-toggle-btn" aria-label="Toggle Language" style="font-weight: 600;">
                        <span class="lang-th">TH</span>&nbsp;<span style="color:var(--text-muted)">|</span>&nbsp;<span class="lang-en" style="opacity: 0.4;">EN</span>
                    </button>
                    <!-- Dark Mode Toggle -->
                    <button id="theme-toggle" class="theme-toggle-btn" aria-label="Toggle Dark Mode">
                        <span class="sun-icon">☀️</span>
                        <span class="moon-icon">🌙</span>
                    </button>
                </div>'''
html = html.replace(toggle_old, toggle_new)

# Inject <script src="i18n.js"></script> before <script src="app.js"></script>
html = html.replace('<script src="app.js"></script>', '<script src="i18n.js"></script>\n    <script src="app.js"></script>')

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)
