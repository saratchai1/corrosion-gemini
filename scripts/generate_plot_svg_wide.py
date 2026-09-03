import rasterio
import geopandas as gpd
import json

gdf = gpd.read_file('web/public/data/nakhon_plots_combined.geojson')
result = {}

tif_path = 'outputs/superres/nakhon/2026-04-05/wide_native.tif'
with rasterio.open(tif_path) as src:
    w, h = src.width, src.height
    tf = src.transform
    inv_tf = ~tf
    crs = src.crs
    
    gdf_proj = gdf.to_crs(crs)
    plot_items = []
    
    for idx, row in gdf_proj.iterrows():
        geom = row.geometry
        name = str(row.get('Name', '') or row.get('plot_id', ''))
        is22 = '22' in name
        pid = '22-vsd' if is22 else '23-vsd'
        label = 'แปลง 22-VSD (300.64 ไร่)' if is22 else 'แปลง 23-VSD (200.12 ไร่)'
        
        geoms = [geom] if geom.geom_type == 'Polygon' else list(geom.geoms)
        svg_paths = []
        
        for g in geoms:
            coords = list(g.exterior.coords)
            px_coords = [inv_tf * (x, y) for x, y in coords]
            # Scale to 0..1000 viewBox coordinates
            svg_pts = [f"{round(col / w * 1000.0, 1)},{round(row_idx / h * 1000.0, 1)}" for col, row_idx in px_coords]
            svg_paths.append("M " + " L ".join(svg_pts) + " Z")
            
        c_x, c_y = geom.centroid.x, geom.centroid.y
        px_cx, px_cy = inv_tf * (c_x, c_y)
        centroid_1000 = {
            "x": round(px_cx / w * 1000.0, 1),
            "y": round(px_cy / h * 1000.0, 1)
        }
        
        plot_items.append({
            "id": pid,
            "label": label,
            "color": "#10b981" if is22 else "#38bdf8",
            "fillColor": "rgba(16, 185, 129, 0.12)" if is22 else "rgba(56, 189, 248, 0.12)",
            "paths": svg_paths,
            "centroid": centroid_1000
        })
        
    result["combined-vsd"] = plot_items
    result["22-vsd"] = plot_items
    result["23-vsd"] = plot_items

out_file = 'web/public/data/plot_boundaries_svg.json'
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"Generated wide {out_file} successfully!")
for p in plot_items:
    print(p["id"], "centroid:", p["centroid"])
