import os
import glob
import rasterio
from rasterio.warp import transform_bounds, Resampling
from PIL import Image
import numpy as np
import json

def process_phangnga_drone():
    tif_candidates = glob.glob('data/drone/phangnga/*.tif')
    if not tif_candidates:
        print("No completed .tif file found in data/drone/phangnga yet.")
        return
    
    out_dir = "web/public/data/phangnga/drone"
    os.makedirs(out_dir, exist_ok=True)
    
    for drone_tif in tif_candidates:
        bname = os.path.basename(drone_tif)
        stem = os.path.splitext(bname)[0].replace(' ', '_').replace('..', '').lower()
        out_webp_hd = f"{out_dir}/{stem}_hd.webp"
        if os.path.exists(out_webp_hd):
            print(f"Skipping already processed: {out_webp_hd}")
            continue

        size_gb = os.path.getsize(drone_tif) / 1e9
        print(f"\nProcessing Phang Nga drone: {drone_tif} ({size_gb:.2f} GB)")
        
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
            
            if count >= 4:
                alpha = src.read(4, out_shape=out_shape, resampling=Resampling.bilinear)
                a_u8 = np.clip(alpha, 0, 255).astype(np.uint8) if alpha.max() <= 255 else (alpha / alpha.max() * 255).astype(np.uint8)
                rgba = np.stack([r_u8, g_u8, b_u8, a_u8], axis=-1)
                img = Image.fromarray(rgba, mode='RGBA')
            else:
                rgb = np.stack([r_u8, g_u8, b_u8], axis=-1)
                img = Image.fromarray(rgb, mode='RGB')
                
            out_webp_hd = f"{out_dir}/{stem}_hd.webp"
            img.save(out_webp_hd, "WEBP", quality=92)
            print(f"  Saved {out_webp_hd} ({os.path.getsize(out_webp_hd)/1e6:.2f} MB)")
            
            img_std = img.resize((2048, int(2048 * h / w)), Image.Resampling.LANCZOS)
            out_webp_std = f"{out_dir}/{stem}.webp"
            img_std.save(out_webp_std, "WEBP", quality=90)
            print(f"  Saved {out_webp_std} ({os.path.getsize(out_webp_std)/1e6:.2f} MB)")
            
            meta = {
                "title": f"ภาพถ่ายโดรนความละเอียดสูง {bname} จ.พังงา",
                "file": f"{stem}_hd.webp",
                "leaflet_bounds": leaflet_bounds,
                "crs": str(crs),
                "original_dimensions": [w, h]
            }
            with open(f"{out_dir}/{stem}_meta.json", "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2, ensure_ascii=False)
            print(f"  Saved metadata to {stem}_meta.json")

if __name__ == "__main__":
    process_phangnga_drone()
