import os
import json
import numpy as np
import rasterio
from shapely.geometry import LineString, MultiLineString, Polygon, mapping, shape
from shapely.ops import unary_union
import geopandas as gpd
from skimage.filters import threshold_otsu
from scipy import ndimage
import pyproj

PROJECTED_CRS = "EPSG:32647" # UTM Zone 47N
DATES = ["2023-04-11", "2024-03-19", "2026-03-21"]

def load_native_bands(date_str):
    tif_path = f"outputs/superres/phangnga/{date_str}/wide_native.tif"
    with rasterio.open(tif_path) as src:
        data = src.read()
        transform = src.transform
        crs = src.crs
    red = data[0].astype(np.float32)
    green = data[1].astype(np.float32)
    blue = data[2].astype(np.float32)
    nir = data[3].astype(np.float32)
    return red, green, blue, nir, transform, crs

def analyze_phangnga():
    print("Starting Phang Nga Quantitative Coastal & Mudflat Analysis...")
    epochs_data = {}
    
    for d in DATES:
        red, green, blue, nir, tf, crs = load_native_bands(d)
        
        # Native NDWI & NDVI
        ndwi = (green - nir) / (green + nir + 1e-5)
        ndvi = (nir - red) / (nir + red + 1e-5)
        
        # Otsu threshold for water
        otsu_val = float(threshold_otsu(ndwi))
        otsu_clamped = max(-0.15, min(0.15, otsu_val))
        water_mask = ndwi > otsu_clamped
        
        # Mangrove mask
        mangrove_mask = ndvi >= 0.35
        
        epochs_data[d] = {
            "ndwi": ndwi,
            "ndvi": ndvi,
            "water_mask": water_mask,
            "mangrove_mask": mangrove_mask,
            "transform": tf,
            "crs": crs
        }
        print(f"[{d}] NDWI & NDVI calculated. Water px: {np.sum(water_mask)}, Mangrove px: {np.sum(mangrove_mask)}")

    tf = epochs_data["2023-04-11"]["transform"]
    H, W = epochs_data["2023-04-11"]["water_mask"].shape
    pixel_size = tf[0] # 10m
    
    # Generate DSAS-like transects across Koh Mai Phai / Phang Nga Bay
    # Plots 40, 41, 42 are centered around rows 120-280, cols 100-300
    transects = []
    waterline_positions = {d: [] for d in DATES}
    mangrove_positions = {d: [] for d in DATES}
    
    step = 5 # every 50 meters
    for r in range(40, H - 40, step):
        x_start, y_pos = rasterio.transform.xy(tf, r, 20)
        x_end, _ = rasterio.transform.xy(tf, r, W - 20)
        
        transect_id = f"T_{r:03d}"
        transect_line = LineString([(x_start, y_pos), (x_end, y_pos)])
        transects.append({
            "id": transect_id,
            "row": r,
            "y": y_pos,
            "line": transect_line
        })
        
        for d in DATES:
            wmask = epochs_data[d]["water_mask"][r, :]
            mmask = epochs_data[d]["mangrove_mask"][r, :]
            
            # Find water boundary (first ocean transition from west to east)
            water_idx = np.where(wmask)[0]
            if len(water_idx) > 0:
                col_water = float(water_idx[-1])
            else:
                col_water = float(W - 1)
            waterline_positions[d].append(col_water * pixel_size)
            
            # Find seaward mangrove edge
            mang_idx = np.where(mmask)[0]
            if len(mang_idx) > 0:
                col_mang = float(mang_idx[-1])
            else:
                col_mang = 0.0
            mangrove_positions[d].append(col_mang * pixel_size)

    # Compute NSM & EPR
    nsm_water_all = np.array(waterline_positions["2026-03-21"]) - np.array(waterline_positions["2023-04-11"])
    nsm_mangrove_all = np.array(mangrove_positions["2026-03-21"]) - np.array(mangrove_positions["2023-04-11"])
    
    # Clip extreme outliers
    valid_mask = np.abs(nsm_water_all) < 500
    nsm_water = nsm_water_all[valid_mask] if np.sum(valid_mask) > 0 else nsm_water_all
    
    mean_nsm_water = float(np.mean(nsm_water))
    max_nsm_water = float(np.max(nsm_water))
    min_nsm_water = float(np.min(nsm_water))
    epr_water = mean_nsm_water / 3.0 # meters / year
    
    mean_nsm_mangrove = float(np.mean(nsm_mangrove_all[nsm_mangrove_all > -50]))
    epr_mangrove = mean_nsm_mangrove / 3.0
    
    # Area changes
    base_water = np.sum(epochs_data["2023-04-11"]["water_mask"])
    y3_water = np.sum(epochs_data["2026-03-21"]["water_mask"])
    water_diff_px = base_water - y3_water # Positive means water turned to land (accretion)
    accretion_rai = max(0.0, float(water_diff_px * 100.0 / 1600.0))
    erosion_rai = max(0.0, float(-water_diff_px * 100.0 / 1600.0))
    
    base_mang = np.sum(epochs_data["2023-04-11"]["mangrove_mask"])
    y3_mang = np.sum(epochs_data["2026-03-21"]["mangrove_mask"])
    mangrove_growth_rai = float((y3_mang - base_mang) * 100.0 / 1600.0)
    
    # Convert transects to WGS84 GeoJSON
    wgs84 = pyproj.CRS("EPSG:4326")
    utm = pyproj.CRS(PROJECTED_CRS)
    transformer = pyproj.Transformer.from_crs(utm, wgs84, always_xy=True)
    
    features = []
    for idx, t in enumerate(transects):
        l = t["line"]
        pts_wgs = [transformer.transform(x, y) for x, y in l.coords]
        
        t_nsm = float(nsm_water_all[idx])
        t_epr = float(t_nsm / 3.0)
        t_mang_nsm = float(nsm_mangrove_all[idx])
        
        feat = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": pts_wgs
            },
            "properties": {
                "id": t["id"],
                "row": t["row"],
                "nsm_water_m": round(t_nsm, 2),
                "epr_water_m_yr": round(t_epr, 2),
                "mangrove_advance_m": round(t_mang_nsm, 2),
                "classification": "Accretion" if t_nsm >= 11.18 else ("Erosion" if t_nsm <= -11.18 else "Stable")
            }
        }
        features.append(feat)

    transects_geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    out_geojson_path = "web/public/data/phangnga/coastal_transects.geojson"
    with open(out_geojson_path, "w", encoding="utf-8") as f:
        json.dump(transects_geojson, f, indent=2)
    print(f"Saved {len(features)} transects to {out_geojson_path}")
    
    metrics = {
        "project": "โครงการปลูกป่าชายเลนเพื่อประโยชน์จากคาร์บอนเครดิต จ.พังงา",
        "tver_type": "Standard กลุ่ม 2 VSD",
        "province": "พังงา",
        "location": "อ่าวพังงา (เกาะไม้ไผ่ - เกาะปันหยี) อ.เมือง จ.พังงา",
        "plots_covered": ["40-VSD", "41-VSD", "42-VSD"],
        "total_contract_rai": 699.49,
        "total_pdd_rai": 679.26,
        "total_seedlings_planted": 235539,
        "monitoring_period": "2023-04-11 to 2026-03-21 (3 ปี)",
        "baseline_scene": "S2B_47PMK_20230411_0_L2A",
        "year1_scene": "S2B_47PMK_20240319_0_L2A",
        "year3_scene": "S2C_47PMK_20260321_0_L2A",
        "coastal_dynamics": {
            "nsm_waterline_mean_m": round(mean_nsm_water, 2),
            "nsm_waterline_max_m": round(max_nsm_water, 2),
            "nsm_waterline_min_m": round(min_nsm_water, 2),
            "epr_waterline_m_per_year": round(epr_water, 2),
            "mangrove_edge_advance_mean_m": round(mean_nsm_mangrove, 2),
            "mangrove_edge_epr_m_per_year": round(epr_mangrove, 2),
            "net_mudflat_accretion_rai": round(accretion_rai, 1),
            "coastal_erosion_rai": round(erosion_rai, 1),
            "mangrove_canopy_expansion_rai": round(mangrove_growth_rai, 1),
            "uncertainty_u_total_m": 11.18,
            "total_transects_evaluated": len(features)
        },
        "vegetation_health": {
            "mean_ndvi_baseline_2023": float(np.nanmean(epochs_data["2023-04-11"]["ndvi"])),
            "mean_ndvi_year1_2024": float(np.nanmean(epochs_data["2024-03-19"]["ndvi"])),
            "mean_ndvi_year3_2026": float(np.nanmean(epochs_data["2026-03-21"]["ndvi"]))
        }
    }
    
    out_metrics_path = "web/public/data/phangnga/coastal_metrics.json"
    with open(out_metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    print(f"Saved coastal metrics to {out_metrics_path}")
    print(json.dumps(metrics["coastal_dynamics"], indent=2))

if __name__ == "__main__":
    analyze_phangnga()
