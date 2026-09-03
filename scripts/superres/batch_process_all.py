import os
import json
import numpy as np
import rasterio
from PIL import Image, ImageStat
import geoai

DATES = ["2023-04-06", "2024-04-05", "2026-04-05"]
PLOTS = [
    {"id": "22-vsd", "label": "แปลง 22-VSD", "lon": 100.00318, "lat": 8.59360, "area_rai": 300.64, "sz": 128, "out_sz": 512},
    {"id": "23-vsd", "label": "แปลง 23-VSD", "lon": 100.00218, "lat": 8.59597, "area_rai": 200.12, "sz": 128, "out_sz": 512},
    {"id": "combined-vsd", "label": "ภาพรวมโครงการ 22-VSD & 23-VSD", "lon": 100.00268, "lat": 8.59478, "area_rai": 500.76, "sz": 256, "out_sz": 1024}
]

SCENE_IDS = {
    "2023-04-06": "S2A_47PPK_20230406_0_L2A",
    "2024-04-05": "S2B_47PPK_20240405_0_L2A",
    "2026-04-05": "S2B_47PPK_20260405_0_L2A"
}

def stretch_to_uint8(bands_data, limits):
    out = np.zeros_like(bands_data, dtype=np.float32)
    for b in range(len(bands_data)):
        lo, hi = limits[b]
        if hi <= lo:
            hi = lo + 1.0
        clipped = np.clip(bands_data[b], lo, hi)
        out[b] = (clipped - lo) / (hi - lo) * 255.0
    return out.transpose(1, 2, 0).astype(np.uint8)

def compute_ndvi_rgb(red, nir):
    denom = nir.astype(np.float32) + red.astype(np.float32) + 1e-6
    ndvi = (nir.astype(np.float32) - red.astype(np.float32)) / denom
    # Colormap: water/mud (-0.2 to 0.1) -> brown/slate, (0.1 to 0.4) -> yellowish/olive, (0.4 to 0.8) -> lush green
    # Normalize ndvi -0.1 to 0.7 into 0..1
    norm = np.clip((ndvi + 0.1) / 0.8, 0.0, 1.0)
    
    # Custom colormap
    r = np.zeros_like(norm)
    g = np.zeros_like(norm)
    b = np.zeros_like(norm)
    
    # Segment 1: low (mud / water)
    mask1 = norm < 0.35
    r[mask1] = 60 + norm[mask1] * 120
    g[mask1] = 70 + norm[mask1] * 130
    b[mask1] = 90 + norm[mask1] * 70
    
    # Segment 2: medium (sparse vegetation / new sprouts)
    mask2 = (norm >= 0.35) & (norm < 0.65)
    t = (norm[mask2] - 0.35) / 0.30
    r[mask2] = 110 * (1 - t) + 40 * t
    g[mask2] = 120 * (1 - t) + 180 * t
    b[mask2] = 80 * (1 - t) + 50 * t
    
    # Segment 3: high (dense mangrove canopy)
    mask3 = norm >= 0.65
    t2 = (norm[mask3] - 0.65) / 0.35
    r[mask3] = 40 * (1 - t2) + 15 * t2
    g[mask3] = 180 * (1 - t2) + 220 * t2
    b[mask3] = 50 * (1 - t2) + 40 * t2
    
    rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
    return rgb, float(np.mean(ndvi))

def main():
    web_dir = "web/public/data/superres25"
    os.makedirs(web_dir, exist_ok=True)
    summary_entries = []
    
    for date_str in DATES:
        scene_id = SCENE_IDS[date_str]
        date_dir = f"outputs/superres/nakhon/{date_str}"
        print(f"\n================ Processing Date: {date_str} ================")
        
        for plot in PLOTS:
            pid = plot["id"]
            native_tif = f"{date_dir}/{pid}_native.tif"
            sr_tif = f"{date_dir}/{pid}_sr.tif"
            
            print(f"[{pid}] Date {date_str}: Reading native TIFF...", flush=True)
            with rasterio.open(native_tif) as src:
                native_data = src.read() # [4, H, W] = [R, G, B, NIR]
                native_crs = str(src.crs)
            
            # Nonzero fraction check
            nonzero_fraction = float(np.count_nonzero(native_data[:3]) / native_data[:3].size)
            assert nonzero_fraction > 0.85, f"Low nonzero fraction: {nonzero_fraction}"
            
            # Super-resolution inference
            if not os.path.exists(sr_tif):
                print(f"[{pid}] Running 4x Super-Resolution inference...", flush=True)
                geoai.super_resolution(
                    input_lr_path=native_tif,
                    output_sr_path=sr_tif,
                    rgb_nir_bands=[1, 2, 3, 4],
                    sampling_steps=5,
                    scale=4,
                    compute_uncertainty=False,
                    scale_factor=10000.0,
                    patch_size=128,
                    overlap=16
                )
                print(f"[{pid}] Finished SR inference -> {sr_tif}", flush=True)
            else:
                print(f"[{pid}] Found cached SR TIFF: {sr_tif}", flush=True)
                
            with rasterio.open(sr_tif) as src:
                sr_data = src.read().astype(np.float32)
                # Rescale SR to 0..10000 if normalized
                if np.nanmax(sr_data) <= 2.0:
                    sr_data = sr_data * 10000.0
                    
            # --- DISPLAY NORMALIZATION (Skill Phase 6) ---
            # Compute stretch limits from NATIVE RGB ONLY (1st to 99th percentile)
            rgb_limits = []
            for b in range(3):
                valid = native_data[b][np.isfinite(native_data[b]) & (native_data[b] > 0)]
                lo, hi = np.percentile(valid, [1, 99])
                rgb_limits.append((float(lo), float(hi)))
                
            # CIR limits: Bands NIR, Red, Green = [3, 0, 1]
            cir_limits = []
            for b in [3, 0, 1]:
                valid = native_data[b][np.isfinite(native_data[b]) & (native_data[b] > 0)]
                lo, hi = np.percentile(valid, [1, 99])
                cir_limits.append((float(lo), float(hi)))
                
            # Generate RGB Images
            target_dim = (plot["out_sz"], plot["out_sz"])
            
            # Native RGB
            native_rgb_uint8 = stretch_to_uint8(native_data[:3], rgb_limits)
            native_rgb_pil = Image.fromarray(native_rgb_uint8).resize(target_dim, Image.Resampling.LANCZOS)
            
            # SR RGB
            sr_rgb_uint8 = stretch_to_uint8(sr_data[:3], rgb_limits)
            sr_rgb_pil = Image.fromarray(sr_rgb_uint8)
            assert sr_rgb_pil.size == target_dim, f"Dimension mismatch: {sr_rgb_pil.size} vs {target_dim}"
            
            # Native CIR & SR CIR
            native_cir_uint8 = stretch_to_uint8(native_data[[3, 0, 1]], cir_limits)
            native_cir_pil = Image.fromarray(native_cir_uint8).resize(target_dim, Image.Resampling.LANCZOS)
            
            sr_cir_uint8 = stretch_to_uint8(sr_data[[3, 0, 1]], cir_limits)
            sr_cir_pil = Image.fromarray(sr_cir_uint8)
            
            # NDVI
            native_ndvi_rgb, native_mean_ndvi = compute_ndvi_rgb(native_data[0], native_data[3])
            native_ndvi_pil = Image.fromarray(native_ndvi_rgb).resize(target_dim, Image.Resampling.LANCZOS)
            
            sr_ndvi_rgb, sr_mean_ndvi = compute_ndvi_rgb(sr_data[0], sr_data[3])
            sr_ndvi_pil = Image.fromarray(sr_ndvi_rgb)
            
            # Save WebP assets (Phase 7)
            rgb_10m = f"{web_dir}/{pid}-{date_str}-10m.webp"
            rgb_2p5m = f"{web_dir}/{pid}-{date_str}-2p5m.webp"
            cir_10m = f"{web_dir}/{pid}-{date_str}-cir-10m.webp"
            cir_2p5m = f"{web_dir}/{pid}-{date_str}-cir-2p5m.webp"
            ndvi_10m = f"{web_dir}/{pid}-{date_str}-ndvi-10m.webp"
            ndvi_2p5m = f"{web_dir}/{pid}-{date_str}-ndvi-2p5m.webp"
            
            native_rgb_pil.save(rgb_10m, "WEBP", quality=92)
            sr_rgb_pil.save(rgb_2p5m, "WEBP", quality=92)
            native_cir_pil.save(cir_10m, "WEBP", quality=92)
            sr_cir_pil.save(cir_2p5m, "WEBP", quality=92)
            native_ndvi_pil.save(ndvi_10m, "WEBP", quality=92)
            sr_ndvi_pil.save(ndvi_2p5m, "WEBP", quality=92)
            
            # QA Validation check (Skill Visual publish validation)
            for path, pil_img in [(rgb_10m, native_rgb_pil), (rgb_2p5m, sr_rgb_pil)]:
                stat = ImageStat.Stat(pil_img)
                extrema = stat.extrema
                assert any(high - low > 10 for low, high in extrema), f"Image flat/black: {path}"
                
            print(f"[{pid}] Saved WebP assets. Mean NDVI: Native={native_mean_ndvi:.3f}, SR={sr_mean_ndvi:.3f}")
            
            summary_entries.append({
                "id": pid,
                "label": plot["label"],
                "lon": plot["lon"],
                "lat": plot["lat"],
                "area_rai": plot["area_rai"],
                "date": date_str,
                "scene_id": scene_id,
                "tile": "47PPK",
                "crs": native_crs,
                "original_rgb": f"public/data/superres25/{pid}-{date_str}-10m.webp",
                "superres_rgb": f"public/data/superres25/{pid}-{date_str}-2p5m.webp",
                "original_cir": f"public/data/superres25/{pid}-{date_str}-cir-10m.webp",
                "superres_cir": f"public/data/superres25/{pid}-{date_str}-cir-2p5m.webp",
                "original_ndvi": f"public/data/superres25/{pid}-{date_str}-ndvi-10m.webp",
                "superres_ndvi": f"public/data/superres25/{pid}-{date_str}-ndvi-2p5m.webp",
                "stats": {
                    "native_rgb_nonzero_fraction": nonzero_fraction,
                    "native_mean_ndvi": round(native_mean_ndvi, 4),
                    "sr_mean_ndvi": round(sr_mean_ndvi, 4),
                    "rgb_stretch_percentile_limits": rgb_limits
                }
            })
            
    # Write summary.json (Skill Phase 8)
    summary_output = {
        "project": "nakhon-si-thammarat-mangrove-superres",
        "province": "นครศรีธรรมราช",
        "district": "เมือง/ท่าศาลา",
        "subdistrict": "ท่าศาลา",
        "model": "OpenSR LDSR-S2 Latent Diffusion",
        "scale": 4,
        "native_grid_m": 10.0,
        "output_grid_m": 2.5,
        "locations": summary_entries
    }
    
    with open(f"{web_dir}/summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_output, f, ensure_ascii=False, indent=2)
    print(f"\nWrote summary.json to {web_dir}/summary.json with {len(summary_entries)} entries.")

if __name__ == '__main__':
    main()
