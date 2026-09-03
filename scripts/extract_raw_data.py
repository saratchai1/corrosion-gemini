import os
import json
import shapely
import geopandas as gpd
import pandas as pd

def extract_kmz_plots():
    kmz_path = 'raw/STC_VSD_EVR.kmz'
    layer_name = 'STC_VSD_EVR (#2)'
    print(f"Reading {kmz_path}, layer: {layer_name}")
    gdf = gpd.read_file(kmz_path, layer=layer_name)
    
    # Filter for Nakhon Si Thammarat
    nst = gdf[gdf['Name'].astype(str).str.contains('นครศรีธรรมราช', na=False)].copy()
    print(f"Found {len(nst)} matching records for Nakhon Si Thammarat")
    
    # Clean geometry: force 2D, make_valid
    nst['geometry'] = nst.geometry.apply(lambda g: shapely.make_valid(shapely.force_2d(g)))
    
    # Identify unique plots: 22-VSD and 23-VSD
    plot_22 = nst[nst['Name'].str.contains('22-VSD')].copy()
    plot_23 = nst[nst['Name'].str.contains('23-VSD')].copy()
    
    # Pick the most updated geometry (e.g. 300.64 rai)
    if len(plot_22) > 1:
        plot_22 = plot_22[plot_22['Name'].str.contains('300.64')].iloc[:1]
    if len(plot_23) > 1:
        plot_23 = plot_23.iloc[:1]
        
    plot_22['plot_id'] = '22-vsd'
    plot_22['label'] = 'แปลง 22-VSD'
    plot_22['area_rai'] = 300.64
    plot_22['province'] = 'นครศรีธรรมราช'
    plot_22['subdistrict'] = 'ท่าศาลา'
    plot_22['district'] = 'เมือง/ท่าศาลา'
    plot_22['land_type'] = 'พื้นที่เลนงอก'
    
    plot_23['plot_id'] = '23-vsd'
    plot_23['label'] = 'แปลง 23-VSD'
    plot_23['area_rai'] = 200.12
    plot_23['province'] = 'นครศรีธรรมราช'
    plot_23['subdistrict'] = 'ท่าศาลา'
    plot_23['district'] = 'เมือง/ท่าศาลา'
    plot_23['land_type'] = 'พื้นที่เลนงอก'
    
    combined = pd.concat([plot_22, plot_23], ignore_index=True)
    combined = gpd.GeoDataFrame(combined, geometry='geometry', crs=gdf.crs)
    
    # Save individual and combined GeoJSON
    os.makedirs('data/aoi', exist_ok=True)
    os.makedirs('web/public/data', exist_ok=True)
    
    plot_22.to_file('data/aoi/plot_22_vsd.geojson', driver='GeoJSON')
    plot_23.to_file('data/aoi/plot_23_vsd.geojson', driver='GeoJSON')
    combined.to_file('data/aoi/nakhon_plots_combined.geojson', driver='GeoJSON')
    combined.to_file('web/public/data/nakhon_plots_combined.geojson', driver='GeoJSON')
    
    print("Exported GeoJSON files to data/aoi/ and web/public/data/")
    return combined

def extract_excel_registry():
    excel_path = 'raw/ข้อมูลเรื่องกล้าไม้ ปี 2565 31.08.2569.xlsx'
    df = pd.read_excel(excel_path, header=3)
    prov_col = [c for c in df.columns if 'จังหวัด' in str(c)][0]
    nst_df = df[df[prov_col].astype(str).str.contains('นครศรีธรรมราช')].copy()
    
    registry = {
        "project_name": "โครงการปลูกป่าเพื่อประโยชน์จากคาร์บอนเครดิต",
        "tver_type": "MOC 1-VSD Premium",
        "province": "นครศรีธรรมราช",
        "total_area_rai": 500.76,
        "plots": [
            {
                "plot_id": "22-vsd",
                "label": "แปลง 22-VSD",
                "area_rai": 300.64,
                "land_type": "พื้นที่เลนงอก",
                "planting_finish_date": "2023-05-29",
                "seedlings": [
                    {"species_thai": "โกงกางใบใหญ่", "species_sci": "Rhizophora mucronata", "count": 200000, "type": "ฝัก/ต้น"},
                    {"species_thai": "โกงกางใบเล็ก", "species_sci": "Rhizophora apiculata", "count": 10000, "type": "ฝัก/ต้น"},
                    {"species_thai": "แสมขาว", "species_sci": "Avicennia alba", "count": 3757, "type": "ฝัก/ต้น"}
                ],
                "maintenance_replanting": [
                    {"date": "2026-07-07", "species_thai": "โกงกางใบใหญ่", "count": 7104, "type": "ฝัก"},
                    {"date": "2026-07-20", "species_thai": "โกงกางใบใหญ่", "count": 7104, "type": "ฝัก"}
                ],
                "total_planted_initial": 213757,
                "centroid": {"lat": 8.59360, "lon": 100.00318}
            },
            {
                "plot_id": "23-vsd",
                "label": "แปลง 23-VSD",
                "area_rai": 200.12,
                "land_type": "พื้นที่เลนงอก",
                "planting_finish_date": "2023-05-29",
                "seedlings": [
                    {"species_thai": "โกงกางใบใหญ่", "species_sci": "Rhizophora mucronata", "count": 130000, "type": "ฝัก/ต้น"},
                    {"species_thai": "โกงกางใบเล็ก", "species_sci": "Rhizophora apiculata", "count": 10000, "type": "ฝัก/ต้น"},
                    {"species_thai": "แสมขาว", "species_sci": "Avicennia alba", "count": 2288, "type": "ฝัก/ต้น"}
                ],
                "maintenance_replanting": [],
                "total_planted_initial": 142288,
                "centroid": {"lat": 8.59597, "lon": 100.00218}
            }
        ],
        "summary": {
            "grand_total_seedlings": 356045,
            "species_breakdown": {
                "โกงกางใบใหญ่": 330000,
                "โกงกางใบเล็ก": 20000,
                "แสมขาว": 6045
            },
            "species_percentage": {
                "โกงกางใบใหญ่": 92.68,
                "โกงกางใบเล็ก": 5.62,
                "แสมขาว": 1.70
            }
        }
    }
    
    with open('web/public/data/seedling_registry.json', 'w', encoding='utf-8') as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    print("Exported seedling registry to web/public/data/seedling_registry.json")

if __name__ == '__main__':
    extract_kmz_plots()
    extract_excel_registry()
