import geopandas as gpd
import matplotlib.pyplot as plt
from db.utils import create_db_session


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
plt.show()