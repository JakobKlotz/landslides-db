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
import contextily as cx

BASE_DIR = Path(__file__).resolve().parents[1]
PLOTS_DIR = BASE_DIR / "plots"
PLOTS_DIR.mkdir(exist_ok=True)



Session = create_db_session()
with Session() as session:
    landslide_view = gpd.read_postgis(
        "SELECT * FROM landslides_view", session.bind, geom_col="geom"
    )

## Plotting the landslide data

landslide_view_3857 = landslide_view.to_crs(epsg=3857)  # Web Mercator for contextily
fig, ax = plt.subplots(figsize=(10, 10))
landslide_view_3857.plot(ax=ax, column='classification_name', legend=True, markersize=5, cmap='Set1', alpha=0.8)
cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik, zoom='auto')
ax.set_title("Landslide Classifications")
ax.set_axis_off()
plt.title("Landslide Classifications")
fig.savefig(PLOTS_DIR / "classification_map.svg", dpi=300, bbox_inches="tight")


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
fig.savefig(PLOTS_DIR / "events_per_month.svg", dpi=300, bbox_inches="tight")

## Plot the number of events by year
landslide_view['event_year'] = landslide_view['event_date'].dt.year
year_counts = landslide_view['event_year'].value_counts().sort_index()
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
fig.savefig(PLOTS_DIR / "events_per_year.svg", dpi=300, bbox_inches="tight")

## Pie chart of landslide classifications with percentage labels
# Data
classification_counts = landslide_view['classification_name'].value_counts()
total = classification_counts.sum()

# Explode small slices
explode = [0.1 if (val / total) < 0.01 else 0 for val in classification_counts]

fig, ax = plt.subplots(figsize=(10, 6))

# Pie chart
wedges, texts, autotexts = ax.pie(
    classification_counts,
    labels=None,
    autopct=lambda p: f'{p:.2f}%' if p >= 1 else '',
    startangle=-20,
    pctdistance=0.8,
    explode=explode
)

# --- Annotation logic ---
for i, (wedge, count) in enumerate(zip(wedges, classification_counts)):
    percentage = count / total

    label_text = (
        f"{classification_counts.index[i]}\n"
        f"{percentage*100:.2f}% (N={count})"
    )

    if percentage < 0.01:
        # Mid-angle of slice
        ang = (wedge.theta2 + wedge.theta1) / 2
        ang_rad = np.deg2rad(ang)

        center, r = wedge.center, wedge.r

        # Small angular offset to reduce overlap
        ang_offset = (-8 if i % 2 == 0 else 8)
        ang_rad_shifted = np.deg2rad(ang + ang_offset)

        # Leader line start and end
        x_start = center[0] + r * np.cos(ang_rad)
        y_start = center[1] + r * np.sin(ang_rad)

        x_end = center[0] + 1.3 * r * np.cos(ang_rad_shifted)
        y_end = center[1] + 1.3 * r * np.sin(ang_rad_shifted)

        ax.plot([x_start, x_end], [y_start, y_end], color='gray', lw=0.8)

        ax.text(
            x_end + (0.02 if np.cos(ang_rad_shifted) > 0 else -0.02),
            y_end,
            label_text,
            ha='left' if np.cos(ang_rad_shifted) > 0 else 'right',
            va='center',
            fontsize=8
        )

    else:
        # Label directly on slice
        texts[i].set_text(label_text)
        texts[i].set_fontsize(8)

# Style percentage text inside slices
for autotext in autotexts:
    autotext.set_fontsize(8)
    autotext.set_color('black')
    autotext.set_weight('bold')

ax.axis('equal')
plt.title("Proportion of Landslide Classifications")
plt.tight_layout()

fig.savefig(PLOTS_DIR / "classification_piechart.svg", dpi=300, bbox_inches="tight")

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
# Rotate month numbers
plt.xticks(rotation=0)
plt.tight_layout()
fig.savefig(PLOTS_DIR / "events_per_month_by_classification.svg", dpi=300, bbox_inches="tight")
