import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from db.utils import create_db_session
import numpy as np
import folium
from folium.plugins import HeatMap
from folium.plugins import TimestampedGeoJson
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
PLOTS_DIR = BASE_DIR / "plots"
PLOTS_DIR.mkdir(exist_ok=True)



Session = create_db_session()
with Session() as session:
    landslide_view = gpd.read_postgis(
        "SELECT * FROM landslides_view", session.bind, geom_col="geom"
    )
#print(landslide_view)
print(list(landslide_view.columns))
#print(type(landslide_view))


## Plotting the landslide data
fig, ax = plt.subplots(figsize=(10, 10))
landslide_view.plot(ax=ax, column='classification_name', legend=True, markersize=5, cmap='Set1', alpha=0.8)
plt.title("Landslide Classifications")
fig.savefig(PLOTS_DIR / "classification_map.png", dpi=300, bbox_inches="tight")
plt.show()


## Plot the number of landslides by classification
classification_counts = landslide_view['classification_name'].value_counts()
ax = classification_counts.plot(kind='bar', figsize=(10, 6), color='skyblue', fontsize=6)

plt.title("Number of events by Classification")
plt.xticks(rotation=0)
plt.xlabel("Classification")
plt.ylabel("Number of events")

# Add counts on top of bars
for i, value in enumerate(classification_counts):
    plt.text(i, value + 0.5, str(value), ha='center', va='bottom', fontsize=8, fontweight='bold')

fig = ax.figure
fig.savefig(PLOTS_DIR / "classification_counts.png", dpi=300, bbox_inches="tight")
plt.show()


## Plot the number of events by month
landslide_view['event_date'] = gpd.pd.to_datetime(landslide_view['date'])
landslide_view['event_month'] = landslide_view['event_date'].dt.month
month_counts = landslide_view['event_month'].value_counts().sort_index()
ax = month_counts.plot(kind='bar', figsize=(10, 6), color='lightgreen', fontsize=6)

plt.title("Number of events by Month")
plt.xticks(rotation=0)
plt.xlabel("Month")
plt.ylabel("Number of events")

# Add counts on top of bars
for i, value in enumerate(month_counts):
    plt.text(i, value + 0.5, str(value), ha='center', va='bottom', fontsize=8, fontweight='bold')

fig = ax.figure
fig.savefig(PLOTS_DIR / "events_per_month.png", dpi=300, bbox_inches="tight")
plt.show()


## Plot the number of events by year
landslide_view['event_year'] = landslide_view['event_date'].dt.year
year_counts = landslide_view['event_year'].value_counts().sort_index()
# remove years that are NaN
year_counts = year_counts[year_counts.index.notna()]
# remove years that are less than 50 events
year_counts = year_counts[year_counts >= 50]
ax = year_counts.plot(kind='bar', figsize=(10, 6), color='salmon', fontsize=6)
plt.title("Number of events by Year (>=50)")
plt.xticks(rotation=90)
plt.xlabel("Year")
plt.ylabel("Number of events")
# Add counts on top of bars
for i, value in enumerate(year_counts):
    plt.text(i, value + 0.5, str(value), ha='center', va='bottom', fontsize=5, fontweight='bold')

fig = ax.figure
fig.savefig(PLOTS_DIR / "events_per_year.png", dpi=300, bbox_inches="tight")
plt.show()


## Pie chart of landslide classifications with percentage labels
# Data
classification_counts = landslide_view['classification_name'].value_counts()
total = classification_counts.sum()

# Compute explode values (optional)
explode = [0.1 if (val / total) < 0.01 else 0 for val in classification_counts]

fig, ax = plt.subplots(figsize=(10, 6))

# Create pie chart (no labels, we’ll handle manually)
wedges, texts, autotexts = ax.pie(
    classification_counts,
    labels=None,
    autopct=lambda p: f'{p:.2f}%' if p >= 1 else '',  # show % inside only if >=1%
    startangle=-20,
    pctdistance=0.8,
    explode=explode
)

# --- Leader line logic for <1% slices ---
for i, (wedge, count) in enumerate(zip(wedges, classification_counts)):
    percentage = count / total
    if percentage < 0.01:  # Only for small slices (<1%)
        # Compute the mid-angle of the slice
        ang = (wedge.theta2 + wedge.theta1) / 2
        # Convert angle to radians
        ang_rad = np.deg2rad(ang)

        # Get slice radius and center (accounting for explode)
        center, r = wedge.center, wedge.r

        # Slight angular offset to spread small slices apart visually
        ang_offset = (-8 if i % 2 == 0 else 8)
        ang_rad_shifted = np.deg2rad(ang + ang_offset)

        # Start point: true edge of the slice
        x_start = center[0] + r * np.cos(ang_rad)
        y_start = center[1] + r * np.sin(ang_rad)

        # End point: slightly angled outward
        x_end = center[0] + 1.3 * r * np.cos(ang_rad_shifted)
        y_end = center[1] + 1.3 * r * np.sin(ang_rad_shifted)

        # Draw leader line
        ax.plot([x_start, x_end], [y_start, y_end], color='gray', lw=0.8)

        # Label placement
        ax.text(x_end + (0.02 if np.cos(ang_rad_shifted) > 0 else -0.02),
                y_end,
                f"{classification_counts.index[i]}\n({percentage*100:.2f}%)",
                ha='left' if np.cos(ang_rad_shifted) > 0 else 'right',
                va='center',
                fontsize=8)
    else:
        # Normal label for ≥1% slices
        texts[i].set_text(f"{classification_counts.index[i]}")

# --- Style inside percentage text ---
for autotext in autotexts:
    autotext.set_fontsize(8)
    autotext.set_color('black')
    autotext.set_weight('bold')

ax.axis('equal')
plt.title("Proportion of Landslide Classifications")
plt.tight_layout()
fig.savefig(PLOTS_DIR / "classification_piechart.png", dpi=300, bbox_inches="tight")
plt.show()


## Plot the number of events per month in a bar plot with different colors for classifications
fig, ax = plt.subplots(figsize=(12, 8))

pivot = (
    landslide_view
    .groupby(['event_month', 'classification_name'])
    .size()
    .unstack(fill_value=0)
    .sort_index()
)

pivot.plot(kind='bar', stacked=True, ax=ax, figsize=(12, 8), colormap='Set1')

ax.set_title("Number of Events per Month by Classification")
ax.set_xlabel("Month")
ax.set_ylabel("Number of Events")
ax.legend(title="Classification", bbox_to_anchor=(1.05, 1), loc='upper left')
# 🔄 Rotate month numbers
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()


## Create a heatmap of landslide density over Austria using Folium 
# (double click on the html file outside of vscode to open)
landslide_latlon = landslide_view.to_crs(epsg=4326)

# --- Drop missing geometries ---
landslide_latlon = landslide_latlon[landslide_latlon.geometry.notnull()]

# --- Extract coordinates safely ---
heat_data = [(geom.y, geom.x) for geom in landslide_latlon.geometry]

# --- Create base map centered on Austria ---
m = folium.Map(location=[47.5162, 14.5501], zoom_start=7, tiles='OpenStreetMap')

# --- Add HeatMap layer ---
HeatMap(
    data=heat_data,
    radius=10,       # controls spread of each point
    blur=15,         # controls smoothness
    max_zoom=8,
    min_opacity=0.5
).add_to(m)

# --- Save and show ---
m.save("austria_landslide_density.html")
m


## Timeslider classification slider
# -------------------------------------------------------
# 1. PREPARE & CLEAN DATA
# -------------------------------------------------------
events = landslide_view.to_crs(epsg=4326).copy()

# Drop invalid geometry
events = events[events.geometry.notnull()]
events = events[events.geometry.type == "Point"]

# Fix date parsing
events["event_date"] = pd.to_datetime(
    events["event_date"],
    errors="coerce",
    infer_datetime_format=True
)

# Fix year-only strings (e.g., "1956")
mask_year_only = events["event_date"].isna() & events["event_date"].astype(str).str.match(r"^\d{4}$")
events.loc[mask_year_only, "event_date"] = pd.to_datetime(
    events.loc[mask_year_only, "event_date"].astype(str) + "-01-01"
)

# Drop rows still missing dates
events = events[events["event_date"].notnull()]

# -----------------------------
# Filter to 1970-2025
# -----------------------------
events = events[(events["event_date"].dt.year >= 1970) & 
                (events["event_date"].dt.year <= 2025)]

# Create timestamp string
events["time"] = events["event_date"].dt.strftime("%Y-%m-%d")

#print("Date range:", events["event_date"].min(), "→", events["event_date"].max())

# -------------------------------------------------------
# 2. CLASSIFICATION COLORS
# -------------------------------------------------------
classifications = events["classification_name"].unique()
cmap = plt.get_cmap("Set1")
colors = [mcolors.to_hex(cmap(i / (len(classifications)-1))) 
          for i in range(len(classifications))]
color_map = dict(zip(classifications, colors))

# -------------------------------------------------------
# 3. BUILD FEATURES
# -------------------------------------------------------
features = []

for geom, date_string, cls in zip(
    events.geometry,
    events["time"],
    events["classification_name"]
):
    lon, lat = geom.x, geom.y
    color = color_map.get(cls, "#000000")

    feature = {
    "type": "Feature",
    "geometry": {"type": "Point", "coordinates": [lon, lat]},
    "properties": {
        "time": date_string,
        "popup": f"Classification: {cls}<br>Date: {date_string}",
        "icon": "circle",
        "iconstyle": {
            "fillColor": color,
            "fillOpacity": 0.8,
            "stroke": False,   # <- remove outlines
            "radius": 2,       # small dots
        },
    },
}
    features.append(feature)

geojson_data = {"type": "FeatureCollection", "features": features}

# -------------------------------------------------------
# 4. FOLIUM MAP
# -------------------------------------------------------
m = folium.Map(location=[47.5162, 14.5501], zoom_start=7, tiles="CartoDB positron")

TimestampedGeoJson(
    data=geojson_data,
    period="P1Y",
    add_last_point=True,
    auto_play=False,
    loop=False,
    max_speed=1,
    loop_button=True,
    date_options="YYYY-MM-DD",
    time_slider_drag_update=True,
).add_to(m)

# -------------------------------------------------------
# 5. LEGEND
# -------------------------------------------------------
legend_html = """
<div style="
     position: fixed; 
     bottom: 50px; left: 50px;
     width: 240px;
     background-color: white; 
     padding: 10px;
     border:2px solid grey; 
     z-index:9999;
     font-size: 14px;">
<b>Landslide Classifications</b><br>
"""
for cls in classifications:
    legend_html += f"<i style='background:{color_map[cls]};width:12px;height:12px;display:inline-block;margin-right:6px;'></i>{cls}<br>"
legend_html += "</div>"

m.get_root().html.add_child(folium.Element(legend_html))

m.save("austria_landslides_timeslider_points.html")
m