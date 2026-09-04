import os
import glob
import rasterio
from rasterio.warp import transform_bounds, Resampling
from PIL import Image
import numpy as np
import json

def process_drone_2026():
    tif_candidates = glob.glob('data/drone/*22*VSD*.tif')
    if not tif_candidates:
        print("No completed .tif file found yet.")
        return
    
    drone_tif = None
    for f in tif_candidates:
        if "22 VSD 23VSD.tif" in f:
            drone_tif = f
            break
    if not drone_tif:
        drone_tif = tif_candidates[0]
        
    print(f"Processing: {drone_tif} ({os.path.getsize(drone_tif)/1e9:.2f} GB)")
    
    with rasterio.open(drone_tif) as src:
        crs = src.crs
        bounds = src.bounds
        w, h = src.width, src.height
        count = src.count
        print(f"  CRS: {crs}, Count: {count}, Dims: {w} x {h}")
        print(f"  Native bounds: {bounds}")
        
        bounds_wgs84 = transform_bounds(crs, 'EPSG:4326', *bounds)
        leaflet_bounds = [[bounds_wgs84[1], bounds_wgs84[0]], [bounds_wgs84[3], bounds_wgs84[2]]]
        print(f"  WGS84 Bounds: {bounds_wgs84}")
        print(f"  Leaflet Bounds: {leaflet_bounds}")
        
        # High resolution overview (4096px width)
        target_w = 4096
        target_h = int(target_w * h / w)
        out_shape = (target_h, target_w)
        print(f"  Reading HD overview {out_shape}...")
        
        r = src.read(1, out_shape=out_shape, resampling=Resampling.bilinear)
        g = src.read(2, out_shape=out_shape, resampling=Resampling.bilinear)
        b = src.read(3, out_shape=out_shape, resampling=Resampling.bilinear)
        
        r_u8 = np.clip(r, 0, 255).astype(np.uint8) if r.max() <= 255 else (r / r.max() * 255).astype(np.uint8)
        g_u8 = np.clip(g, 0, 255).astype(np.uint8) if g.max() <= 255 else (g / g.max() * 255).astype(np.uint8)
        b_u8 = np.clip(b, 0, 255).astype(np.uint8) if b.max() <= 255 else (b / b.max() * 255).astype(np.uint8)
        
        out_dir = "web/public/data/drone"
        os.makedirs(out_dir, exist_ok=True)
        
        if count >= 4:
            alpha = src.read(4, out_shape=out_shape, resampling=Resampling.bilinear)
            a_u8 = np.clip(alpha, 0, 255).astype(np.uint8) if alpha.max() <= 255 else (alpha / alpha.max() * 255).astype(np.uint8)
            rgba = np.stack([r_u8, g_u8, b_u8, a_u8], axis=-1)
            img = Image.fromarray(rgba, mode='RGBA')
        else:
            rgb = np.stack([r_u8, g_u8, b_u8, a_u8 if count >= 4 else 255], axis=-1) if count >= 4 else np.stack([r_u8, g_u8, b_u8], axis=-1)
            img = Image.fromarray(rgb, mode='RGB')
            
        out_webp_hd = f"{out_dir}/drone_2026_04_hd.webp"
        img.save(out_webp_hd, "WEBP", quality=92)
        print(f"  Saved {out_webp_hd} ({os.path.getsize(out_webp_hd)/1e6:.2f} MB)")
        
        img_std = img.resize((2048, int(2048 * h / w)), Image.Resampling.LANCZOS)
        out_webp_std = f"{out_dir}/drone_2026_04.webp"
        img_std.save(out_webp_std, "WEBP", quality=90)
        print(f"  Saved {out_webp_std} ({os.path.getsize(out_webp_std)/1e6:.2f} MB)")
        
        meta = {
            "title": "ภาพถ่ายโดรนความละเอียดสูง เม.ย. 2569 (UAV Drone Orthomosaic April 2026)",
            "date": "2026-04-05",
            "file": "drone_2026_04_hd.webp",
            "leaflet_bounds": leaflet_bounds,
            "crs": str(crs),
            "original_resolution_m": round((bounds.right - bounds.left) / w, 4),
            "original_dimensions": [w, h]
        }
        with open(f"{out_dir}/drone_2026_04_meta.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
        print("  Saved metadata to drone_2026_04_meta.json successfully!")

if __name__ == "__main__":
    process_drone_2026()
