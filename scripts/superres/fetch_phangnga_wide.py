import os
import rasterio
from rasterio.windows import Window
from rasterio.warp import transform_bounds
import numpy as np
import json

SCENES = {
    "2023-04-11": {
        "id": "S2B_47PMK_20230411_0_L2A",
        "date": "2023-04-11",
        "base_url": "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/47/P/MK/2023/4/S2B_47PMK_20230411_0_L2A"
    },
    "2024-03-19": {
        "id": "S2B_47PMK_20240319_0_L2A",
        "date": "2024-03-19",
        "base_url": "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/47/P/MK/2024/3/S2B_47PMK_20240319_0_L2A"
    },
    "2026-03-21": {
        "id": "S2C_47PMK_20260321_0_L2A",
        "date": "2026-03-21",
        "base_url": "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/47/P/MK/2026/3/S2C_47PMK_20260321_0_L2A"
    }
}

BANDS = [
    ("red", "B04.tif"),
    ("green", "B03.tif"),
    ("blue", "B02.tif"),
    ("nir", "B08.tif")
]

# Center in UTM 47N covering all 3 plots (40, 41, 42-VSD) in Phang Nga Bay
CX = 449470.30
CY = 923415.30
PATCH_SIZE = 384  # 384 x 10m = 3.84 km x 3.84 km

env = rasterio.Env(
    GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',
    VSI_CACHE=True
)

patch_bounds_wgs84 = None

with env:
    for date_key, scene in SCENES.items():
        print(f"\n--- Fetching Wide Sentinel-2 for Phang Nga ({date_key}) ---")
        out_dir = f"outputs/superres/phangnga/{date_key}"
        os.makedirs(out_dir, exist_ok=True)
        
        ref_url = f"{scene['base_url']}/B04.tif"
        with rasterio.open(ref_url) as ref_src:
            row, col = ref_src.index(CX, CY)
            half = PATCH_SIZE // 2
            col_off = col - half
            row_off = row - half
            win = Window(col_off, row_off, PATCH_SIZE, PATCH_SIZE)
            
            profile = ref_src.profile.copy()
            win_transform = ref_src.window_transform(win)
            profile.update({
                'count': 4,
                'height': PATCH_SIZE,
                'width': PATCH_SIZE,
                'transform': win_transform,
                'compress': 'deflate'
            })
            
            # Calculate WGS84 bounds
            native_bounds = rasterio.windows.bounds(win, ref_src.transform)
            wgs84_bounds = transform_bounds(ref_src.crs, 'EPSG:4326', *native_bounds)
            # Leaflet bounds: [[south, west], [north, east]]
            leaflet_bounds = [[wgs84_bounds[1], wgs84_bounds[0]], [wgs84_bounds[3], wgs84_bounds[2]]]
            if patch_bounds_wgs84 is None:
                patch_bounds_wgs84 = {
                    "native_bounds": native_bounds,
                    "wgs84_bounds": wgs84_bounds,
                    "leaflet_bounds": leaflet_bounds
                }
            
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
            print(f"Saved {out_tif}, shape: {stack.shape}, non-zero fraction: {(stack > 0).mean():.4f}")

# Save bounds metadata
meta_path = "outputs/superres/phangnga/bounds.json"
with open(meta_path, "w") as f:
    json.dump(patch_bounds_wgs84, f, indent=2)
print(f"\nSaved bounds to {meta_path}:")
print(json.dumps(patch_bounds_wgs84, indent=2))
