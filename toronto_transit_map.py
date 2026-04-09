"""
Toronto Transit Accessibility Map
---------------------------------
A geospatial visualization of TTC Line 1 subway stations across Toronto,
classified by zone and annotated with approximate daily ridership.

Author: Hamza Faruqui
Tools:  Python, pandas, folium (interactive) + matplotlib (static export)
"""

import pandas as pd
import folium
from folium.plugins import MarkerCluster

# -------------------------------------------------------------------
# 1. Dataset: TTC Line 1 (Yonge-University) stations
#    Coordinates are real; ridership figures are approximate daily boardings.
# -------------------------------------------------------------------
stations = pd.DataFrame([
    # name,              lat,       lon,       zone,         ridership
    ["Union",             43.6453, -79.3806, "Downtown",    75000],
    ["King",              43.6492, -79.3779, "Downtown",    52000],
    ["Queen",             43.6525, -79.3791, "Downtown",    48000],
    ["Dundas",            43.6561, -79.3802, "Downtown",    56000],
    ["College",           43.6612, -79.3831, "Downtown",    33000],
    ["Wellesley",         43.6655, -79.3841, "Downtown",    24000],
    ["Bloor-Yonge",       43.6710, -79.3857, "Midtown",     95000],
    ["Rosedale",          43.6770, -79.3890, "Midtown",     12000],
    ["Summerhill",        43.6821, -79.3897, "Midtown",      9000],
    ["St. Clair",         43.6878, -79.3930, "Midtown",     26000],
    ["Davisville",        43.6981, -79.3976, "Midtown",     22000],
    ["Eglinton",          43.7063, -79.3986, "Midtown",     45000],
    ["Lawrence",          43.7253, -79.4023, "North York",  18000],
    ["York Mills",        43.7438, -79.4064, "North York",  21000],
    ["Sheppard-Yonge",    43.7615, -79.4110, "North York",  41000],
    ["North York Centre", 43.7684, -79.4125, "North York",  19000],
    ["Finch",             43.7805, -79.4149, "North York",  52000],
    ["St. George",        43.6684, -79.3995, "Downtown",    63000],
    ["Museum",            43.6674, -79.3939, "Downtown",    11000],
    ["Queen's Park",      43.6597, -79.3903, "Downtown",    14000],
], columns=["name", "lat", "lon", "zone", "ridership"])

# -------------------------------------------------------------------
# 2. Basic spatial summary (demonstrates simple geospatial analysis)
# -------------------------------------------------------------------
zone_summary = (
    stations.groupby("zone")
    .agg(stations=("name", "count"),
         avg_ridership=("ridership", "mean"),
         total_ridership=("ridership", "sum"))
    .round(0)
    .sort_values("total_ridership", ascending=False)
)
print("Ridership summary by zone:")
print(zone_summary)
print()

centroid_lat = stations["lat"].mean()
centroid_lon = stations["lon"].mean()
print(f"Network centroid: ({centroid_lat:.4f}, {centroid_lon:.4f})")

# -------------------------------------------------------------------
# 3. Build interactive Folium map
# -------------------------------------------------------------------
zone_colors = {
    "Downtown":   "red",
    "Midtown":    "blue",
    "North York": "green",
}

m = folium.Map(
    location=[centroid_lat, centroid_lon],
    zoom_start=12,
    tiles="CartoDB positron",
)

# Marker cluster for clean display
cluster = MarkerCluster(name="TTC Stations").add_to(m)

for _, row in stations.iterrows():
    # Scale marker radius by ridership (simple data-driven symbology)
    radius = 4 + (row["ridership"] / 10000)
    popup_html = (
        f"<b>{row['name']}</b><br>"
        f"Zone: {row['zone']}<br>"
        f"Daily riders: {row['ridership']:,}"
    )
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=radius,
        color=zone_colors[row["zone"]],
        fill=True,
        fill_opacity=0.75,
        popup=folium.Popup(popup_html, max_width=220),
        tooltip=row["name"],
    ).add_to(cluster)

# Draw the subway line roughly in station order (spatial connection)
line_coords = stations.sort_values("lat")[["lat", "lon"]].values.tolist()
folium.PolyLine(line_coords, color="#444", weight=2, opacity=0.6,
                tooltip="TTC Line 1 (approx.)").add_to(m)

folium.LayerControl().add_to(m)
m.save("/home/claude/toronto_transit_map.html")
print("Interactive map saved to toronto_transit_map.html")
