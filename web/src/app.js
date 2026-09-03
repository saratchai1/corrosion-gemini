// JavaScript Application for Nakhon Si Thammarat Coastal Erosion & Mudflat Accretion Dashboard
// Fully Compliant with sentinel-2-super-resolution and coastal-erosion-accretion skills
// Features: Dual-Map Swipe Slider with OpenStreetMap Background, UAV Drone Orthomosaic (2.6cm/px), Full Plot Coverage, Vector Boundaries, & Native Smooth Zoom

document.addEventListener('DOMContentLoaded', async () => {
  let summaryData = null;
  let coastalMetrics = null;
  let transectGeoJson = null;
  let plotGeoJson = null;

  // Comparator State
  let comparatorMode = 'temporal'; // 'temporal' (before vs after) or 'resolution' (10m vs 2.5m)
  let currentPlot = 'combined-vsd';
  let currentMode = 'rgb'; // 'rgb', 'cir', 'ndvi'
  let leftDate = '2023-04-06';
  let rightDate = 'drone-ortho'; // Default to user's drone image for high impact
  let singleDate = 'drone-ortho';
  let temporalQuality = '2p5m'; // '2p5m' or '10m'
  let currentBasemap = 'osm'; // 'osm' or 'satellite'
  let showBoundaries = true;
  let showBottomDrone = true;
  let isFullscreen = false;
  let isDraggingDivider = false;

  // Exact geographic bounding box for wide Sentinel-2 footprint
  const sentinelBounds = [
    [8.57549576268467, 99.98614806906022], // South-West
    [8.610315197158018, 100.02113228300021] // North-East
  ];

  // Exact geographic bounding box for high-resolution UAV Drone Orthomosaic (EPSG:32647 -> WGS84)
  const droneBounds = [
    [8.585914525682421, 99.99048684871822], // South-West
    [8.60302831899287, 100.01235991418478]  // North-East
  ];

  const initialCenter = [8.59478, 100.00268];

  // DOM Elements
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

  const dateLabels = {
    '2023-04-06': 'ก่อนเริ่มปลูก (เม.ย. 2566)',
    '2024-04-05': 'หลังปลูก 1 ปี (เม.ย. 2567)',
    '2026-04-05': 'หลังปลูก 3 ปี (เม.ย. 2569)',
    'drone-ortho': '🛸 ภาพถ่ายโดรน UAV (ความละเอียด 2.6 cm/px)'
  };

  const sceneMap = {
    '2023-04-06': 'S2A_47PPK_20230406_0_L2A',
    '2024-04-05': 'S2B_47PPK_20240405_0_L2A',
    '2026-04-05': 'S2B_47PPK_20260405_0_L2A',
    'drone-ortho': 'UAV-Drone-Orthomosaic-Tha-Sala-22-23-VSD'
  };

  // Basemap Tile URLs
  const OSM_TILE_URL = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
  const ESRI_TILE_URL = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';

  // 1. Initialize Dual Leaflet Slider Maps
  const mapLeft = L.map('sliderMapLeft', {
    center: initialCenter,
    zoom: 15,
    minZoom: 11,
    maxZoom: 19,
    zoomControl: false,
    attributionControl: false
  });

  const mapRight = L.map('sliderMapRight', {
    center: initialCenter,
    zoom: 15,
    minZoom: 11,
    maxZoom: 19,
    zoomControl: false,
    attributionControl: false
  });

  // Basemap Tile Layers
  const tileLayerLeft = L.tileLayer(OSM_TILE_URL, { maxZoom: 19 }).addTo(mapLeft);
  const tileLayerRight = L.tileLayer(OSM_TILE_URL, { maxZoom: 19 }).addTo(mapRight);

  // High-Resolution Overlays on both maps
  const initialSentinelUrl = 'public/data/superres25/combined-vsd-2023-04-06-2p5m.webp';
  const initialDroneUrl = 'public/data/drone/drone_ortho_hd.webp';
  let overlayLeft = L.imageOverlay(initialSentinelUrl, sentinelBounds, { opacity: 1.0 }).addTo(mapLeft);
  let overlayRight = L.imageOverlay(initialDroneUrl, droneBounds, { opacity: 1.0 }).addTo(mapRight);

  // Vector Plot Boundary Layers on both maps
  let plotLayerLeft = null;
  let plotLayerRight = null;
  let plotBoundsAll = null;
  let plot22Bounds = null;
  let plot23Bounds = null;

  // 2. Synchronize Dual Maps (Left map drives Right map)
  mapLeft.on('move', () => {
    mapRight.setView(mapLeft.getCenter(), mapLeft.getZoom(), { animate: false });
  });

  // 3. Fetch Data (GeoJSON Plots, Metrics, Summary)
  try {
    const [resSummary, resMetrics, resTransects, resPlots] = await Promise.all([
      fetch('public/data/superres25/summary.json').catch(() => null),
      fetch('public/data/coastal_metrics.json').catch(() => null),
      fetch('public/data/coastal_transects.geojson').catch(() => null),
      fetch('public/data/nakhon_plots_combined.geojson').catch(() => null)
    ]);

    if (resSummary && resSummary.ok) summaryData = await resSummary.json();
    if (resMetrics && resMetrics.ok) {
      coastalMetrics = await resMetrics.json();
      populateTransectsTable(coastalMetrics.transects);
    }
    if (resTransects && resTransects.ok) transectGeoJson = await resTransects.json();
    if (resPlots && resPlots.ok) {
      plotGeoJson = await resPlots.json();
      setupPlotLayers();
    }
  } catch (err) {
    console.warn('Data fetch warning:', err);
  }

  // Set up Vector Plot Boundaries on both maps
  function setupPlotLayers() {
    if (!plotGeoJson) return;

    const plotStyle = (feature) => {
      const is22 = feature.properties.Name && feature.properties.Name.includes('22-VSD');
      return {
        color: is22 ? '#10b981' : '#38bdf8',
        weight: 3,
        dashArray: '6, 6',
        fillColor: is22 ? '#059669' : '#0284c7',
        fillOpacity: 0.15
      };
    };

    const onEachPlot = (feature, layer) => {
      const name = feature.properties.Name || 'แปลงป่าชายเลน';
      const is22 = name.includes('22-VSD');
      const area = is22 ? '300.64 ไร่' : '200.12 ไร่';
      
      layer.bindTooltip(`<strong>${is22 ? 'แปลง 22-VSD' : 'แปลง 23-VSD'}</strong> (${area})`, {
        permanent: false,
        direction: 'center',
        className: 'bg-slate-900/90 text-white font-sans text-xs px-2 py-1 rounded border border-slate-700'
      });
    };

    plotLayerLeft = L.geoJSON(plotGeoJson, { style: plotStyle, onEachFeature: onEachPlot }).addTo(mapLeft);
    plotLayerRight = L.geoJSON(plotGeoJson, { style: plotStyle, onEachFeature: onEachPlot }).addTo(mapRight);

    plotBoundsAll = plotLayerLeft.getBounds();

    // Calculate individual plot bounds
    plotLayerLeft.eachLayer(layer => {
      const name = layer.feature.properties.Name || '';
      if (name.includes('22-VSD')) plot22Bounds = layer.getBounds();
      if (name.includes('23-VSD')) plot23Bounds = layer.getBounds();
    });

    // Fit map to drone bounds initially (or plot bounds)
    mapLeft.fitBounds(droneBounds, { padding: [30, 30] });
  }

  // 4. Update Overlays based on User Selection (Sentinel-2 vs UAV Drone)
  function updateSliderOverlays() {
    let modePrefix = '';
    if (currentMode === 'cir') modePrefix = 'cir-';
    if (currentMode === 'ndvi') modePrefix = 'ndvi-';

    if (comparatorMode === 'temporal') {
      // Left side configuration
      if (leftDate === 'drone-ortho') {
        overlayLeft.setUrl('public/data/drone/drone_ortho_hd.webp');
        overlayLeft.setBounds(droneBounds);
        leftBadgeText.textContent = dateLabels['drone-ortho'];
      } else {
        overlayLeft.setUrl(`public/data/superres25/combined-vsd-${leftDate}-${modePrefix}${temporalQuality}.webp`);
        overlayLeft.setBounds(sentinelBounds);
        const qLabel = temporalQuality === '2p5m' ? '4x SR (2.5m)' : 'Native (10m)';
        leftBadgeText.textContent = `${dateLabels[leftDate] || leftDate} [${qLabel}]`;
      }

      // Right side configuration
      if (rightDate === 'drone-ortho') {
        overlayRight.setUrl('public/data/drone/drone_ortho_hd.webp');
        overlayRight.setBounds(droneBounds);
        rightBadgeText.textContent = dateLabels['drone-ortho'];
      } else {
        overlayRight.setUrl(`public/data/superres25/combined-vsd-${rightDate}-${modePrefix}${temporalQuality}.webp`);
        overlayRight.setBounds(sentinelBounds);
        const qLabel = temporalQuality === '2p5m' ? '4x SR (2.5m)' : 'Native (10m)';
        rightBadgeText.textContent = `${dateLabels[rightDate] || rightDate} [${qLabel}]`;
      }

      currentSceneTag.textContent = `เทียบ: ${leftDate === 'drone-ortho' ? 'ภาพโดรน' : leftDate} vs ${rightDate === 'drone-ortho' ? 'ภาพถ่ายโดรนความละเอียดสูง (2.6 cm)' : rightDate}`;
    } else {
      // Resolution Mode: Compare Sentinel vs Drone Ortho
      if (singleDate === 'drone-ortho') {
        overlayLeft.setUrl(`public/data/superres25/combined-vsd-2026-04-05-${modePrefix}2p5m.webp`);
        overlayLeft.setBounds(sentinelBounds);
        leftBadgeText.textContent = 'ดาวเทียม Sentinel-2 (2.5m SR)';

        overlayRight.setUrl('public/data/drone/drone_ortho_hd.webp');
        overlayRight.setBounds(droneBounds);
        rightBadgeText.textContent = '🛸 ภาพถ่ายโดรน UAV (2.6 cm/px)';

        currentSceneTag.textContent = 'เปรียบเทียบ: ดาวเทียม 2.5m vs ภาพถ่ายโดรนจริง 2.6cm';
      } else {
        overlayLeft.setUrl(`public/data/superres25/combined-vsd-${singleDate}-${modePrefix}10m.webp`);
        overlayLeft.setBounds(sentinelBounds);
        leftBadgeText.textContent = `Native 10m [${dateLabels[singleDate] || singleDate}]`;

        overlayRight.setUrl(`public/data/superres25/combined-vsd-${singleDate}-${modePrefix}2p5m.webp`);
        overlayRight.setBounds(sentinelBounds);
        rightBadgeText.textContent = `4x Super-Res 2.5m [${dateLabels[singleDate] || singleDate}]`;

        currentSceneTag.textContent = `Scene: ${sceneMap[singleDate] || 'Sentinel-2 L2A'} (${singleDate})`;
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

  updateSliderOverlays();

  // 5. High-Performance 60/120 FPS Swipe Divider Logic
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
    if (!dividerRafId) {
      dividerRafId = requestAnimationFrame(renderDivider);
    }
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

  // Tap/click on the viewport to slide directly
  swipeViewport.addEventListener('pointerdown', (e) => {
    if (e.target.closest('#dividerLine') || e.target.closest('button') || e.target.closest('select') || e.target.closest('.leaflet-control')) return;
    updateCachedRect();
    const xPos = e.clientX - cachedViewportRect.left;
    const pct = (xPos / cachedViewportRect.width) * 100;
    scheduleDividerPosition(pct);
  });

  // 6. Basemap Switcher (OpenStreetMap vs Satellite)
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

  // 7. Toggle Plot Boundaries
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

  // 8. Zoom Controls
  zoomInBtn.addEventListener('click', () => mapLeft.zoomIn());
  zoomOutBtn.addEventListener('click', () => mapLeft.zoomOut());
  zoomResetBtn.addEventListener('click', () => {
    setDividerPositionInstant(50);
    mapLeft.fitBounds(droneBounds, { padding: [30, 30] });
  });

  // 9. Plot Selection & Camera Flying
  plotSelector.addEventListener('change', (e) => {
    currentPlot = e.target.value;
    if (currentPlot === 'drone-area') {
      mapLeft.fitBounds(droneBounds, { padding: [30, 30] });
    } else if (currentPlot === '22-vsd' && plot22Bounds) {
      mapLeft.fitBounds(plot22Bounds, { padding: [30, 30] });
    } else if (currentPlot === '23-vsd' && plot23Bounds) {
      mapLeft.fitBounds(plot23Bounds, { padding: [30, 30] });
    } else if (plotBoundsAll) {
      mapLeft.fitBounds(plotBoundsAll, { padding: [40, 40] });
    }
  });

  // 10. Comparator Mode Toggle (Temporal vs Resolution)
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

  // 11. Fullscreen Mode
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

  // 12. Bottom Leaflet Map (GIS Map with Drone Overlay & Transects)
  const mapBottom = L.map('mapView', {
    center: initialCenter,
    zoom: 15,
    zoomControl: false
  });

  L.control.zoom({ position: 'bottomright' }).addTo(mapBottom);

  L.tileLayer(ESRI_TILE_URL, {
    attribution: 'Tiles &copy; Esri &mdash; Sentinel-2 L2A',
    maxZoom: 19
  }).addTo(mapBottom);

  // Drone Orthomosaic Layer on Bottom Map
  const bottomDroneOverlay = L.imageOverlay('public/data/drone/drone_ortho_hd.webp', droneBounds, {
    opacity: 0.95
  }).addTo(mapBottom);

  if (toggleBottomDroneBtn) {
    toggleBottomDroneBtn.addEventListener('click', () => {
      showBottomDrone = !showBottomDrone;
      if (showBottomDrone) {
        mapBottom.addLayer(bottomDroneOverlay);
        toggleBottomDroneBtn.classList.add('bg-sky-950/80', 'text-sky-300', 'border-sky-500/50');
        toggleBottomDroneBtn.classList.remove('bg-slate-800', 'text-slate-400');
        bottomDroneBtnText.textContent = 'ภาพโดรน: เปิด';
      } else {
        mapBottom.removeLayer(bottomDroneOverlay);
        toggleBottomDroneBtn.classList.remove('bg-sky-950/80', 'text-sky-300', 'border-sky-500/50');
        toggleBottomDroneBtn.classList.add('bg-slate-800', 'text-slate-400');
        bottomDroneBtnText.textContent = 'ภาพโดรน: ปิด';
      }
    });
  }

  let bottomPlotLayer = null;
  let transectsLayer = null;
  let showTransects = true;

  if (plotGeoJson) {
    bottomPlotLayer = L.geoJSON(plotGeoJson, {
      style: (feature) => {
        const is22 = feature.properties.Name && feature.properties.Name.includes('22-VSD');
        return {
          color: is22 ? '#10b981' : '#38bdf8',
          weight: 2.5,
          opacity: 0.9,
          fillColor: is22 ? '#059669' : '#0284c7',
          fillOpacity: 0.2,
          dashArray: '4, 4'
        };
      },
      onEachFeature: (feature, layer) => {
        const is22 = (feature.properties.Name || '').includes('22-VSD');
        layer.bindPopup(`
          <div class="p-1 space-y-1 font-sans">
            <h4 class="font-bold text-sm text-white flex items-center gap-1.5">
              <span class="w-2.5 h-2.5 rounded-full ${is22 ? 'bg-emerald-400' : 'bg-sky-400'}"></span>
              ${is22 ? 'แปลง 22-VSD' : 'แปลง 23-VSD'}
            </h4>
            <p class="text-xs text-slate-300">ต.ท่าศาลา จ.นครศรีธรรมราช</p>
            <div class="border-t border-slate-700/60 pt-1.5 text-xs text-slate-300 space-y-0.5">
              <p><strong>เนื้อที่:</strong> ${is22 ? '300.64' : '200.12'} ไร่ (พื้นที่เลนงอก)</p>
              <p><strong>จำนวนปลูก:</strong> ${is22 ? '213,757' : '142,288'} ต้น</p>
              <p><strong>พันธุ์ไม้หลัก:</strong> โกงกางใบใหญ่, โกงกางใบเล็ก, แสมขาว</p>
            </div>
          </div>
        `);
      }
    }).addTo(mapBottom);

    recenterMapBtn.addEventListener('click', () => {
      mapBottom.fitBounds(droneBounds, { padding: [20, 20] });
    });
  }

  // Load Transects on Bottom Map
  if (transectGeoJson) {
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
    }).addTo(mapBottom);

    toggleTransectsBtn.addEventListener('click', () => {
      showTransects = !showTransects;
      if (showTransects) {
        mapBottom.addLayer(transectsLayer);
        toggleTransectsBtn.classList.add('text-emerald-300', 'border-emerald-500/40');
        toggleTransectsBtn.classList.remove('text-slate-400');
      } else {
        mapBottom.removeLayer(transectsLayer);
        toggleTransectsBtn.classList.remove('text-emerald-300', 'border-emerald-500/40');
        toggleTransectsBtn.classList.add('text-slate-400');
      }
    });
  }

  // Populate Transect Table
  function populateTransectsTable(transects) {
    if (!transectsTableBody || !transects) return;
    transectsTableBody.innerHTML = '';
    const sample = transects.filter((_, idx) => idx % 4 === 0);
    sample.forEach(t => {
      const tr = document.createElement('tr');
      tr.className = 'hover:bg-slate-800/40 transition';
      const badgeColor = t.waterline_class.includes('ACCRETION') 
        ? 'text-emerald-400 bg-emerald-950/60 border border-emerald-800/60' 
        : 'text-slate-400 bg-slate-800/60 border border-slate-700/60';

      tr.innerHTML = `
        <td class="py-2 px-3 font-semibold text-white">${t.id}</td>
        <td class="py-2 px-3 text-slate-400">${t.y_utm.toFixed(1)}</td>
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

  // 13. Temporal Chart (Chart.js)
  const ctx = document.getElementById('temporalChart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['เม.ย. 2566 (ก่อนปลูก)', 'เม.ย. 2567 (1 ปี)', 'เม.ย. 2569 (3 ปี)'],
      datasets: [
        {
          label: 'ดินเลนงอกสะสม (ไร่)',
          data: [0, 2.1, 226.0],
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
          data: [0.21, 0.39, 0.58],
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
});
