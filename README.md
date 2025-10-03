![PostGIS](https://img.shields.io/badge/PostGIS-3840A0?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=white)
![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg?style=for-the-badge)

<div align="center">
  <img src="./assets/header.png" alt="Header" width="450"/>
</div>

# Austrian Landslide Inventory

This project aims to build the most comprehensive, open-source landslide 
data base for Austria. By consolidating data from various national and 
international sources, we provide a PostGIS database that can be easily setup 
using Docker.

> [!WARNING]
> This project is under active development. The database schema and its records
> are subject to change.

## Getting Started

To get your own instance of the database up and running, please follow the 
setup instructions which use Docker for easy deployment.

Please refer to the [**Database Setup Guide**](./alembic/README.md).

## Data Sources

The inventory is built by incorporating data from the following sources:

- [GeoSphere](https://data.inspire.gv.at/d69f276f-24b4-4c16-aed7-349135921fa1):
    CC BY 4.0 ([link](https://creativecommons.org/licenses/by/4.0/))
- [Global Fatal Landslides](https://www.arcgis.com/home/item.html?id=7c9397b261aa436ebfbc41396bd96d06):
    Open Government License ([link](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/))
- [NASA COOLR](https://maps.nccs.nasa.gov/arcgis/apps/MapAndAppGallery/index.html?appid=574f26408683485799d02e857e5d9521): 
    Custom License ([link](./data/raw/nasa-coolr/LICENSE))
- [WLV](https://geometadatensuche.inspire.gv.at/metadatensuche/inspire/ger/catalog.search#/metadata/ccca05aa-728d-4218-9f4c-81286c537527)
    No Limitations ([link](https://geometadatensuche.inspire.gv.at/metadatensuche/inspire/ger/catalog.search#/metadata/ccca05aa-728d-4218-9f4c-81286c537527))

> [!NOTE]
> Each record in the database is linked to its original source to ensure clear
> data provenance and proper attribution.

We are continuously working on adding more data sources to enhance the
comprehensiveness of the inventory.

---

## Development setup

If you want to contribute to the project, follow these steps to set up your 
development environment.

### 1️⃣ Python packages 

The project is setup with `uv`. Simply follow their installation instructions
[here](https://docs.astral.sh/uv/#installation).

Next, install the project with:

```bash
uv sync
```

That's it! 🚀

### 2️⃣ Code formatting & linting

For a consistent codebase, we use `pre-commit` to format and lint all
Python scripts. Upon initial setup install `pre-commit` with:

```bash
uv tool install pre-commit
```

To automatically format and lint the code we make use of so called hooks, 
install them with:

```bash
pre-commit install --install-hooks
```

That's it. Now every time you make a commit, all your code is automatically
processed to ensure that we end up with a consistently styled code base.

### 3️⃣ `git lfs`

To manage raw data (i.e., simply large files that we've downloaded)
from different sources, git large file storage (lfs) is used. Install it if you
haven't already - [link](https://git-lfs.com/).

Put files within `data/raw/`. By default, `.gpkg` files are being tracked by
`git lfs` (see `.gitattributes`). If you want to track a specific file or 
another file extension expand `.gitattributes`.
