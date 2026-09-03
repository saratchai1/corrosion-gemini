import os
import glob
import rasterio
from rasterio.warp import transform_bounds, calculate_default_transform, reproject, Resampling
from PIL import Image
import numpy as np

def main():
    tif_files = glob.glob('data/drone/*.tif')
    if not tif_files:
        print("No completed .tif file found in data/drone yet.")
        return
        
    drone_tif = tif_files[0]
    print(f"Opening drone GeoTIFF: {drone_tif} ({os.path.getsize(drone_tif) / 1e9:.2f} GB)")
    
    with rasterio.open(drone_tif) as src:
        crs = src.crs
        bounds = src.bounds
        w, h = src.width, src.height
        count = src.count
        print(f"  CRS: {crs}")
        print(f"  Dimensions: {w} x {h}, Bands: {count}")
        print(f"  Native bounds: {bounds}")
        
        # Transform bounds to WGS84 (EPSG:4326)
        bounds_wgs84 = transform_bounds(crs, 'EPSG:4326', *bounds)
        leaflet_bounds = [[bounds_wgs84[1], bounds_wgs84[0]], [bounds_wgs84[3], bounds_wgs84[2]]]
        print(f"  WGS84 Bounds [south, west, north, east]: {bounds_wgs84}")
        print(f"  Leaflet Bounds: {leaflet_bounds}")
        
        # Read downsampled overview for fast web display (e.g. 2048 x 2048 or 4096 x 4096)
        # Using rasterio overviews or decimation
        target_size = 2048
        out_shape = (target_size, int(target_size * h / w)) if w >= h else (int(target_size * w / h), target_size)
        print(f"  Reading downsampled RGB array {out_shape} for web...")
        
        # Read bands (typically 1=R, 2=G, 3=B or with Alpha)
        r = src.read(1, out_shape=out_shape, resampling=Resampling.bilinear)
        g = src.read(2, out_shape=out_shape, resampling=Resampling.bilinear)
        b = src.read(3, out_shape=out_shape, resampling=Resampling.bilinear)
        
        # Check alpha if 4 bands
        if count >= 4:
            alpha = src.read(4, out_shape=out_shape, resampling=Resampling.bilinear)
            # Normalize and create RGBA
            r_u8 = np.clip(r, 0, 255).astype(np.uint8) if r.max() <= 255 else (r / r.max() * 255).astype(np.uint8)
            g_u8 = np.clip(g, 0, 255).astype(np.uint8) if g.max() <= 255 else (g / g.max() * 255).astype(np.uint8)
            b_u8 = np.clip(b, 0, 255).astype(np.uint8) if b.max() <= 255 else (b / b.max() * 255).astype(np.uint8)
            a_u8 = np.clip(alpha, 0, 255).astype(np.uint8) if alpha.max() <= 255 else (alpha / alpha.max() * 255).astype(np.uint8)
            rgba = np.stack([r_u8, g_u8, b_u8, a_u8], axis=-1)
            img = Image.fromarray(rgba, mode='RGBA')
        else:
            r_u8 = np.clip(r, 0, 255).astype(np.uint8) if r.max() <= 255 else (r / r.max() * 255).astype(np.uint8)
            g_u8 = np.clip(g, 0, 255).astype(np.uint8) if g.max() <= 255 else (g / g.max() * 255).astype(np.uint8)
            b_u8 = np.clip(b, 0, 255).astype(np.uint8) if b.max() <= 255 else (b / b.max() * 255).astype(np.uint8)
            rgb = np.stack([r_u8, g_u8, b_u8], axis=-1)
            img = Image.fromarray(rgb, mode='RGB')
            
        out_dir = "web/public/data/drone"
        os.makedirs(out_dir, exist_ok=True)
        out_webp = f"{out_dir}/drone_ortho.webp"
        img.save(out_webp, "WEBP", quality=90)
        print(f"Saved optimized web orthomosaic to {out_webp} ({os.path.getsize(out_webp) / 1e6:.2f} MB)")
        
        # Save bounds JSON for app.js
        import json
        metadata = {
            "file": "drone_ortho.webp",
            "leaflet_bounds": leaflet_bounds,
            "crs": str(crs),
            "original_resolution_m": round(bounds.width / w, 4) if hasattr(bounds, 'width') else round((bounds.right - bounds.left) / w, 4),
            "original_dimensions": [w, h]
        }
        with open(f"{out_dir}/drone_meta.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        print("Saved drone_meta.json successfully!")

if __name__ == "__main__":
    main()
