import os
import rasterio
from rasterio.windows import Window
import numpy as np

SCENES = {
    "2023-04-06": {
        "id": "S2A_47PPK_20230406_0_L2A",
        "date": "2023-04-06",
        "base_url": "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/47/P/PK/2023/4/S2A_47PPK_20230406_0_L2A"
    },
    "2024-04-05": {
        "id": "S2B_47PPK_20240405_0_L2A",
        "date": "2024-04-05",
        "base_url": "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/47/P/PK/2024/4/S2B_47PPK_20240405_0_L2A"
    },
    "2026-04-05": {
        "id": "S2B_47PPK_20260405_0_L2A",
        "date": "2026-04-05",
        "base_url": "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/47/P/PK/2026/4/S2B_47PPK_20260405_0_L2A"
    }
}

BANDS = [
    ("red", "B04.tif"),
    ("green", "B03.tif"),
    ("blue", "B02.tif"),
    ("nir", "B08.tif")
]

# Center in UTM 47N covering all of 22-VSD and 23-VSD
CX = 610446.65
CY = 949982.1
PATCH_SIZE = 384  # 384 x 10m = 3.84 km x 3.84 km

env = rasterio.Env(
    GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',
    VSI_CACHE=True
)

with env:
    for date_key, scene in SCENES.items():
        print(f"\n--- Fetching Wide Sentinel-2 for {date_key} ---")
        out_dir = f"outputs/superres/nakhon/{date_key}"
        os.makedirs(out_dir, exist_ok=True)
        
        ref_url = f"{scene['base_url']}/B04.tif"
        with rasterio.open(ref_url) as ref_src:
            row, col = ref_src.index(CX, CY)
            half = PATCH_SIZE // 2
            col_off = col - half
            row_off = row - half
            win = Window(col_off, row_off, PATCH_SIZE, PATCH_SIZE)
            
            profile = ref_src.profile.copy()
            profile.update({
                'count': 4,
                'height': PATCH_SIZE,
                'width': PATCH_SIZE,
                'transform': ref_src.window_transform(win),
                'compress': 'deflate'
            })
            
            bands_data = []
            for bname, fname in BANDS:
                b_url = f"{scene['base_url']}/{fname}"
                with rasterio.open(b_url) as b_src:
                    arr = b_src.read(1, window=win)
                    bands_data.append(arr)
            
            stack = np.stack(bands_data, axis=0)
            out_tif = f"{out_dir}/wide_native.tif"
            with rasterio.open(out_tif, 'w', **profile) as dst:
                dst.write(stack)
            print(f"Saved {out_tif}, shape: {stack.shape}, non-zero: {(stack > 0).mean():.4f}")

print("\nDone fetching all wide scenes!")
