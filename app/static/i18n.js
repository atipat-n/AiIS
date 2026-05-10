const translations = {
    th: {
        "header.title": "MBA IS AI Checker <span>Pro</span>",
        "header.subtitle": "ระบบตรวจสอบรูปแบบสารนิพนธ์อัจฉริยะ มหาวิทยาลัยขอนแก่น",
        "banner.warning": "⚠️ ระบบอาจมีความคลาดเคลื่อน (AI Error) โปรดยึดตามคู่มือ MBA และคำแนะนำของอาจารย์ผู้ตรวจเป็นหลัก",
        "sidebar.howToUse": "ขั้นตอนการใช้งาน",
        "sidebar.step1": "<strong>อัปโหลดเอกสาร:</strong> อัปโหลดไฟล์เอกสาร (เฉพาะ .docx) ลงในระบบ โดยแยกอัปโหลดตามช่องที่กำหนดไว้ทั้ง 5 ส่วน (เช่น ส่วนปก, ส่วนเนื้อหา, บรรณานุกรม)",
        "sidebar.step2": "<strong>ระบบประมวลผล:</strong> กดปุ่ม \"ตรวจสอบ\" ระบบจะทำการสแกนและวิเคราะห์เอกสารของคุณอย่างละเอียด ทั้งในด้านรูปแบบโครงสร้าง (Hard Rules) และบริบทของเนื้อหา (AI) ในเวลาไม่กี่วินาที",
        "sidebar.step3": "<strong>ตรวจสอบและแก้ไข:</strong> ระบบจะแสดงผลการตรวจสอบ พร้อมชี้เป้าหมายจุดที่พบข้อผิดพลาดอย่างชัดเจน (เช่น ระยะขอบผิดระเบียบ, การกั้นหน้าคลาดเคลื่อน, หรือพบคำสะกดผิด) ผู้ใช้สามารถนำข้อเสนอแนะไปปรับแก้ไขในเอกสารต้นฉบับได้ทันที",
        "sidebar.warningTitle": "⚠️ คำเตือน",
        "sidebar.warningText": "กรุณาตรวจสอบความถูกต้องกับอาจารย์ที่ปรึกษาอีกครั้ง ระบบนี้เป็นเพียงผู้ช่วยคัดกรองเบื้องต้น",
        "upload.title": "อัปโหลดเอกสาร (5 ส่วน)",
        "upload.slot1Title": "ส่วนหน้า (Front Matter)",
        "upload.slot1Sub": "ปกนอก ปกใน ใบรับรอง กิตติกรรมประกาศ",
        "upload.slot2Title": "บทคัดย่อ (Abstract)",
        "upload.slot2Sub": "บทคัดย่อภาษาไทยและภาษาอังกฤษ",
        "upload.slot3Title": "สารบัญ (Table of Contents)",
        "upload.slot3Sub": "สารบัญเนื้อหา สารบัญตาราง สารบัญภาพ",
        "upload.slot4Title": "เนื้อหา (Main Content)",
        "upload.slot4Sub": "บทที่ 1-5 เนื้อหาหลักของวิทยานิพนธ์",
        "upload.slot5Title": "บรรณานุกรม (References)",
        "upload.slot5Sub": "รายการอ้างอิง APA 7th Edition",
        "upload.ch1Title": "บทที่ 1 บทนำ (Introduction)",
        "upload.ch2Title": "บทที่ 2 ทบทวนวรรณกรรม (Literature Review)",
        "upload.ch3Title": "บทที่ 3 ระเบียบวิธีวิจัย (Methodology)",
        "upload.ch4Title": "บทที่ 4 ผลการวิจัย (Results)",
        "upload.ch5Title": "บทที่ 5 สรุปและอภิปราย (Conclusion)",
        "upload.dragDrop1": "ลากไฟล์มาวางหรือคลิกเพื่อเลือก",
        "upload.dragDrop2": "อัปโหลดบทที่ 1",
        "upload.dragDrop3": "อัปโหลดบทที่ 2",
        "upload.dragDrop4": "อัปโหลดบทที่ 3",
        "upload.dragDrop5": "อัปโหลดบทที่ 4",
        "upload.dragDrop6": "อัปโหลดบทที่ 5",
        "upload.statusPending": "⏳ รอตรวจ",
        "btn.scan1": "🔍 สแกนส่วนหน้า",
        "btn.scan2": "🔍 สแกนบทคัดย่อ",
        "btn.scan3": "🔍 สแกนสารบัญ",
        "btn.scan4_1": "🔍 สแกนบทที่ 1",
        "btn.scan4_2": "🔍 สแกนบทที่ 2",
        "btn.scan4_3": "🔍 สแกนบทที่ 3",
        "btn.scan4_4": "🔍 สแกนบทที่ 4",
        "btn.scan4_5": "🔍 สแกนบทที่ 5",
        "btn.scan5": "🔍 สแกนบรรณานุกรม",
        "insights.title": "AI Analysis & Cross-Check",
        "insights.citationTitle": "🔗 Citation Cross-Check",
        "insights.citationEmpty": "อัปโหลด Slot 4 (เนื้อหา) และ Slot 5 (บรรณานุกรม)<br>เพื่อเปิดใช้การตรวจสอบอ้างอิงข้ามส่วน",
        "insights.aiTitle": "🤖 AI Analysis Summary",
        "insights.aiEmpty": "ผลวิเคราะห์จาก AI จะปรากฏที่นี่<br>หลังอัปโหลดเอกสารแต่ละส่วน",
        "footer.text": "© 2026 MBA IS AI Checker Pro — <a href='https://mba.kku.ac.th' target='_blank'>วิทยาลัยบัณฑิตศึกษาการจัดการ มหาวิทยาลัยขอนแก่น</a>",
        "modal.checklistTitle": "รายการที่ต้องแก้ไขทั้งหมด (Full Error Checklist)",
        "modal.aiWarning": "ข้อควรระวัง: ผลการตรวจสอบและข้อเสนอแนะจาก AI อาจคลาดเคลื่อน หรือมีการเปลี่ยนแปลงคำแนะนำในแต่ละครั้ง โปรดใช้วิจารณญาณส่วนบุคคลในการพิจารณาแก้ไขเอกสารของท่าน",
        "modal.empty": "ยังไม่มีผลการตรวจสอบ",
        "disclaimer.title": "คำเตือนการใช้งานระบบ",
        "disclaimer.text1": "ห้ามเชื่อถือการทำงานของระบบ 100% เนื่องจากการทำงานของ AI และระบบสกัดข้อมูลอาจมีความคลาดเคลื่อนหรือทำงานผิดพลาด (AI Error) ได้ในทางเทคนิค",
        "disclaimer.text2": "ระบบนี้เป็นเพียง<strong>ผู้ช่วยคัดกรองเบื้องต้น</strong>เท่านั้น นักศึกษาต้องศึกษาและปฏิบัติตาม <strong>\"กฎระเบียบการทำเล่มวิทยานิพนธ์/การศึกษาอิสระของหลักสูตร MBA\"</strong> อย่างเคร่งครัด และต้องผ่านการตรวจสอบจากอาจารย์ที่ปรึกษาและผู้ตรวจรูปแบบของมหาวิทยาลัยเสมอ",
        "disclaimer.btn": "รับทราบและเข้าใช้งาน (I Understand)"
    },
    en: {
        "header.title": "MBA IS AI Checker <span>Pro</span>",
        "header.subtitle": "Intelligent Thesis Formatting Checker, Khon Kaen University",
        "banner.warning": "⚠️ The system may contain AI errors. Please always cross-reference with the MBA manual and advisor feedback.",
        "sidebar.howToUse": "How to Use",
        "sidebar.step1": "<strong>Upload Document:</strong> Upload your document files (.docx only) into the system by separating them into the 5 designated slots (e.g., Front Matter, Main Content, References).",
        "sidebar.step2": "<strong>Processing:</strong> Click the \"Analyze\" button. The system will deeply scan and analyze your document for structural formats (Hard Rules) and contextual content (AI) within seconds.",
        "sidebar.step3": "<strong>Review & Revise:</strong> The system will display the analysis results, pointing out errors clearly (e.g., margin violations, misalignments, typos). Users can apply these suggestions immediately to the original document.",
        "sidebar.warningTitle": "⚠️ Disclaimer",
        "sidebar.warningText": "Please verify the accuracy with your advisor. This system serves only as a preliminary screening assistant.",
        "upload.title": "Document Upload (5 Slots)",
        "upload.slot1Title": "Front Matter",
        "upload.slot1Sub": "Cover, Title Page, Approval Sheet, Acknowledgements",
        "upload.slot2Title": "Abstract",
        "upload.slot2Sub": "Thai and English Abstracts",
        "upload.slot3Title": "Table of Contents",
        "upload.slot3Sub": "Main TOC, List of Tables, List of Figures",
        "upload.slot4Title": "Main Content",
        "upload.slot4Sub": "Chapters 1-5 Core Thesis Content",
        "upload.slot5Title": "References",
        "upload.slot5Sub": "APA 7th Edition Reference List",
        "upload.ch1Title": "Chapter 1: Introduction",
        "upload.ch2Title": "Chapter 2: Literature Review",
        "upload.ch3Title": "Chapter 3: Methodology",
        "upload.ch4Title": "Chapter 4: Results",
        "upload.ch5Title": "Chapter 5: Conclusion",
        "upload.dragDrop1": "Drag file here or click to upload",
        "upload.dragDrop2": "Upload Chapter 1",
        "upload.dragDrop3": "Upload Chapter 2",
        "upload.dragDrop4": "Upload Chapter 3",
        "upload.dragDrop5": "Upload Chapter 4",
        "upload.dragDrop6": "Upload Chapter 5",
        "upload.statusPending": "⏳ Pending",
        "btn.scan1": "🔍 Analyze Front Matter",
        "btn.scan2": "🔍 Analyze Abstract",
        "btn.scan3": "🔍 Analyze TOC",
        "btn.scan4_1": "🔍 Analyze Chapter 1",
        "btn.scan4_2": "🔍 Analyze Chapter 2",
        "btn.scan4_3": "🔍 Analyze Chapter 3",
        "btn.scan4_4": "🔍 Analyze Chapter 4",
        "btn.scan4_5": "🔍 Analyze Chapter 5",
        "btn.scan5": "🔍 Analyze References",
        "insights.title": "AI Analysis & Cross-Check",
        "insights.citationTitle": "🔗 Citation Cross-Check",
        "insights.citationEmpty": "Upload Slot 4 (Content) and Slot 5 (References)<br>to enable citation cross-checking.",
        "insights.aiTitle": "🤖 AI Analysis Summary",
        "insights.aiEmpty": "AI analysis results will appear here<br>after uploading each document slot.",
        "footer.text": "© 2026 MBA IS AI Checker Pro — <a href='https://mba.kku.ac.th' target='_blank'>College of Graduate Study in Management, KKU</a>",
        "modal.checklistTitle": "Full Error Checklist",
        "modal.aiWarning": "Caution: AI verification results and suggestions may be inaccurate or change across multiple scans. Please use your discretion when applying these changes.",
        "modal.empty": "No analysis results yet",
        "disclaimer.title": "System Usage Warning",
        "disclaimer.text1": "Do not rely on the system 100%. AI processing and data extraction may technically have inaccuracies or fail (AI Error).",
        "disclaimer.text2": "This system is merely a <strong>preliminary screening assistant</strong>. Students must strictly adhere to the <strong>\"MBA Thesis/Independent Study Formatting Guidelines\"</strong> and always seek final approval from their advisor and the university's format checker.",
        "disclaimer.btn": "I Understand and Accept"
    }
};

function changeLanguage(lang) {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {
            el.innerHTML = translations[lang][key];
        }
    });
    
    // Handle inputs or placeholders if any, currently we just have innerHTML
    localStorage.setItem('appLang', lang);
    
    // Update the toggle button visually
    const langToggle = document.getElementById('lang-toggle');
    if (langToggle) {
        if (lang === 'en') {
            langToggle.querySelector('.lang-th').style.opacity = '0.4';
            langToggle.querySelector('.lang-en').style.opacity = '1';
        } else {
            langToggle.querySelector('.lang-th').style.opacity = '1';
            langToggle.querySelector('.lang-en').style.opacity = '0.4';
        }
    }
}

// Initializing Language
(function initLanguage() {
    const savedLang = localStorage.getItem('appLang') || 'th';
    // Run immediately before DOMContentLoaded to prevent flicker where possible
    document.addEventListener('DOMContentLoaded', () => {
        changeLanguage(savedLang);

        const langToggle = document.getElementById('lang-toggle');
        if (langToggle) {
            langToggle.addEventListener('click', () => {
                const currentLang = localStorage.getItem('appLang') === 'en' ? 'th' : 'en';
                changeLanguage(currentLang);
            });
        }
    });
})();
