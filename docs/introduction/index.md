---
outline: deep
---

# About

This project builds a reproducible, harmonized inventory for mass movement data
in Austria. By curating multiple open data sets, a single PostGIS data base 
is provided.

::: warning

This project is under active development. The data base schema and its records
are subject to change.

:::

## Why?

Several institutes, regional authorities and researchers maintain data 
collections, but they live in different silos and formats. This project aims 
to collect these sources, harmonize it and publish the data for the research 
community to use.

By providing a single, reproducible database, we enable:

- Easy access to comprehensive mass movement data
- Standardized data formats and classifications
- Clear data provenance and attribution
- A foundation for research and analysis

## Data Coverage

The database encompasses different mass movement phenomena, including:

- Gravity slide or flow
- Rockfall
- Mass movement (undefined)
- Deep‑seated rock slope deformation
- Collapse / sinkhole

## Getting Started

### Quick Access (GeoPackage)

For users who want to quickly explore the data without setting up a database, 
we provide a ready-to-use GeoPackage file. This is ideal for:

- Quick data exploration and visualization
- One-time analyses or prototyping
- Users without data base management experience

::: tip

The GeoPackage dump contains a single table with all events and is located 
in the repository's [`db-dump/`](https://github.com/JakobKlotz/landslides-db/tree/main/db-dump) 
directory. Simply download and open it in your favorite GIS application.

:::

### PostGIS Database Setup

For a proper workflow with reproducible data pipelines, advanced querying and 
integration into existing infrastructure, we recommend deploying the full 
PostGIS database using Docker.

To set up the database, please refer to the 
[Quick Start Guide](../quick-start.md).

## Data Sources

The inventory incorporates data from the following sources:

| Source Name                                                                                                                             |         License         |
|-----------------------------------------------------------------------------------------------------------------------------------------|:-----------------------:|
| [GeoSphere](https://data.inspire.gv.at/d69f276f-24b4-4c16-aed7-349135921fa1)                                                            |        [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)       |
| [Global Fatal Landslides](https://www.arcgis.com/home/item.html?id=7c9397b261aa436ebfbc41396bd96d06)                                    | [Open Government License](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/) |
| [NASA COOLR](https://maps.nccs.nasa.gov/arcgis/apps/MapAndAppGallery/index.html?appid=574f26408683485799d02e857e5d9521)                 |     Custom License (provided in the repo)     |
| [WLV](https://geometadatensuche.inspire.gv.at/metadatensuche/inspire/ger/catalog.search#/metadata/ccca05aa-728d-4218-9f4c-81286c537527) |     [No Limitations](https://geometadatensuche.inspire.gv.at/metadatensuche/inspire/ger/catalog.search#/metadata/ccca05aa-728d-4218-9f4c-81286c537527)      |

Each record in the database is linked to its original source to ensure clear
data provenance and proper attribution.

We are continuously working on adding more data sources to enhance the 
comprehensiveness of the inventory.

## Attributions

Website icon by <a target="_blank" href="https://icons8.com">Icons8</a>

This project is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).