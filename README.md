# ระบบติดตามการกัดเซาะชายฝั่งและดินเลนงอก จ.นครศรีธรรมราช
### Nakhon Si Thammarat Coastal Erosion & Mudflat Accretion Dashboard
**โครงการฟื้นฟูป่าชายเลนเพื่อประโยชน์จากคาร์บอนเครดิต (T-VER Premium)**  
แปลงปลูก **22-VSD (300.64 ไร่)** และ **23-VSD (200.12 ไร่)** ต.ท่าศาลา อ.ท่าศาลา จ.นครศรีธรรมราช

---

## 🌟 จุดเด่นของระบบ (Highlights)
1. **Interactive Swipe Slider บนแผนที่จริง (OpenStreetMap & Esri World Imagery)**:
   - แถบเลื่อนเปรียบเทียบภาพก่อนปลูก (เม.ย. 2566) vs หลังปลูก (เม.ย. 2569) และภาพถ่ายโดรนความละเอียดสูง
   - ความเร็วลื่นไหลระดับ 60/120 FPS ด้วย Hardware GPU Acceleration (`requestAnimationFrame`, `will-change: clip-path`)
   - ระบบซูมเข้า-ออกอย่างอิสระด้วย Mouse Scroll Wheel และปุ่ม Fullscreen เต็มจอ
2. **Sentinel-2 L2A 4x Super-Resolution (2.5m Ground Sampling Distance)**:
   - สกัดภาพดาวเทียมจริง 4 แบนด์ `[Red, Green, Blue, NIR]` ผ่าน Sentinel-2 COG STAC API
   - Display stretch 1%-99% แบบควบคุมคอนทราสต์เที่ยงตรง
   - คลุมพื้นที่แบบกว้าง (Wide Footprint: 3.84 km × 3.84 km) ครอบคลุมกรอบแปลงทั้งหมด 100%
3. **บูรณาการภาพถ่ายโดรนความละเอียดสูงระดับเซนติเมตร (UAV Drone Orthomosaic 2.6 cm/px)**:
   - ประมวลผลจากภาพสำรวจทางอากาศความละเอียดสูง 92,070 × 72,286 พิกเซล
   - ซ้อนทับพิกัด GIS จริงบนแปลง 22-VSD และ 23-VSD มองเห็นต้นกล้าโกงกาง แนวหลักไม้ และร่องน้ำเลนงอกรายต้น
4. **การวิเคราะห์การกัดเซาะและดินงอกเชิงปริมาณ (Coastal Erosion & Accretion Analysis)**:
   - เป็นไปตามมาตรฐาน **Coastal Erosion & Accretion Skill** อย่างเคร่งครัด
   - คำนวณจาก Native Analytical Sentinel-2 (10m) โดยไม่ใช้ Super-Resolution ในการวัดเชิงปริมาณ (Decoupled Policy)
   - วางแนวสำรวจ Transects 44 แนวเส้น ห่างกันทุก 50 เมตร ตั้งฉากกับแนวชายฝั่ง
   - ควบคุมอิทธิพลน้ำขึ้นน้ำลง (Tide & Season Matching) และคำนวณงบประมาณความคลาดเคลื่อน $U_{total} = \pm 11.18$ เมตร

---

## 📊 ผลการวิเคราะห์หลัก (Executive Summary)

| ตัวชี้วัด | ผลลัพธ์ที่คำนวณได้ | หมายเหตุ / ระเบียบวิธี |
| :--- | :---: | :--- |
| **พื้นที่แปลงปลูกตามสัญญา** | **500.76 ไร่** | แปลง 22-VSD (300.64) + 23-VSD (200.12) |
| **จำนวนกล้าไม้ปลูกสะสม** | **356,045 ต้น/ฝัก** | โกงกางใบใหญ่ 92.7%, เล็ก 5.6%, แสมขาว 1.7% |
| **ระยะ Waterline รุกทะเล (NSM)** | **+121.82 เมตร** | สังเกตการรุกออกทะเลของแนวเส้นน้ำ (สูงสุด +280.0 ม.) |
| **อัตราการรุกออกทะเล (EPR)** | **+40.61 ม./ปี** | End Point Rate ข้าม 3 ปี (เม.ย. 2566 - เม.ย. 2569) |
| **การขยับแนวป่าชายเลน (Mangrove Edge)** | **+635.45 เมตร** | แนวเรือนยอดไม้จริง (NDVI $\ge 0.35$) ไม่ขึ้นกับน้ำขึ้นน้ำลง |
| **พื้นที่ดินเลนงอกสุทธิ (Accretion)** | **+226.0 ไร่** | การสูญเสียชายฝั่งจากการกัดเซาะ = 0.0 ไร่ |
| **การขยายตัวของเรือนยอดไม้** | **+741.5 ไร่** | บริเวณโครงการ (Mean NDVI เพิ่มจาก 0.21 สู่ 0.58) |
| **งบประมาณความคลาดเคลื่อน ($U_{total}$)** | **$\pm 11.18$ เมตร** | รวมความคลาดเคลื่อน Grid (10m) + Coreg (3m) + Threshold (4m) |

---

## 📂 โครงสร้างโฟลเดอร์โครงการ

```text
corrosion-gemini/
├── .github/
│   └── workflows/
│       └── deploy-pages.yml       # GitHub Actions deploy to GitHub Pages
├── config/
│   └── superres/                  # ค่าพารามิเตอร์ Sentinel-2 และพิกัดแปลง
├── data/
│   ├── aoi/                       # ขอบเขตแปลง GeoJSON / Shapefiles
│   └── drone/                     # ไฟล์ภาพถ่ายโดรน
├── outputs/
│   └── superres/nakhon/           # ภาพดาวเทียม GeoTIFF 4 แบนด์ และแบบกว้าง 384x384
├── raw/                           # ทะเบียนคุมกล้าไม้ และเอกสารตรวจรับงาน
├── scripts/
│   ├── coastal_change_analysis.py # ไปป์ไลน์คำนวณการกัดเซาะและดินงอกรายแนวเส้น
│   ├── process_drone_ortho.py     # ไปป์ไลน์แปลงภาพถ่ายโดรนเป็น Web-Optimized Pyramidal Asset
│   └── superres/                  # สคริปต์ดึง Sentinel-2 COG และสร้าง WebP
├── skills/
│   └── coastal-erosion-accretion/ # ข้อกำหนดมาตรฐานการวิเคราะห์ชายฝั่ง
└── web/                           # แอปพลิเคชัน Dashboard (HTML5 / Tailwind / Leaflet / Chart.js)
    ├── index.html                 # หน้าหลัก Dashboard
    ├── src/
    │   ├── app.js                 # แอปลอจิก Dual-Map Slider และ GIS Controls
    │   └── styles.css             # สไตล์ CSS และการเร่งความเร็วกราฟิก GPU
    └── public/data/               # ข้อมูล GeoJSON, WebP, Drone Orthomosaic, และ JSON Metrics
```

---

## 🚀 การเปิดใช้งานแบบ Local (Local Development)

```bash
# 1. Clone repository
git clone https://github.com/saratchai1/corrosion-gemini.git
cd corrosion-gemini

# 2. รัน Local HTTP Server
python3 -m http.server 8080 --directory web

# 3. เปิดเว็บเบราว์เซอร์
# เข้าใช้งานที่: http://localhost:8080/
```

---

## 📜 การปฏิบัติตามมาตรฐานคู่มือทักษะ (Skills Compliance)
- **Sentinel-2 Super-Resolution Skill**:
  - ใช้ Display stretch 1%-99% percentile ขจัด contrast bias
  - ใช้งานภาพ Super-Resolution เฉพาะในมิติการสังเกตการณ์เชิงสายตา (Visual Layer)
- **Coastal Erosion & Accretion Skill**:
  - การคำนวณระยะการรุกตัว (NSM/EPR) คำนวณจาก **Native Sentinel-2 10m** เท่านั้น
  - ควบคุมระดับน้ำขึ้นน้ำลงด้วยการเทียบภาพถ่ายช่วงเวลาเดียวกันของปีและเวลาเดียวกันของวัน (~10:35 น. เวลาท้องถิ่น)
  - ไม่ใช้สูตรดึงระดับน้ำสมมุติ ($dx = dh / \tan\beta$) กับหาดเลนงอก เพื่อป้องกัน pseudo-correction error ตามมาตรฐาน Phase 4

---

## 👨‍💻 ผู้พัฒนา
- **โครงการฟื้นฟูป่าชายเลนเพื่อประโยชน์จากคาร์บอนเครดิต จ.นครศรีธรรมราช**
