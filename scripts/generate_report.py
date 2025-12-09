import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from db.utils import create_db_session
from pathlib import Path
import pandas as pd


# Basis-Pfade
BASE_DIR = Path(__file__).resolve().parents[1]
PLOTS_DIR = BASE_DIR / "plots"
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# Logos
LOGO_MCI = BASE_DIR / "utils" / "MCI-positive-Web.png"
LOGO_GEOHUB = BASE_DIR / "utils" / "geohub-logo.png"
print("LOGO_MCI:", LOGO_MCI, "exists:", LOGO_MCI.exists())
print("LOGO_GEOHUB:", LOGO_GEOHUB, "exists:", LOGO_GEOHUB.exists())



def load_data():
    Session = create_db_session()
    with Session() as session:
        df = gpd.read_postgis(
            "SELECT * FROM landslides_view", session.bind, geom_col="geom"
        )
    # Datumsspalten vorbereiten
    df["event_date"] = pd.to_datetime(df["date"])
    df["event_year"] = df["event_date"].dt.year
    df["event_month"] = df["event_date"].dt.month
    return df


def compute_kpis(df: gpd.GeoDataFrame) -> dict:
    kpis = {}
    kpis["total_events"] = len(df)
    kpis["years_span"] = (int(df["event_year"].min()), int(df["event_year"].max()))

    class_counts = df["classification_name"].value_counts()
    kpis["classification_counts"] = class_counts

    year_counts = df["event_year"].value_counts().sort_index()
    kpis["year_counts"] = year_counts

    month_counts = df["event_month"].value_counts().sort_index()
    kpis["month_counts"] = month_counts

    return kpis


def add_title_page(pdf: PdfPages, kpis: dict,
                   logo_geohub: Path = None,
                   logo_mci: Path = None):

    fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4 Hochformat
    ax.axis("off")

    # -----------------------
    # Logos oben einfügen
    # -----------------------
    if logo_geohub is not None:
        print("Trying to load GeoHub logo from:", logo_geohub)
    if logo_mci is not None:
        print("Trying to load MCI logo from:", logo_mci)

    try:
        if logo_geohub is not None and logo_geohub.exists():
            img_geo = plt.imread(logo_geohub)
            # [x, y, w, h] in Figure-Koordinaten
            ax_geo = fig.add_axes([0.05, 0.87, 0.2, 0.1])
            ax_geo.imshow(img_geo)
            ax_geo.axis("off")
        else:
            print("GeoHub logo not found or path is None.")
    except Exception as e:
        print("Error loading GeoHub logo:", e)

    try:
        if logo_mci is not None and logo_mci.exists():
            img_mci = plt.imread(logo_mci)
            ax_mci = fig.add_axes([0.75, 0.87, 0.2, 0.1])
            ax_mci.imshow(img_mci)
            ax_mci.axis("off")
        else:
            print("MCI logo not found or path is None.")
    except Exception as e:
        print("Error loading MCI logo:", e)

    # -----------------------
    # Titel / Untertitel
    # -----------------------
    ax.text(0.5, 0.78, "Landslide Analysis Report – Austria",
            ha="center", va="center",
            fontsize=18, fontweight="bold")
    ax.text(0.5, 0.73,
            "Automatisch generierter Bericht (Database: landslides_view)",
            ha="center", va="center",
            fontsize=10)

    # -----------------------
    # KPIs
    # -----------------------
    y = 0.65
    ax.text(0.1, y, f"Total number of events: {kpis['total_events']}",
            fontsize=11)
    y -= 0.05
    year_min, year_max = kpis["years_span"]
    ax.text(0.1, y, f"Observation period: {year_min} – {year_max}",
            fontsize=11)

    y -= 0.08
    ax.text(0.1, y, "Top 5 classifications (by count):",
            fontsize=11, fontweight="bold")
    y -= 0.04
    for name, val in kpis["classification_counts"].head(5).items():
        ax.text(0.12, y, f"- {name}: {val} events", fontsize=10)
        y -= 0.03

    pdf.savefig(fig)
    plt.close(fig)




def add_image_page(pdf: PdfPages, image_path: Path, title: str):
    if not image_path.exists():
        return
    img = plt.imread(image_path)
    fig, ax = plt.subplots(figsize=(8.27, 11.69))
    ax.imshow(img)
    ax.axis("off")
    fig.suptitle(title, fontsize=12, fontweight="bold", y=0.97)
    pdf.savefig(fig)
    plt.close(fig)


def main():
    df = load_data()
    kpis = compute_kpis(df)

    report_path = REPORTS_DIR / "landslides_report.pdf"
    with PdfPages(report_path) as pdf:
        # Seite 1: Titel + Kennzahlen
        add_title_page(pdf, kpis, logo_geohub=LOGO_GEOHUB, logo_mci=LOGO_MCI)

        # Seite 2 ff.: Plots aus dem plots/-Ordner
        add_image_page(pdf, PLOTS_DIR / "classification_map.png",
                       "Landslide locations by classification")
        add_image_page(pdf, PLOTS_DIR / "classification_counts.png",
                       "Number of events by classification")
        add_image_page(pdf, PLOTS_DIR / "events_per_year.png",
                       "Number of events per year (>= 50)")
        add_image_page(pdf, PLOTS_DIR / "events_per_month.png",
                       "Number of events per month")
        add_image_page(pdf, PLOTS_DIR / "classification_piechart.png",
                       "Proportion of landslide classifications")
        add_image_page(pdf, PLOTS_DIR / "events_per_month_by_classification.png",
                       "Events per month by classification (stacked)")

    print(f"Report written to: {report_path}")


if __name__ == "__main__":
    main()
