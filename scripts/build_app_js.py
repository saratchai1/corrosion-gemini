import sys

code = '''// Multi-Province JavaScript Application for Coastal Erosion & Accretion Monitoring
// Supporting: Nakhon Si Thammarat (ท่าศาลา) & Phang Nga (อ่าวพังงา)
// Compliant with sentinel-2-super-resolution and coastal-erosion-accretion skills
// Features: Dual-Map Swipe Slider, Drone Orthomosaics, GeoJSON Plots, DSAS Transects, Dynamic KPIs & Multi-Province Switching

document.addEventListener('DOMContentLoaded', async () => {
  // DOM Elements
  const headerProvinceTitle = document.getElementById('headerProvinceTitle');
  const headerSubtitle = document.getElementById('headerSubtitle');
  const provBtnNakhon = document.getElementById('provBtnNakhon');
  const provBtnPhangnga = document.getElementById('provBtnPhangnga');

  const kpiAreaVal = document.getElementById('kpiAreaVal');
  const kpiAreaSub = document.getElementById('kpiAreaSub');
  const kpiTreesVal = document.getElementById('kpiTreesVal');
  const kpiTreesSub = document.getElementById('kpiTreesSub');
  const kpiAccretionVal = document.getElementById('kpiAccretionVal');
  const kpiAccretionSub = document.getElementById('kpiAccretionSub');
  const kpiCanopyVal = document.getElementById('kpiCanopyVal');
  const kpiCanopySub = document.getElementById('kpiCanopySub');

  const skillDominantRegime = document.getElementById('skillDominantRegime');
  const skillWaterlineNsmVal = document.getElementById('skillWaterlineNsmVal');
  const skillWaterlineNsmSub = document.getElementById('skillWaterlineNsmSub');
  const skillWaterlineEprVal = document.getElementById('skillWaterlineEprVal');
  const skillWaterlineEprSub = document.getElementById('skillWaterlineEprSub');
  const skillMangroveAdvVal = document.getElementById('skillMangroveAdvVal');
  const skillMangroveAdvSub = document.getElementById('skillMangroveAdvSub');
  const skillNetAccretionVal = document.getElementById('skillNetAccretionVal');
  const skillNetAccretionSub = document.getElementById('skillNetAccretionSub');
  const skillUncertaintyVal = document.getElementById('skillUncertaintyVal');
  const skillUncertaintySub = document.getElementById('skillUncertaintySub');

  const sliderSectionCard = document.getElementById('sliderSectionCard');
  const fullscreenBtn = document.getElementById('fullscreenBtn');
  const fullscreenBtnText = document.getElementById('fullscreenBtnText');
  const compareModeTemporalBtn = document.getElementById('compareModeTemporalBtn');
  const compareModeResolutionBtn = document.getElementById('compareModeResolutionBtn');
  const temporalControls = document.getElementById('temporalControls');
  const resolutionControls = document.getElementById('resolutionControls');
  const temporalQualityControls = document.getElementById('temporalQualityControls');
  const plotSelector = document.getElementById('plotSelector');
  const leftDateSelector = document.getElementById('leftDateSelector');
  const rightDateSelector = document.getElementById('rightDateSelector');
  const singleDateSelector = document.getElementById('singleDateSelector');
  const temporalQualitySelector = document.getElementById('temporalQualitySelector');
  const basemapOsmBtn = document.getElementById('basemapOsmBtn');
  const basemapSatBtn = document.getElementById('basemapSatBtn');
  const bandTabBtns = document.querySelectorAll('.band-tab-btn');
  const toggleBoundaryBtn = document.getElementById('toggleBoundaryBtn');
  const boundaryBtnText = document.getElementById('boundaryBtnText');
  const viewportPlotLegend = document.getElementById('viewportPlotLegend');

  const swipeViewport = document.getElementById('swipeViewport');
  const sliderMapRightContainer = document.getElementById('sliderMapRight');
  const dividerLine = document.getElementById('dividerLine');
  const leftBadgeText = document.getElementById('leftBadgeText');
  const rightBadgeText = document.getElementById('rightBadgeText');

  const zoomInBtn = document.getElementById('zoomInBtn');
  const zoomOutBtn = document.getElementById('zoomOutBtn');
  const zoomResetBtn = document.getElementById('zoomResetBtn');
  const currentSceneTag = document.getElementById('currentSceneTag');
  const currentStretchTag = document.getElementById('currentStretchTag');
  const recenterMapBtn = document.getElementById('recenterMapBtn');
  const toggleTransectsBtn = document.getElementById('toggleTransectsBtn');
  const toggleBottomDroneBtn = document.getElementById('toggleBottomDroneBtn');
  const bottomDroneBtnText = document.getElementById('bottomDroneBtnText');
  const transectsTableBody = document.getElementById('transectsTableBody');
  const seedlingRegistryBody = document.getElementById('seedlingRegistryBody');
  const seedlingNotesCard = document.getElementById('seedlingNotesCard');

  // Province Configurations
  const PROVINCES = {
    nakhon: {
      id: 'nakhon',
      name: 'นครศรีธรรมราช',
      headerTitle: 'นครศรีธรรมราช • การติดตามการกัดเซาะและดินงอก <span class="text-xs font-semibold px-2 py-0.5 rounded-full bg-mangrove-500/20 text-mangrove-300 border border-mangrove-500/30">ป่าชายเลน T-VER</span>',
      subtitle: 'แปลง 22-VSD & 23-VSD (500.76 ไร่) ต.ท่าศาลา | 4x Super-Resolution & Coastal Dynamics',
      center: [8.59478, 100.00268],
      zoom: 15,
      sentinelBounds: [
        [8.57549576268467, 99.98614806906022],
        [8.610315197158018, 100.02113228300021]
      ],
      droneBounds: [
        [8.582890337166464, 99.99030342802266],
        [8.602868743932794, 100.01715564698156]
      ],
      initialBounds: [
        [8.582890337166464, 99.99030342802266],
        [8.602868743932794, 100.01715564698156]
      ],
      kpis: {
        areaVal: '500.76',
        areaSub: '<i class="fa-solid fa-shield-check"></i> แปลง 22-VSD (300.64) + 23-VSD (200.12)',
        treesVal: '356,045',
        treesSub: '<i class="fa-solid fa-leaf text-mangrove-400"></i> โกงกางใหญ่ 92.7% • เล็ก 5.6% • แสม 1.7%',
        accretionVal: '+226.0',
        accretionSub: '<i class="fa-solid fa-arrow-trend-up"></i> รุกออกทะเลเฉลี่ย +40.61 ม./ปี',
        canopyVal: '+741.5',
        canopySub: '<i class="fa-solid fa-arrow-up"></i> Mean NDVI เพิ่มจาก 0.21 สู่ 0.58'
      },
      skillMetrics: {
        regime: '<i class="fa-solid fa-circle-check mr-1"></i> Dominant Regime: Apparent Accretion & Mangrove Advance',
        waterlineNsm: '+121.82 <span class="text-xs text-slate-400 font-normal">เมตร</span>',
        waterlineNsmSub: 'สูงสุด +280.0 ม. (3 ปี)',
        waterlineEpr: '+40.61 <span class="text-xs text-slate-400 font-normal">ม./ปี</span>',
        waterlineEprSub: 'End Point Rate 2023-2026',
        mangroveAdv: '+635.45 <span class="text-xs text-slate-400 font-normal">เมตร</span>',
        mangroveAdvSub: 'Mangrove Edge Advance Proxy',
        netAccretion: '+226.0 <span class="text-xs text-slate-400 font-normal">ไร่</span>',
        netAccretionSub: 'การกัดเซาะ: 0.0 ไร่',
        uncertainty: '&plusmn;11.18 <span class="text-xs text-slate-400 font-normal">เมตร</span>',
        uncertaintySub: 'U_grid(10m) + U_coreg(3m) + U_thresh(4m)'
      },
      plotsGeoJsonUrl: 'public/data/nakhon_plots_combined.geojson',
      metricsJsonUrl: 'public/data/coastal_metrics.json',
      transectsGeoJsonUrl: 'public/data/coastal_transects.geojson',
      chartData: {
        labels: ['เม.ย. 2566 (ก่อนปลูก)', 'เม.ย. 2567 (1 ปี)', 'เม.ย. 2569 (3 ปี)'],
        accretion: [0, 2.1, 226.0],
        ndvi: [0.21, 0.39, 0.58]
      },
      plotOptions: [
        { value: 'combined-vsd', label: 'ภาพรวม 22 & 23-VSD (500 ไร่)' },
        { value: '22-vsd', label: 'แปลง 22-VSD (300.64 ไร่)' },
        { value: '23-vsd', label: 'แปลง 23-VSD (200.12 ไร่)' },
        { value: 'drone-area', label: '🛸 ขอบเขตภาพถ่ายโดรน (UAV)' }
      ],
      temporalDates: {
        left: [
          { value: '2023-04-06', label: 'เม.ย. 2566 (ก่อนปลูก - Baseline)' },
          { value: '2024-04-05', label: 'เม.ย. 2567 (1 ปีหลังปลูก)' },
          { value: 'drone-2024', label: '🛸 ภาพโดรนเดิม (มิ.ย. 2567)' },
          { value: '2026-04-05', label: 'เม.ย. 2569 (3 ปี - ปัจจุบัน)' }
        ],
        right: [
          { value: 'drone-2026', label: '🛸 ภาพโดรนใหม่ เม.ย. 2569 (UAV ล่าสุด)' },
          { value: 'drone-2024', label: '🛸 ภาพโดรนเดิม มิ.ย. 2567 (UAV 2024)' },
          { value: '2026-04-05', label: 'ดาวเทียม เม.ย. 2569 (3 ปี - ปัจจุบัน)' },
          { value: '2024-04-05', label: 'ดาวเทียม เม.ย. 2567 (1 ปีหลังปลูก)' }
        ],
        defaultLeft: '2023-04-06',
        defaultRight: 'drone-2026'
      },
      resolutionDates: [
        { value: 'drone-2026', label: '🛸 ภาพโดรนใหม่ เม.ย. 2569 (UAV 2026)' },
        { value: 'drone-2024', label: '🛸 ภาพโดรนเดิม มิ.ย. 2567 (UAV 2024)' },
        { value: '2026-04-05', label: 'ปี 2569 (3 ปีหลังปลูก - ปัจจุบัน)' },
        { value: '2024-04-05', label: 'ปี 2567 (1 ปีหลังปลูก)' },
        { value: '2023-04-06', label: 'ปี 2566 (ก่อนเริ่มปลูก - Baseline)' }
      ],
      defaultSingleDate: 'drone-2026',
      dateLabels: {
        '2023-04-06': 'ก่อนเริ่มปลูก (เม.ย. 2566)',
        '2024-04-05': 'หลังปลูก 1 ปี (เม.ย. 2567)',
        '2026-04-05': 'หลังปลูก 3 ปี (เม.ย. 2569)',
        'drone-2024': '🛸 ภาพโดรนเดิม มิ.ย. 2567 (UAV 2024)',
        'drone-2026': '🛸 ภาพโดรนใหม่ เม.ย. 2569 (UAV ล่าสุด)'
      },
      seedlingRowsHtml: `
        <tr class="hover:bg-slate-800/30 transition">
          <td class="py-3 px-3 font-semibold text-white">22-VSD</td>
          <td class="py-3 px-3">300.64</td>
          <td class="py-3 px-3"><span class="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800/50">พื้นที่เลนงอก</span></td>
          <td class="py-3 px-3">โกงกางใบใหญ่ (200k), เล็ก (10k), แสมขาว (3.7k)</td>
          <td class="py-3 px-3 font-mono text-right font-medium text-white">213,757</td>
          <td class="py-3 px-3 text-center text-slate-400">29 พ.ค. 2566</td>
        </tr>
        <tr class="hover:bg-slate-800/30 transition">
          <td class="py-3 px-3 font-semibold text-white">23-VSD</td>
          <td class="py-3 px-3">200.12</td>
          <td class="py-3 px-3"><span class="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800/50">พื้นที่เลนงอก</span></td>
          <td class="py-3 px-3">โกงกางใบใหญ่ (130k), เล็ก (10k), แสมขาว (2.3k)</td>
          <td class="py-3 px-3 font-mono text-right font-medium text-white">142,288</td>
          <td class="py-3 px-3 text-center text-slate-400">29 พ.ค. 2566</td>
        </tr>
        <tr class="bg-slate-800/40 font-semibold text-white">
          <td class="py-3 px-3">รวมทั้งโครงการ</td>
          <td class="py-3 px-3 text-emerald-400">500.76</td>
          <td class="py-3 px-3">พื้นที่เลนงอก</td>
          <td class="py-3 px-3 text-slate-300">รวม 3 ชนิดพันธุ์หลัก + เสริมซ่อมบำรุง</td>
          <td class="py-3 px-3 font-mono text-right text-mangrove-300">356,045</td>
          <td class="py-3 px-3 text-center text-slate-300">-</td>
        </tr>
      `,
      seedlingNotesHtml: `
        <p class="font-medium text-sky-300 flex items-center gap-1.5">
          <i class="fa-solid fa-circle-check"></i> บันทึกการปลูกเสริมและซ่อมบำรุงแปลง 22-VSD:
        </p>
        <p class="text-slate-400 text-[11px]">
          • วันที่ 7 ก.ค. 2569: ปลูกเสริมโกงกางใบใหญ่ (ฝัก) จำนวน 7,104 ฝัก เพื่อเพิ่มความหนาแน่นบริเวณร่องเลน<br>
          • วันที่ 20 ก.ค. 2569: ปลูกเสริมโกงกางใบใหญ่ (ฝัก) จำนวน 7,104 ฝัก เพื่อเสริมแนวชะลอคลื่นชายฝั่ง
        </p>
      `
    },
    phangnga: {
      id: 'phangnga',
      name: 'พังงา (อ่าวพังงา)',
      headerTitle: 'พังงา (อ่าวพังงา) • การติดตามการกัดเซาะและดินงอก <span class="text-xs font-semibold px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">ป่าชายเลน T-VER</span>',
      subtitle: 'แปลง 40-VSD, 41-VSD & 42-VSD (699.49 ไร่) เกาะไม้ไผ่-เกาะปันหยี | 4x Super-Resolution & Coastal Dynamics',
      center: [8.35357, 98.54107],
      zoom: 14,
      sentinelBounds: [
        [8.336225340897428, 98.52360840989306],
        [8.370998958976356, 98.55852457482966]
      ],
      droneBounds: [
        [8.3443621884707, 98.5332164885241],
        [8.363022067475319, 98.55320496491346]
      ],
      droneBounds40_1: [
        [8.349952303062057, 98.55018184554493],
        [8.353712508600562, 98.55320496491346]
      ],
      droneBounds40_2: [
        [8.3443621884707, 98.5494316079051],
        [8.349004416111159, 98.55291785728623]
      ],
      droneBounds41: [
        [8.352259809416694, 98.5332164885241],
        [8.363022067475319, 98.54037638971805]
      ],
      initialBounds: [
        [8.34465182, 98.52958611],
        [8.36248309, 98.5525505]
      ],
      kpis: {
        areaVal: '699.49',
        areaSub: '<i class="fa-solid fa-shield-check"></i> แปลง 40 (289.11) + 41 (181.50) + 42 (228.88)',
        treesVal: '235,539',
        treesSub: '<i class="fa-solid fa-leaf text-cyan-400"></i> โกงกางใหญ่ 48.8% • เล็ก 32.3% • ถั่ว/จิก/โปรง 18.9%',
        accretionVal: '+36.1',
        accretionSub: '<i class="fa-solid fa-arrow-trend-up"></i> แนวสันทรายเลนงอกเฉลี่ย +12.43 ม./ปี',
        canopyVal: '+13.3',
        canopySub: '<i class="fa-solid fa-arrow-up"></i> Mean NDVI เพิ่มจาก 0.28 สู่ 0.62'
      },
      skillMetrics: {
        regime: '<i class="fa-solid fa-circle-check mr-1"></i> Dominant Regime: Apparent Accretion & Mangrove Expansion',
        waterlineNsm: '+37.28 <span class="text-xs text-slate-400 font-normal">เมตร</span>',
        waterlineNsmSub: 'สูงสุด +92.5 ม. (3 ปี)',
        waterlineEpr: '+12.43 <span class="text-xs text-slate-400 font-normal">ม./ปี</span>',
        waterlineEprSub: 'End Point Rate 2023-2026',
        mangroveAdv: '+48.15 <span class="text-xs text-slate-400 font-normal">เมตร</span>',
        mangroveAdvSub: 'Mangrove Edge Advance Proxy',
        netAccretion: '+36.1 <span class="text-xs text-slate-400 font-normal">ไร่</span>',
        netAccretionSub: 'การกัดเซาะ: 0.0 ไร่',
        uncertainty: '&plusmn;11.18 <span class="text-xs text-slate-400 font-normal">เมตร</span>',
        uncertaintySub: 'U_grid(10m) + U_coreg(3m) + U_thresh(4m)'
      },
      plotsGeoJsonUrl: 'public/data/phangnga/phangnga_plots_combined.geojson',
      metricsJsonUrl: 'public/data/phangnga/coastal_metrics.json',
      transectsGeoJsonUrl: 'public/data/phangnga/coastal_transects.geojson',
      chartData: {
        labels: ['เม.ย. 2566 (ก่อนปลูก)', 'มี.ค. 2567 (1 ปี)', 'มี.ค. 2569 (3 ปี)'],
        accretion: [0, 11.2, 36.1],
        ndvi: [0.28, 0.44, 0.62]
      },
      plotOptions: [
        { value: 'combined-vsd', label: 'ภาพรวมแปลง 40, 41, 42-VSD (699.49 ไร่)' },
        { value: '40-vsd', label: 'แปลง 40-VSD (289.11 ไร่ เกาะไม้ไผ่)' },
        { value: '41-vsd', label: 'แปลง 41-VSD (181.50 ไร่ เกาะปันหยี)' },
        { value: '42-vsd', label: 'แปลง 42-VSD (228.88 ไร่ อ่าวพังงา)' },
        { value: 'drone-area-40-1', label: '🛸 ขอบเขตโดรน 40-VSD เหนือ' },
        { value: 'drone-area-40-2', label: '🛸 ขอบเขตโดรน 40-VSD ใต้' },
        { value: 'drone-area-41', label: '🛸 ขอบเขตโดรน 41-VSD เกาะปันหยี' }
      ],
      temporalDates: {
        left: [
          { value: '2023-04-11', label: 'เม.ย. 2566 (ก่อนปลูก - Baseline)' },
          { value: '2024-03-19', label: 'มี.ค. 2567 (1 ปีหลังปลูก)' },
          { value: '2026-03-21', label: 'มี.ค. 2569 (3 ปี - ปัจจุบัน)' }
        ],
        right: [
          { value: 'drone-phangnga-40-1', label: '🛸 โดรน 40-VSD เหนือ (เกาะไม้ไผ่)' },
          { value: 'drone-phangnga-40-2', label: '🛸 โดรน 40-VSD ใต้ (เกาะไม้ไผ่)' },
          { value: 'drone-phangnga-41', label: '🛸 โดรน 41-VSD (เกาะปันหยี)' },
          { value: '2026-03-21', label: 'ดาวเทียม มี.ค. 2569 (3 ปี - ปัจจุบัน)' },
          { value: '2024-03-19', label: 'ดาวเทียม มี.ค. 2567 (1 ปีหลังปลูก)' }
        ],
        defaultLeft: '2023-04-11',
        defaultRight: 'drone-phangnga-40-1'
      },
      resolutionDates: [
        { value: 'drone-phangnga-40-1', label: '🛸 โดรน 40-VSD เหนือ (เกาะไม้ไผ่)' },
        { value: 'drone-phangnga-40-2', label: '🛸 โดรน 40-VSD ใต้ (เกาะไม้ไผ่)' },
        { value: 'drone-phangnga-41', label: '🛸 โดรน 41-VSD (เกาะปันหยี)' },
        { value: '2026-03-21', label: 'ปี 2569 (3 ปีหลังปลูก - ปัจจุบัน)' },
        { value: '2024-03-19', label: 'ปี 2567 (1 ปีหลังปลูก)' },
        { value: '2023-04-11', label: 'ปี 2566 (ก่อนเริ่มปลูก - Baseline)' }
      ],
      defaultSingleDate: 'drone-phangnga-40-1',
      dateLabels: {
        '2023-04-11': 'ก่อนเริ่มปลูก (เม.ย. 2566)',
        '2024-03-19': 'หลังปลูก 1 ปี (มี.ค. 2567)',
        '2026-03-21': 'หลังปลูก 3 ปี (มี.ค. 2569)',
        'drone-phangnga-40-1': '🛸 โดรน 40-VSD เหนือ (เกาะไม้ไผ่)',
        'drone-phangnga-40-2': '🛸 โดรน 40-VSD ใต้ (เกาะไม้ไผ่)',
        'drone-phangnga-41': '🛸 โดรน 41-VSD (เกาะปันหยี)'
      },
      seedlingRowsHtml: `
        <tr class="hover:bg-slate-800/30 transition">
          <td class="py-3 px-3 font-semibold text-white">40-VSD</td>
          <td class="py-3 px-3">289.11</td>
          <td class="py-3 px-3"><span class="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800/50">ป่าเสื่อมโทรม/เลนงอก</span></td>
          <td class="py-3 px-3">โกงกางใหญ่ (50k), เล็ก (30k), ถั่วขาว/โปรง/จิก (3.2k)</td>
          <td class="py-3 px-3 font-mono text-right font-medium text-white">83,199</td>
          <td class="py-3 px-3 text-center text-slate-400">20 พ.ย. 2567</td>
        </tr>
        <tr class="hover:bg-slate-800/30 transition">
          <td class="py-3 px-3 font-semibold text-white">41-VSD</td>
          <td class="py-3 px-3">181.50</td>
          <td class="py-3 px-3"><span class="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800/50">เลนงอกเกาะปันหยี</span></td>
          <td class="py-3 px-3">โกงกางใหญ่ (15k), เล็ก (15k), ถั่วขาว (10k), โปรง/จิก (13.7k)</td>
          <td class="py-3 px-3 font-mono text-right font-medium text-white">53,676</td>
          <td class="py-3 px-3 text-center text-slate-400">25 พ.ย. 2567</td>
        </tr>
        <tr class="hover:bg-slate-800/30 transition">
          <td class="py-3 px-3 font-semibold text-white">42-VSD</td>
          <td class="py-3 px-3">228.88</td>
          <td class="py-3 px-3"><span class="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800/50">เลนงอกอ่าวพังงา</span></td>
          <td class="py-3 px-3">โกงกางใหญ่ (50k), เล็ก (31k), จิก (8.7k), โปรง/ถั่ว (9k)</td>
          <td class="py-3 px-3 font-mono text-right font-medium text-white">98,664</td>
          <td class="py-3 px-3 text-center text-slate-400">30 พ.ย. 2567</td>
        </tr>
        <tr class="bg-slate-800/40 font-semibold text-white">
          <td class="py-3 px-3">รวมทั้งโครงการ</td>
          <td class="py-3 px-3 text-cyan-400">699.49</td>
          <td class="py-3 px-3">เลนงอกและป่าเสื่อมโทรม</td>
          <td class="py-3 px-3 text-slate-300">รวม 5 ชนิดพันธุ์หลัก + ซ่อมบำรุง</td>
          <td class="py-3 px-3 font-mono text-right text-cyan-300">235,539</td>
          <td class="py-3 px-3 text-center text-slate-300">-</td>
        </tr>
      `,
      seedlingNotesHtml: `
        <p class="font-medium text-cyan-300 flex items-center gap-1.5">
          <i class="fa-solid fa-circle-check"></i> บันทึกการปลูกเสริมและซ่อมบำรุงแปลง จ.พังงา:
        </p>
        <p class="text-slate-400 text-[11px]">
          • แปลง 40-VSD (เกาะไม้ไผ่): ซ่อมบำรุงโกงกางใบใหญ่ 1,516 ฝัก (เม.ย. - มิ.ย. 2569)<br>
          • แปลง 41-VSD (เกาะปันหยี): ปลูกเสริมถั่วขาว 178 ต้น เพื่อรักษาแนวดักตะกอน (มี.ค. - มิ.ย. 2569)<br>
          • แปลง 42-VSD: อัตราการรอดตายสูงกว่า 94% ไม่พบการชะล้างรุนแรง
        </p>
      `
    }
  };

  // Determine initial province from query param or hash, default to nakhon
  const urlParams = new URLSearchParams(window.location.search);
  let activeProvinceKey = (urlParams.get('province') || window.location.hash.replace('#', '')).toLowerCase();
  if (!PROVINCES[activeProvinceKey]) activeProvinceKey = 'nakhon';

  // Application State
  let currentProvince = PROVINCES[activeProvinceKey];
  let comparatorMode = 'temporal';
  let currentPlot = 'combined-vsd';
  let currentMode = 'rgb';
  let leftDate = currentProvince.temporalDates.defaultLeft;
  let rightDate = currentProvince.temporalDates.defaultRight;
  let singleDate = currentProvince.defaultSingleDate;
  let temporalQuality = '2p5m';
  let currentBasemap = 'osm';
  let showBoundaries = true;
  let showBottomDrone = true;
  let isFullscreen = false;
  let isDraggingDivider = false;

  // Leaflet Layer References
  let plotGeoJson = null;
  let transectGeoJson = null;
  let coastalMetrics = null;

  let plotLayerLeft = null;
  let plotLayerRight = null;
  let bottomPlotLayer = null;
  let transectsLayer = null;
  let individualPlotBounds = {};

  // Basemap Tile URLs
  const OSM_TILE_URL = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
  const ESRI_TILE_URL = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';

  // 1. Initialize Dual Leaflet Slider Maps
  const mapLeft = L.map('sliderMapLeft', {
    center: currentProvince.center,
    zoom: currentProvince.zoom,
    minZoom: 10,
    maxZoom: 20,
    zoomControl: false,
    attributionControl: false
  });

  const mapRight = L.map('sliderMapRight', {
    center: currentProvince.center,
    zoom: currentProvince.zoom,
    minZoom: 10,
    maxZoom: 20,
    zoomControl: false,
    attributionControl: false
  });

  const tileLayerLeft = L.tileLayer(OSM_TILE_URL, { maxZoom: 20 }).addTo(mapLeft);
  const tileLayerRight = L.tileLayer(OSM_TILE_URL, { maxZoom: 20 }).addTo(mapRight);

  let overlayLeft = L.imageOverlay('', currentProvince.sentinelBounds, { opacity: 1.0 }).addTo(mapLeft);
  let overlayRight = L.imageOverlay('', currentProvince.sentinelBounds, { opacity: 1.0 }).addTo(mapRight);

  // Synchronize Dual Maps
  mapLeft.on('move', () => {
    mapRight.setView(mapLeft.getCenter(), mapLeft.getZoom(), { animate: false });
  });

  // 2. Initialize Bottom Leaflet Map
  const mapBottom = L.map('mapView', {
    center: currentProvince.center,
    zoom: currentProvince.zoom,
    zoomControl: false
  });

  L.control.zoom({ position: 'bottomright' }).addTo(mapBottom);
  L.tileLayer(ESRI_TILE_URL, { attribution: 'Tiles &copy; Esri &mdash; Sentinel-2 L2A', maxZoom: 20 }).addTo(mapBottom);

  const bottomDroneGroup = L.layerGroup().addTo(mapBottom);

  // 3. Initialize Chart.js
  const ctx = document.getElementById('temporalChart').getContext('2d');
  const temporalChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: currentProvince.chartData.labels,
      datasets: [
        {
          label: 'ดินเลนงอกสะสม (ไร่)',
          data: currentProvince.chartData.accretion,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.15)',
          fill: true,
          tension: 0.35,
          yAxisID: 'yAcquisition',
          pointRadius: 4,
          pointHoverRadius: 6,
        },
        {
          label: 'ดัชนีเรือนยอด (NDVI)',
          data: currentProvince.chartData.ndvi,
          borderColor: '#38bdf8',
          backgroundColor: 'transparent',
          borderDash: [5, 5],
          tension: 0.35,
          yAxisID: 'yNDVI',
          pointRadius: 4,
          pointHoverRadius: 6,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          position: 'top',
          labels: { color: '#94a3b8', font: { family: 'Prompt', size: 10 }, boxWidth: 12 }
        },
        tooltip: {
          backgroundColor: '#0f172a',
          titleColor: '#f8fafc',
          bodyColor: '#cbd5e1',
          borderColor: '#334155',
          borderWidth: 1,
          padding: 10,
          titleFont: { family: 'Prompt' },
          bodyFont: { family: 'Prompt' }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(51, 65, 85, 0.3)' },
          ticks: { color: '#94a3b8', font: { family: 'Prompt', size: 10 } }
        },
        yAcquisition: {
          type: 'linear',
          display: true,
          position: 'left',
          grid: { color: 'rgba(51, 65, 85, 0.3)' },
          ticks: { color: '#10b981', font: { family: 'Prompt', size: 10 } },
          title: { display: true, text: 'ดินงอก (ไร่)', color: '#10b981', font: { family: 'Prompt', size: 10 } }
        },
        yNDVI: {
          type: 'linear',
          display: true,
          position: 'right',
          grid: { drawOnChartArea: false },
          ticks: { color: '#38bdf8', font: { family: 'Prompt', size: 10 } },
          title: { display: true, text: 'NDVI', color: '#38bdf8', font: { family: 'Prompt', size: 10 } }
        }
      }
    }
  });

  // Layer Resolution Logic
  function resolveLayer(key, modePrefix) {
    const isPhangnga = currentProvince.id === 'phangnga';

    if (key === 'drone-2026') {
      return {
        url: 'public/data/drone/drone_2026_04_hd.webp',
        bounds: currentProvince.droneBounds,
        badge: '🛸 ภาพโดรนใหม่ เม.ย. 2569 (UAV ล่าสุด)'
      };
    }
    if (key === 'drone-2024' || key === 'drone-ortho') {
      return {
        url: 'public/data/drone/drone_ortho_hd.webp',
        bounds: [
          [8.585914525682421, 99.99048684871822],
          [8.60302831899287, 100.01235991418478]
        ],
        badge: '🛸 ภาพโดรนเดิม มิ.ย. 2567 (UAV 2024)'
      };
    }
    if (key === 'drone-phangnga-40-1') {
      return {
        url: 'public/data/phangnga/drone/40-vsd_small1_hd.webp',
        bounds: currentProvince.droneBounds40_1,
        badge: '🛸 โดรน 40-VSD เหนือ (เกาะไม้ไผ่)'
      };
    }
    if (key === 'drone-phangnga-40-2') {
      return {
        url: 'public/data/phangnga/drone/40-vsd_small2_hd.webp',
        bounds: currentProvince.droneBounds40_2,
        badge: '🛸 โดรน 40-VSD ใต้ (เกาะไม้ไผ่)'
      };
    }
    if (key === 'drone-phangnga-41') {
      return {
        url: 'public/data/phangnga/drone/41-vsd_hd.webp',
        bounds: currentProvince.droneBounds41,
        badge: '🛸 โดรน 41-VSD (เกาะปันหยี)'
      };
    }

    const qLabel = temporalQuality === '2p5m' ? '4x SR (2.5m)' : 'Native (10m)';
    const dateLabel = currentProvince.dateLabels[key] || key;

    if (isPhangnga) {
      return {
        url: `public/data/phangnga/superres25/phangnga-${key}-${modePrefix}${temporalQuality}.webp`,
        bounds: currentProvince.sentinelBounds,
        badge: `${dateLabel} [${qLabel}]`
      };
    } else {
      return {
        url: `public/data/superres25/combined-vsd-${key}-${modePrefix}${temporalQuality}.webp`,
        bounds: currentProvince.sentinelBounds,
        badge: `${dateLabel} [${qLabel}]`
      };
    }
  }

  // Update Overlays
  function updateSliderOverlays() {
    let modePrefix = '';
    if (currentMode === 'cir') modePrefix = 'cir-';
    if (currentMode === 'ndvi') modePrefix = 'ndvi-';

    if (comparatorMode === 'temporal') {
      const leftConf = resolveLayer(leftDate, modePrefix);
      const rightConf = resolveLayer(rightDate, modePrefix);

      overlayLeft.setUrl(leftConf.url);
      overlayLeft.setBounds(leftConf.bounds);
      leftBadgeText.textContent = leftConf.badge;

      overlayRight.setUrl(rightConf.url);
      overlayRight.setBounds(rightConf.bounds);
      rightBadgeText.textContent = rightConf.badge;

      currentSceneTag.textContent = `เทียบ: ${leftConf.badge} vs ${rightConf.badge}`;
    } else {
      // Resolution Mode
      if (singleDate.startsWith('drone')) {
        const droneConf = resolveLayer(singleDate, modePrefix);
        const satDate = currentProvince.id === 'phangnga' ? '2026-03-21' : '2026-04-05';
        const satUrl = currentProvince.id === 'phangnga'
          ? `public/data/phangnga/superres25/phangnga-${satDate}-${modePrefix}2p5m.webp`
          : `public/data/superres25/combined-vsd-${satDate}-${modePrefix}2p5m.webp`;

        overlayLeft.setUrl(satUrl);
        overlayLeft.setBounds(currentProvince.sentinelBounds);
        leftBadgeText.textContent = 'ดาวเทียม Sentinel-2 (2.5m SR)';

        overlayRight.setUrl(droneConf.url);
        overlayRight.setBounds(droneConf.bounds);
        rightBadgeText.textContent = droneConf.badge;

        currentSceneTag.textContent = `เทียบ: ดาวเทียม 2.5m vs ${droneConf.badge}`;
      } else {
        const natUrl = currentProvince.id === 'phangnga'
          ? `public/data/phangnga/superres25/phangnga-${singleDate}-${modePrefix}10m.webp`
          : `public/data/superres25/combined-vsd-${singleDate}-${modePrefix}10m.webp`;
        const srUrl = currentProvince.id === 'phangnga'
          ? `public/data/phangnga/superres25/phangnga-${singleDate}-${modePrefix}2p5m.webp`
          : `public/data/superres25/combined-vsd-${singleDate}-${modePrefix}2p5m.webp`;

        overlayLeft.setUrl(natUrl);
        overlayLeft.setBounds(currentProvince.sentinelBounds);
        leftBadgeText.textContent = `Native 10m [${currentProvince.dateLabels[singleDate] || singleDate}]`;

        overlayRight.setUrl(srUrl);
        overlayRight.setBounds(currentProvince.sentinelBounds);
        rightBadgeText.textContent = `4x Super-Res 2.5m [${currentProvince.dateLabels[singleDate] || singleDate}]`;

        currentSceneTag.textContent = `Sentinel-2 L2A (${singleDate})`;
      }
    }

    if (currentMode === 'rgb') {
      currentStretchTag.textContent = 'RGB 1%-99% / UAV Drone Orthomosaic TrueColor';
    } else if (currentMode === 'cir') {
      currentStretchTag.textContent = 'CIR [NIR, Red, Green] 1%-99%';
    } else {
      currentStretchTag.textContent = 'NDVI (Brown: Mud/Water → Green: Mangrove)';
    }
  }

  // Populate UI Dropdowns for active province
  function populateDropdowns() {
    // Plot Selector
    plotSelector.innerHTML = '';
    currentProvince.plotOptions.forEach(opt => {
      const el = document.createElement('option');
      el.value = opt.value;
      el.textContent = opt.label;
      plotSelector.appendChild(el);
    });
    currentPlot = 'combined-vsd';

    // Temporal Left Selector
    leftDateSelector.innerHTML = '';
    currentProvince.temporalDates.left.forEach(opt => {
      const el = document.createElement('option');
      el.value = opt.value;
      el.textContent = opt.label;
      if (opt.value === currentProvince.temporalDates.defaultLeft) el.selected = true;
      leftDateSelector.appendChild(el);
    });
    leftDate = currentProvince.temporalDates.defaultLeft;

    // Temporal Right Selector
    rightDateSelector.innerHTML = '';
    currentProvince.temporalDates.right.forEach(opt => {
      const el = document.createElement('option');
      el.value = opt.value;
      el.textContent = opt.label;
      if (opt.value === currentProvince.temporalDates.defaultRight) el.selected = true;
      rightDateSelector.appendChild(el);
    });
    rightDate = currentProvince.temporalDates.defaultRight;

    // Resolution Selector
    singleDateSelector.innerHTML = '';
    currentProvince.resolutionDates.forEach(opt => {
      const el = document.createElement('option');
      el.value = opt.value;
      el.textContent = opt.label;
      if (opt.value === currentProvince.defaultSingleDate) el.selected = true;
      singleDateSelector.appendChild(el);
    });
    singleDate = currentProvince.defaultSingleDate;
  }

  // Populate Transects Table
  function populateTransectsTable(transects) {
    if (!transectsTableBody || !transects) return;
    transectsTableBody.innerHTML = '';
    const sample = transects.filter((_, idx) => idx % 4 === 0);
    sample.forEach(t => {
      const tr = document.createElement('tr');
      tr.className = 'hover:bg-slate-800/40 transition';
      const isAcc = (t.waterline_class || '').includes('ACCRETION');
      const badgeColor = isAcc 
        ? 'text-emerald-400 bg-emerald-950/60 border border-emerald-800/60' 
        : 'text-slate-400 bg-slate-800/60 border border-slate-700/60';

      tr.innerHTML = `
        <td class="py-2 px-3 font-semibold text-white">${t.id}</td>
        <td class="py-2 px-3 text-slate-400">${t.y_utm ? t.y_utm.toFixed(1) : '-'}</td>
        <td class="py-2 px-3 ${t.waterline_nsm_m >= 0 ? 'text-emerald-400' : 'text-red-400'} font-bold">
          ${t.waterline_nsm_m >= 0 ? '+' : ''}${t.waterline_nsm_m} m
        </td>
        <td class="py-2 px-3 text-slate-300">
          ${t.waterline_epr_m_yr >= 0 ? '+' : ''}${t.waterline_epr_m_yr} m/yr
        </td>
        <td class="py-2 px-3 text-sky-400">+${t.mangrove_nsm_m} m</td>
        <td class="py-2 px-3"><span class="px-2 py-0.5 rounded text-[10px] ${badgeColor}">${t.waterline_class}</span></td>
      `;
      transectsTableBody.appendChild(tr);
    });
  }

  // Set up Vector Plot Layers
  function setupPlotLayers() {
    if (plotLayerLeft) mapLeft.removeLayer(plotLayerLeft);
    if (plotLayerRight) mapRight.removeLayer(plotLayerRight);
    if (bottomPlotLayer) mapBottom.removeLayer(bottomPlotLayer);

    if (!plotGeoJson) return;

    individualPlotBounds = {};

    const plotStyle = (feature) => {
      const name = feature.properties.Name || feature.properties.plot_id || '';
      const isGreen = name.includes('22') || name.includes('40');
      return {
        color: isGreen ? '#10b981' : '#38bdf8',
        weight: 3,
        dashArray: '6, 6',
        fillColor: isGreen ? '#059669' : '#0284c7',
        fillOpacity: 0.15
      };
    };

    const onEachPlot = (feature, layer) => {
      const name = feature.properties.Name || feature.properties.plot_id || 'แปลงป่าชายเลน';
      const area = feature.properties.area_rai ? `${feature.properties.area_rai} ไร่` : '';
      layer.bindTooltip(`<strong>${name}</strong> ${area ? '(' + area + ')' : ''}`, {
        permanent: false,
        direction: 'center',
        className: 'bg-slate-900/90 text-white font-sans text-xs px-2 py-1 rounded border border-slate-700'
      });
    };

    plotLayerLeft = L.geoJSON(plotGeoJson, { style: plotStyle, onEachFeature: onEachPlot });
    plotLayerRight = L.geoJSON(plotGeoJson, { style: plotStyle, onEachFeature: onEachPlot });

    if (showBoundaries) {
      plotLayerLeft.addTo(mapLeft);
      plotLayerRight.addTo(mapRight);
    }

    // Cache individual plot bounds
    plotLayerLeft.eachLayer(layer => {
      const name = (layer.feature.properties.Name || layer.feature.properties.plot_id || '').toLowerCase();
      if (name.includes('22')) individualPlotBounds['22-vsd'] = layer.getBounds();
      if (name.includes('23')) individualPlotBounds['23-vsd'] = layer.getBounds();
      if (name.includes('40')) individualPlotBounds['40-vsd'] = layer.getBounds();
      if (name.includes('41')) individualPlotBounds['41-vsd'] = layer.getBounds();
      if (name.includes('42')) individualPlotBounds['42-vsd'] = layer.getBounds();
    });

    // Bottom Map Plots
    bottomPlotLayer = L.geoJSON(plotGeoJson, {
      style: (feature) => {
        const name = feature.properties.Name || feature.properties.plot_id || '';
        const isGreen = name.includes('22') || name.includes('40');
        return {
          color: isGreen ? '#10b981' : '#38bdf8',
          weight: 2.5,
          opacity: 0.9,
          fillColor: isGreen ? '#059669' : '#0284c7',
          fillOpacity: 0.2,
          dashArray: '4, 4'
        };
      },
      onEachFeature: (feature, layer) => {
        const name = feature.properties.Name || feature.properties.plot_id || 'แปลงป่าชายเลน';
        const area = feature.properties.area_rai || (name.includes('22') ? '300.64' : name.includes('23') ? '200.12' : '289.11');
        const provName = currentProvince.name;
        layer.bindPopup(`
          <div class="p-1 space-y-1 font-sans">
            <h4 class="font-bold text-sm text-white flex items-center gap-1.5">
              <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
              ${name}
            </h4>
            <p class="text-xs text-slate-300">จ.${provName}</p>
            <div class="border-t border-slate-700/60 pt-1.5 text-xs text-slate-300 space-y-0.5">
              <p><strong>เนื้อที่:</strong> ${area} ไร่</p>
              <p><strong>โครงการ:</strong> ปลูกป่าชายเลน T-VER คาร์บอนเครดิต</p>
            </div>
          </div>
        `);
      }
    }).addTo(mapBottom);
  }

  // Set up Transects Layer
  function setupTransectsLayer() {
    if (transectsLayer) mapBottom.removeLayer(transectsLayer);
    if (!transectGeoJson) return;

    transectsLayer = L.geoJSON(transectGeoJson, {
      style: () => ({ color: '#10b981', weight: 2, opacity: 0.8 }),
      onEachFeature: (feature, layer) => {
        const p = feature.properties;
        layer.bindPopup(`
          <div class="p-1 font-sans text-xs space-y-1">
            <h4 class="font-bold text-white flex items-center gap-1">
              <i class="fa-solid fa-ruler-horizontal text-emerald-400"></i>
              Transect ${p.id}
            </h4>
            <p><strong>Waterline Movement (NSM):</strong> <span class="text-emerald-400 font-bold">+${p.waterline_nsm_m} m</span></p>
            <p><strong>End Point Rate (EPR):</strong> +${p.waterline_epr_m_yr} m/yr</p>
            <p><strong>Mangrove Advance:</strong> +${p.mangrove_nsm_m} m</p>
            <p><strong>Status:</strong> <span class="text-emerald-300 font-semibold">${p.waterline_class}</span></p>
          </div>
        `);
      }
    });

    if (showTransects) mapBottom.addLayer(transectsLayer);
  }

  // Load Province Data & Refresh Entire Dashboard
  async function loadProvinceData(provKey) {
    currentProvince = PROVINCES[provKey];
    activeProvinceKey = provKey;

    // Update Header
    headerProvinceTitle.innerHTML = currentProvince.headerTitle;
    headerSubtitle.textContent = currentProvince.subtitle;

    // Update Province Switcher Buttons
    if (provKey === 'nakhon') {
      provBtnNakhon.className = 'province-btn active px-3.5 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5 text-white bg-mangrove-600 shadow-sm';
      provBtnPhangnga.className = 'province-btn px-3.5 py-1.5 rounded-lg font-medium transition flex items-center gap-1.5 text-slate-400 hover:text-white';
    } else {
      provBtnPhangnga.className = 'province-btn active px-3.5 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5 text-white bg-cyan-600 shadow-sm';
      provBtnNakhon.className = 'province-btn px-3.5 py-1.5 rounded-lg font-medium transition flex items-center gap-1.5 text-slate-400 hover:text-white';
    }

    // Update KPIs
    kpiAreaVal.textContent = currentProvince.kpis.areaVal;
    kpiAreaSub.innerHTML = currentProvince.kpis.areaSub;
    kpiTreesVal.textContent = currentProvince.kpis.treesVal;
    kpiTreesSub.innerHTML = currentProvince.kpis.treesSub;
    kpiAccretionVal.textContent = currentProvince.kpis.accretionVal;
    kpiAccretionSub.innerHTML = currentProvince.kpis.accretionSub;
    kpiCanopyVal.textContent = currentProvince.kpis.canopyVal;
    kpiCanopySub.innerHTML = currentProvince.kpis.canopySub;

    // Update Coastal Skill Metrics Grid
    if (skillDominantRegime) skillDominantRegime.innerHTML = currentProvince.skillMetrics.regime;
    if (skillWaterlineNsmVal) skillWaterlineNsmVal.innerHTML = currentProvince.skillMetrics.waterlineNsm;
    if (skillWaterlineNsmSub) skillWaterlineNsmSub.textContent = currentProvince.skillMetrics.waterlineNsmSub;
    if (skillWaterlineEprVal) skillWaterlineEprVal.innerHTML = currentProvince.skillMetrics.waterlineEpr;
    if (skillWaterlineEprSub) skillWaterlineEprSub.textContent = currentProvince.skillMetrics.waterlineEprSub;
    if (skillMangroveAdvVal) skillMangroveAdvVal.innerHTML = currentProvince.skillMetrics.mangroveAdv;
    if (skillMangroveAdvSub) skillMangroveAdvSub.textContent = currentProvince.skillMetrics.mangroveAdvSub;
    if (skillNetAccretionVal) skillNetAccretionVal.innerHTML = currentProvince.skillMetrics.netAccretion;
    if (skillNetAccretionSub) skillNetAccretionSub.textContent = currentProvince.skillMetrics.netAccretionSub;
    if (skillUncertaintyVal) skillUncertaintyVal.innerHTML = currentProvince.skillMetrics.uncertainty;
    if (skillUncertaintySub) skillUncertaintySub.textContent = currentProvince.skillMetrics.uncertaintySub;

    // Update Seedling Registry Table & Notes
    if (seedlingRegistryBody) seedlingRegistryBody.innerHTML = currentProvince.seedlingRowsHtml;
    if (seedlingNotesCard) seedlingNotesCard.innerHTML = currentProvince.seedlingNotesHtml;

    // Update Chart
    temporalChart.data.labels = currentProvince.chartData.labels;
    temporalChart.data.datasets[0].data = currentProvince.chartData.accretion;
    temporalChart.data.datasets[1].data = currentProvince.chartData.ndvi;
    temporalChart.update();

    // Populate Dropdowns
    populateDropdowns();

    // Update Bottom Drone Overlays in group
    bottomDroneGroup.clearLayers();
    if (provKey === 'nakhon') {
      bottomDroneGroup.addLayer(L.imageOverlay('public/data/drone/drone_2026_04_hd.webp', currentProvince.droneBounds, { opacity: 0.95 }));
    } else {
      bottomDroneGroup.addLayer(L.imageOverlay('public/data/phangnga/drone/40-vsd_small1_hd.webp', currentProvince.droneBounds40_1, { opacity: 0.95 }));
      bottomDroneGroup.addLayer(L.imageOverlay('public/data/phangnga/drone/40-vsd_small2_hd.webp', currentProvince.droneBounds40_2, { opacity: 0.95 }));
      bottomDroneGroup.addLayer(L.imageOverlay('public/data/phangnga/drone/41-vsd_hd.webp', currentProvince.droneBounds41, { opacity: 0.95 }));
    }

    // Update Slider Overlays
    updateSliderOverlays();

    // Fly Maps to Province
    mapLeft.fitBounds(currentProvince.initialBounds, { padding: [30, 30] });
    mapRight.setView(mapLeft.getCenter(), mapLeft.getZoom(), { animate: false });
    mapBottom.fitBounds(currentProvince.initialBounds, { padding: [20, 20] });

    // Fetch GeoJSON datasets for this province
    try {
      const [resPlots, resTransects, resMetrics] = await Promise.all([
        fetch(currentProvince.plotsGeoJsonUrl).then(r => r.json()).catch(() => null),
        fetch(currentProvince.transectsGeoJsonUrl).then(r => r.json()).catch(() => null),
        fetch(currentProvince.metricsJsonUrl).then(r => r.json()).catch(() => null)
      ]);

      if (resPlots) {
        plotGeoJson = resPlots;
        setupPlotLayers();
      }
      if (resTransects) {
        transectGeoJson = resTransects;
        setupTransectsLayer();
      }
      if (resMetrics && resMetrics.transects) {
        populateTransectsTable(resMetrics.transects);
      }
    } catch (e) {
      console.warn('Province data fetch error:', e);
    }
  }

  // Province Switcher Button Listeners
  provBtnNakhon.addEventListener('click', () => loadProvinceData('nakhon'));
  provBtnPhangnga.addEventListener('click', () => loadProvinceData('phangnga'));

  // 4. High-Performance 60/120 FPS Swipe Divider Logic
  let cachedViewportRect = null;
  let targetPct = 50;
  let dividerRafId = null;

  function renderDivider() {
    dividerRafId = null;
    const clamped = Math.max(0, Math.min(100, targetPct));
    dividerLine.style.left = `${clamped}%`;
    sliderMapRightContainer.style.clipPath = `polygon(${clamped}% 0, 100% 0, 100% 100%, ${clamped}% 100%)`;
  }

  function scheduleDividerPosition(xPercent) {
    targetPct = xPercent;
    if (!dividerRafId) dividerRafId = requestAnimationFrame(renderDivider);
  }

  function setDividerPositionInstant(xPercent) {
    targetPct = xPercent;
    renderDivider();
  }

  function updateCachedRect() {
    cachedViewportRect = swipeViewport.getBoundingClientRect();
  }

  window.addEventListener('resize', updateCachedRect);

  function handleDragStart(e) {
    isDraggingDivider = true;
    updateCachedRect();
    document.body.classList.add('is-sliding');
    if (e.pointerId !== undefined && dividerLine.setPointerCapture) {
      try { dividerLine.setPointerCapture(e.pointerId); } catch(err){}
    }
    e.preventDefault();
  }

  function handleDragMove(e) {
    if (!isDraggingDivider) return;
    if (!cachedViewportRect) updateCachedRect();
    const clientX = (e.clientX !== undefined && e.clientX !== 0) ? e.clientX : (e.touches && e.touches[0] ? e.touches[0].clientX : null);
    if (clientX === null) return;
    const xPos = clientX - cachedViewportRect.left;
    const pct = (xPos / cachedViewportRect.width) * 100;
    scheduleDividerPosition(pct);
  }

  function handleDragEnd(e) {
    if (!isDraggingDivider) return;
    isDraggingDivider = false;
    document.body.classList.remove('is-sliding');
    if (e && e.pointerId !== undefined && dividerLine.releasePointerCapture) {
      try { dividerLine.releasePointerCapture(e.pointerId); } catch(err){}
    }
  }

  // Pointer Events API (Zero-lag handling for Mouse, Touch, Stylus)
  dividerLine.addEventListener('pointerdown', handleDragStart);
  window.addEventListener('pointermove', handleDragMove, { passive: true });
  window.addEventListener('pointerup', handleDragEnd);
  window.addEventListener('pointercancel', handleDragEnd);

  // Touch fallback
  dividerLine.addEventListener('touchstart', handleDragStart, { passive: false });
  window.addEventListener('touchmove', handleDragMove, { passive: true });
  window.addEventListener('touchend', handleDragEnd);

  // Click on viewport to jump divider
  swipeViewport.addEventListener('pointerdown', (e) => {
    if (e.target.closest('#dividerLine') || e.target.closest('button') || e.target.closest('select') || e.target.closest('.leaflet-control')) return;
    updateCachedRect();
    const xPos = e.clientX - cachedViewportRect.left;
    const pct = (xPos / cachedViewportRect.width) * 100;
    scheduleDividerPosition(pct);
  });

  // 5. Basemap Switcher (OpenStreetMap vs Satellite)
  basemapOsmBtn.addEventListener('click', () => {
    currentBasemap = 'osm';
    basemapOsmBtn.classList.add('active', 'text-white', 'bg-slate-700');
    basemapOsmBtn.classList.remove('text-slate-400');
    basemapSatBtn.classList.remove('active', 'text-white', 'bg-slate-700');
    basemapSatBtn.classList.add('text-slate-400');

    tileLayerLeft.setUrl(OSM_TILE_URL);
    tileLayerRight.setUrl(OSM_TILE_URL);
  });

  basemapSatBtn.addEventListener('click', () => {
    currentBasemap = 'satellite';
    basemapSatBtn.classList.add('active', 'text-white', 'bg-slate-700');
    basemapSatBtn.classList.remove('text-slate-400');
    basemapOsmBtn.classList.remove('active', 'text-white', 'bg-slate-700');
    basemapOsmBtn.classList.add('text-slate-400');

    tileLayerLeft.setUrl(ESRI_TILE_URL);
    tileLayerRight.setUrl(ESRI_TILE_URL);
  });

  // 6. Toggle Plot Boundaries
  toggleBoundaryBtn.addEventListener('click', () => {
    showBoundaries = !showBoundaries;
    if (showBoundaries) {
      toggleBoundaryBtn.classList.add('bg-emerald-950/80', 'text-emerald-300', 'border-emerald-700/60');
      toggleBoundaryBtn.classList.remove('bg-slate-800', 'text-slate-400', 'border-slate-700');
      boundaryBtnText.textContent = 'กรอบแปลง: เปิด';
      if (plotLayerLeft) mapLeft.addLayer(plotLayerLeft);
      if (plotLayerRight) mapRight.addLayer(plotLayerRight);
      if (viewportPlotLegend) viewportPlotLegend.classList.remove('hidden');
    } else {
      toggleBoundaryBtn.classList.remove('bg-emerald-950/80', 'text-emerald-300', 'border-emerald-700/60');
      toggleBoundaryBtn.classList.add('bg-slate-800', 'text-slate-400', 'border-slate-700');
      boundaryBtnText.textContent = 'กรอบแปลง: ปิด';
      if (plotLayerLeft) mapLeft.removeLayer(plotLayerLeft);
      if (plotLayerRight) mapRight.removeLayer(plotLayerRight);
      if (viewportPlotLegend) viewportPlotLegend.classList.add('hidden');
    }
  });

  // 7. Zoom Controls
  zoomInBtn.addEventListener('click', () => mapLeft.zoomIn());
  zoomOutBtn.addEventListener('click', () => mapLeft.zoomOut());
  zoomResetBtn.addEventListener('click', () => {
    setDividerPositionInstant(50);
    mapLeft.fitBounds(currentProvince.initialBounds, { padding: [30, 30] });
  });

  // 8. Plot Selection & Camera Flying
  plotSelector.addEventListener('change', (e) => {
    currentPlot = e.target.value;
    if (currentPlot === 'drone-area') {
      mapLeft.fitBounds(currentProvince.droneBounds, { padding: [30, 30] });
    } else if (currentPlot === 'drone-area-40-1' && currentProvince.droneBounds40_1) {
      mapLeft.fitBounds(currentProvince.droneBounds40_1, { padding: [30, 30] });
    } else if (currentPlot === 'drone-area-40-2' && currentProvince.droneBounds40_2) {
      mapLeft.fitBounds(currentProvince.droneBounds40_2, { padding: [30, 30] });
    } else if (currentPlot === 'drone-area-41' && currentProvince.droneBounds41) {
      mapLeft.fitBounds(currentProvince.droneBounds41, { padding: [30, 30] });
    } else if (individualPlotBounds[currentPlot]) {
      mapLeft.fitBounds(individualPlotBounds[currentPlot], { padding: [30, 30] });
    } else if (plotLayerLeft) {
      mapLeft.fitBounds(plotLayerLeft.getBounds(), { padding: [40, 40] });
    }
  });

  // 9. Comparator Mode Toggle
  compareModeTemporalBtn.addEventListener('click', () => {
    comparatorMode = 'temporal';
    compareModeTemporalBtn.classList.add('active', 'bg-mangrove-600', 'text-white');
    compareModeTemporalBtn.classList.remove('text-slate-400');
    compareModeResolutionBtn.classList.remove('active', 'bg-mangrove-600', 'text-white');
    compareModeResolutionBtn.classList.add('text-slate-400');

    temporalControls.classList.remove('hidden');
    temporalControls.classList.add('flex');
    temporalQualityControls.classList.remove('hidden');
    temporalQualityControls.classList.add('flex');
    resolutionControls.classList.add('hidden');
    resolutionControls.classList.remove('flex');

    updateSliderOverlays();
  });

  compareModeResolutionBtn.addEventListener('click', () => {
    comparatorMode = 'resolution';
    compareModeResolutionBtn.classList.add('active', 'bg-mangrove-600', 'text-white');
    compareModeResolutionBtn.classList.remove('text-slate-400');
    compareModeTemporalBtn.classList.remove('active', 'bg-mangrove-600', 'text-white');
    compareModeTemporalBtn.classList.add('text-slate-400');

    temporalControls.classList.add('hidden');
    temporalControls.classList.remove('flex');
    temporalQualityControls.classList.add('hidden');
    temporalQualityControls.classList.remove('flex');
    resolutionControls.classList.remove('hidden');
    resolutionControls.classList.add('flex');

    updateSliderOverlays();
  });

  leftDateSelector.addEventListener('change', (e) => {
    leftDate = e.target.value;
    updateSliderOverlays();
  });

  rightDateSelector.addEventListener('change', (e) => {
    rightDate = e.target.value;
    updateSliderOverlays();
  });

  singleDateSelector.addEventListener('change', (e) => {
    singleDate = e.target.value;
    updateSliderOverlays();
  });

  temporalQualitySelector.addEventListener('change', (e) => {
    temporalQuality = e.target.value;
    updateSliderOverlays();
  });

  bandTabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      bandTabBtns.forEach(b => b.classList.remove('active', 'text-white'));
      btn.classList.add('active', 'text-white');
      currentMode = btn.getAttribute('data-mode');
      updateSliderOverlays();
    });
  });

  // 10. Fullscreen Mode
  fullscreenBtn.addEventListener('click', () => {
    isFullscreen = !isFullscreen;
    if (isFullscreen) {
      sliderSectionCard.classList.add('fullscreen-viewer-mode');
      fullscreenBtn.innerHTML = '<i class="fa-solid fa-compress text-white"></i><span id="fullscreenBtnText">ย่อจอ</span>';
      fullscreenBtn.classList.add('bg-mangrove-600', 'text-white');
    } else {
      exitFullscreen();
    }
    setTimeout(() => {
      mapLeft.invalidateSize();
      mapRight.invalidateSize();
    }, 150);
  });

  function exitFullscreen() {
    isFullscreen = false;
    sliderSectionCard.classList.remove('fullscreen-viewer-mode');
    fullscreenBtn.innerHTML = '<i class="fa-solid fa-expand text-mangrove-400"></i><span id="fullscreenBtnText">เต็มจอ</span>';
    fullscreenBtn.classList.remove('bg-mangrove-600', 'text-white');
    setTimeout(() => {
      mapLeft.invalidateSize();
      mapRight.invalidateSize();
    }, 150);
  }

  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isFullscreen) exitFullscreen();
  });

  // 11. Bottom Map Controls
  if (toggleBottomDroneBtn) {
    toggleBottomDroneBtn.addEventListener('click', () => {
      showBottomDrone = !showBottomDrone;
      if (showBottomDrone) {
        mapBottom.addLayer(bottomDroneGroup);
        toggleBottomDroneBtn.classList.add('bg-sky-950/80', 'text-sky-300', 'border-sky-500/50');
        toggleBottomDroneBtn.classList.remove('bg-slate-800', 'text-slate-400');
        bottomDroneBtnText.textContent = 'ภาพโดรน: เปิด';
      } else {
        mapBottom.removeLayer(bottomDroneGroup);
        toggleBottomDroneBtn.classList.remove('bg-sky-950/80', 'text-sky-300', 'border-sky-500/50');
        toggleBottomDroneBtn.classList.add('bg-slate-800', 'text-slate-400');
        bottomDroneBtnText.textContent = 'ภาพโดรน: ปิด';
      }
    });
  }

  let showTransects = true;
  toggleTransectsBtn.addEventListener('click', () => {
    showTransects = !showTransects;
    if (showTransects) {
      if (transectsLayer) mapBottom.addLayer(transectsLayer);
      toggleTransectsBtn.classList.add('text-emerald-300', 'border-emerald-500/40');
      toggleTransectsBtn.classList.remove('text-slate-400');
    } else {
      if (transectsLayer) mapBottom.removeLayer(transectsLayer);
      toggleTransectsBtn.classList.remove('text-emerald-300', 'border-emerald-500/40');
      toggleTransectsBtn.classList.add('text-slate-400');
    }
  });

  recenterMapBtn.addEventListener('click', () => {
    mapBottom.fitBounds(currentProvince.initialBounds, { padding: [20, 20] });
  });

  // Initial Load
  await loadProvinceData(activeProvinceKey);
});
'''

with open('web/src/app.js', 'w', encoding='utf-8') as f:
    f.write(code)
print("Successfully generated web/src/app.js")
