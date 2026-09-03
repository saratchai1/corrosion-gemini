import os
import rasterio
from rasterio.windows import Window
from pyproj import Transformer
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

PLOTS = [
    {"id": "22-vsd", "lon": 100.00318, "lat": 8.59360, "patch_size": 128},
    {"id": "23-vsd", "lon": 100.00218, "lat": 8.59597, "patch_size": 128},
    {"id": "combined-vsd", "lon": 100.00268, "lat": 8.59478, "patch_size": 256}
]

BANDS = [
    ("red", "B04.tif"),
    ("green", "B03.tif"),
    ("blue", "B02.tif"),
    ("nir", "B08.tif")
]

def main():
    env = rasterio.Env(
        GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',
        CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',
        VSI_CACHE=True
    )
    with env:
        for date_key, scene in SCENES.items():
            print(f"\n--- Scene {scene['id']} ({date_key}) ---", flush=True)
            out_dir = f"outputs/superres/nakhon/{date_key}"
            os.makedirs(out_dir, exist_ok=True)
            
            # Open red band to get transform & coords
            ref_url = f"{scene['base_url']}/B04.tif"
            with rasterio.open(ref_url) as ref_src:
                crs = ref_src.crs
                transformer = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
                
                # Precompute window for each plot
                plot_windows = {}
                for plot in PLOTS:
                    x, y = transformer.transform(plot["lon"], plot["lat"])
                    row, col = ref_src.index(x, y)
                    half = plot["patch_size"] // 2
                    win = Window(col - half, row - half, plot["patch_size"], plot["patch_size"])
                    tf = rasterio.windows.transform(win, ref_src.transform)
                    plot_windows[plot["id"]] = (win, tf, plot["patch_size"])
            
            # Now read each band once for all plots
            band_data = {p["id"]: [] for p in PLOTS}
            for band_name, band_file in BANDS:
                b_url = f"{scene['base_url']}/{band_file}"
                print(f"Reading {band_name} from {band_file}...", flush=True)
                with rasterio.open(b_url) as b_src:
                    for p in PLOTS:
                        pid = p["id"]
                        win, tf, sz = plot_windows[pid]
                        raw = b_src.read(1, window=win, boundless=True, fill_value=0).astype(np.float32)
                        data = np.clip(np.rint(raw), 0, 10000).astype(np.uint16)
                        band_data[pid].append(data)
                        
            # Save GeoTIFF for each plot
            for p in PLOTS:
                pid = p["id"]
                win, tf, sz = plot_windows[pid]
                stack = np.stack(band_data[pid], axis=0) # [4, H, W]
                nonzero = float(np.count_nonzero(stack[:3]) / stack[:3].size)
                print(f"  Plot {pid}: shape {stack.shape}, nonzero: {nonzero:.4f}", flush=True)
                
                tif_path = f"{out_dir}/{pid}_native.tif"
                with rasterio.open(
                    tif_path,
                    "w",
                    driver="GTiff",
                    width=sz,
                    height=sz,
                    count=4,
                    dtype="uint16",
                    crs=crs,
                    transform=tf,
                    tiled=True,
                    compress="deflate"
                ) as dst:
                    dst.write(stack)
                print(f"  Saved -> {tif_path}", flush=True)

if __name__ == '__main__':
    main()
