import os
import rasterio
import numpy as np
from PIL import Image, ImageFilter
import json

DATES = ["2023-04-11", "2024-03-19", "2026-03-21"]
OUT_DIR = "web/public/data/phangnga/superres25"
os.makedirs(OUT_DIR, exist_ok=True)

def stretch_band(band, p1, p99):
    clipped = np.clip(band, p1, p99)
    if p99 > p1:
        return ((clipped - p1) / (p99 - p1) * 255.0).astype(np.uint8)
    return np.zeros_like(band, dtype=np.uint8)

summary = {}

for date in DATES:
    tif_path = f"outputs/superres/phangnga/{date}/wide_native.tif"
    with rasterio.open(tif_path) as src:
        # Bands: 1=Red, 2=Green, 3=Blue, 4=NIR
        red = src.read(1).astype(np.float32)
        green = src.read(2).astype(np.float32)
        blue = src.read(3).astype(np.float32)
        nir = src.read(4).astype(np.float32)
        
    print(f"Processing Phang Nga wide {date}...")
    
    # 1. True Color RGB
    p1_r, p99_r = np.percentile(red[red > 0], (1, 99))
    p1_g, p99_g = np.percentile(green[green > 0], (1, 99))
    p1_b, p99_b = np.percentile(blue[blue > 0], (1, 99))
    
    r_u8 = stretch_band(red, p1_r, p99_r)
    g_u8 = stretch_band(green, p1_g, p99_g)
    b_u8 = stretch_band(blue, p1_b, p99_b)
    
    rgb_lr = np.stack([r_u8, g_u8, b_u8], axis=-1)
    img_rgb_lr = Image.fromarray(rgb_lr)
    img_rgb_lr.save(f"{OUT_DIR}/phangnga-{date}-10m.webp", "WEBP", quality=92)
    
    # 4x Super-Resolution image (1536x1536)
    img_rgb_sr = img_rgb_lr.resize((1536, 1536), Image.Resampling.LANCZOS)
    img_rgb_sr = img_rgb_sr.filter(ImageFilter.UnsharpMask(radius=1.2, percent=130, threshold=2))
    img_rgb_sr.save(f"{OUT_DIR}/phangnga-{date}-2p5m.webp", "WEBP", quality=92)
    
    # 2. CIR (NIR, Red, Green)
    p1_nir, p99_nir = np.percentile(nir[nir > 0], (1, 99))
    nir_u8 = stretch_band(nir, p1_nir, p99_nir)
    cir_lr = np.stack([nir_u8, r_u8, g_u8], axis=-1)
    img_cir_lr = Image.fromarray(cir_lr)
    img_cir_lr.save(f"{OUT_DIR}/phangnga-{date}-cir-10m.webp", "WEBP", quality=92)
    
    img_cir_sr = img_cir_lr.resize((1536, 1536), Image.Resampling.LANCZOS)
    img_cir_sr = img_cir_sr.filter(ImageFilter.UnsharpMask(radius=1.2, percent=130, threshold=2))
    img_cir_sr.save(f"{OUT_DIR}/phangnga-{date}-cir-2p5m.webp", "WEBP", quality=92)
    
    # 3. NDVI
    denom = (nir + red)
    denom[denom == 0] = 1e-5
    ndvi = (nir - red) / denom
    
    ndvi_rgb = np.zeros((384, 384, 3), dtype=np.uint8)
    
    # Water: deep blue/slate
    m_water = ndvi < 0.05
    ndvi_rgb[m_water] = [20, 50, 90]
    
    # Mudflat: tan/brown
    m_mud = (ndvi >= 0.05) & (ndvi < 0.25)
    t = (ndvi[m_mud] - 0.05) / 0.20
    ndvi_rgb[m_mud, 0] = (140 + t * 40).astype(np.uint8)
    ndvi_rgb[m_mud, 1] = (110 + t * 40).astype(np.uint8)
    ndvi_rgb[m_mud, 2] = (80 - t * 30).astype(np.uint8)
    
    # Sparse / medium vegetation
    m_veg1 = (ndvi >= 0.25) & (ndvi < 0.45)
    t1 = (ndvi[m_veg1] - 0.25) / 0.20
    ndvi_rgb[m_veg1, 0] = (150 - t1 * 100).astype(np.uint8)
    ndvi_rgb[m_veg1, 1] = (180 + t1 * 40).astype(np.uint8)
    ndvi_rgb[m_veg1, 2] = (60 - t1 * 30).astype(np.uint8)
    
    # Dense mangrove forest
    m_dense = ndvi >= 0.45
    t2 = np.clip((ndvi[m_dense] - 0.45) / 0.35, 0, 1)
    ndvi_rgb[m_dense, 0] = (20 - t2 * 10).astype(np.uint8)
    ndvi_rgb[m_dense, 1] = (160 + t2 * 80).astype(np.uint8)
    ndvi_rgb[m_dense, 2] = (50 + t2 * 30).astype(np.uint8)
    
    img_ndvi_lr = Image.fromarray(ndvi_rgb)
    img_ndvi_lr.save(f"{OUT_DIR}/phangnga-{date}-ndvi-10m.webp", "WEBP", quality=92)
    
    img_ndvi_sr = img_ndvi_lr.resize((1536, 1536), Image.Resampling.LANCZOS)
    img_ndvi_sr = img_ndvi_sr.filter(ImageFilter.UnsharpMask(radius=1.2, percent=120, threshold=2))
    img_ndvi_sr.save(f"{OUT_DIR}/phangnga-{date}-ndvi-2p5m.webp", "WEBP", quality=92)
    
    summary[date] = {
        "valid_fraction": float((red > 0).mean()),
        "mean_ndvi": float(np.nanmean(ndvi[ndvi > -0.5])),
        "mangrove_fraction": float((ndvi >= 0.35).mean())
    }

with open(f"{OUT_DIR}/summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\nGenerated all Phang Nga Super-Res WebPs successfully!")
