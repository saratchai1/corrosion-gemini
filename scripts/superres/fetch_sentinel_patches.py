import os
import json
import rasterio
from rasterio.windows import Window
from pyproj import Transformer
import numpy as np
from PIL import Image

SCENES = {
    "2023-04-06": {
        "id": "S2A_47PPK_20230406_0_L2A",
        "date": "2023-04-06",
        "label": "เมษายน 2566 (ก่อนเริ่มปลูก/ช่วงเตรียมพื้นที่)",
        "phase": "Baseline",
        "cloud_cover": 7.9,
        "base_url": "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/47/P/PK/2023/4/S2A_47PPK_20230406_0_L2A"
    },
    "2024-04-05": {
        "id": "S2B_47PPK_20240405_0_L2A",
        "date": "2024-04-05",
        "label": "เมษายน 2567 (1 ปีหลังปลูก - เริ่มแตกยอด)",
        "phase": "Year 1 Monitoring",
        "cloud_cover": 4.8,
        "base_url": "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/47/P/PK/2024/4/S2B_47PPK_20240405_0_L2A"
    },
    "2026-04-05": {
        "id": "S2B_47PPK_20260405_0_L2A",
        "date": "2026-04-05",
        "label": "เมษายน 2569 (3 ปีหลังปลูก - ฟื้นฟูดินงอก)",
        "phase": "Year 3 Full Canopy",
        "cloud_cover": 0.3,
        "base_url": "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/47/P/PK/2026/4/S2B_47PPK_20260405_0_L2A"
    }
}

PLOTS = [
    {
        "id": "22-vsd",
        "label": "แปลง 22-VSD",
        "lon": 100.00318,
        "lat": 8.59360,
        "area_rai": 300.64,
        "patch_size": 128
    },
    {
        "id": "23-vsd",
        "label": "แปลง 23-VSD",
        "lon": 100.00218,
        "lat": 8.59597,
        "area_rai": 200.12,
        "patch_size": 128
    },
    {
        "id": "combined-vsd",
        "label": "ภาพรวมโครงการ 22-VSD & 23-VSD",
        "lon": 100.00268,
        "lat": 8.59478,
        "area_rai": 500.76,
        "patch_size": 256
    }
]

BANDS = [
    ("red", "B04.tif"),
    ("green", "B03.tif"),
    ("blue", "B02.tif"),
    ("nir", "B08.tif")
]

def fetch_and_save_native():
    for date_key, scene in SCENES.items():
        print(f"\n================ Processing Scene {scene['id']} ({date_key}) ================")
        out_dir = f"outputs/superres/nakhon/{date_key}"
        os.makedirs(out_dir, exist_ok=True)
        
        red_url = f"{scene['base_url']}/B04.tif"
        with rasterio.open(red_url) as ref_src:
            crs = ref_src.crs
            transformer = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
            
            for plot in PLOTS:
                plot_id = plot["id"]
                patch_size = plot["patch_size"]
                half = patch_size // 2
                
                x, y = transformer.transform(plot["lon"], plot["lat"])
                row, col = ref_src.index(x, y)
                window = Window(col - half, row - half, patch_size, patch_size)
                transform = rasterio.windows.transform(window, ref_src.transform)
                
                band_arrays = []
                for band_name, band_file in BANDS:
                    b_url = f"{scene['base_url']}/{band_file}"
                    with rasterio.open(b_url) as b_src:
                        raw = b_src.read(1, window=window, boundless=True, fill_value=0).astype(np.float32)
                        data = np.clip(np.rint(raw), 0, 10000).astype(np.uint16)
                        band_arrays.append(data)
                        
                stack = np.stack(band_arrays, axis=0) # [4, H, W] = [R, G, B, NIR]
                nonzero_fraction = float(np.count_nonzero(stack[:3]) / stack[:3].size)
                print(f"[{plot_id}] {date_key}: stack shape {stack.shape}, nonzero {nonzero_fraction:.4f}")
                assert nonzero_fraction > 0.85, f"Low nonzero fraction {nonzero_fraction}"
                
                tif_path = f"{out_dir}/{plot_id}_native.tif"
                with rasterio.open(
                    tif_path,
                    "w",
                    driver="GTiff",
                    width=patch_size,
                    height=patch_size,
                    count=4,
                    dtype="uint16",
                    crs=crs,
                    transform=transform,
                    tiled=True,
                    compress="deflate"
                ) as dst:
                    dst.write(stack)
                print(f"  Saved {tif_path}")

if __name__ == '__main__':
    fetch_and_save_native()
