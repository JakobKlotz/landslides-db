# About

Carinthia (Kärnten) provides mass-movement data in two formats: an 
INSPIRE-compliant distribution and a simplified distribution named
"Vereinfachte Umsetzung als Geopackage in der Projektion EPSG:31258".
Both are available [here](https://www.data.gv.at/datasets/70b85305-d3d1-487a-beff-75fa6d712c28?locale=de).

This project uses the simplified distribution because it omits 
several INSPIRE-specific attributes, i.e. `beginLifeSpanVersion`, 
`specificHazardType`, `quantitativeValue` and `qualitativeValue_`, 
which are always null in the INSPIRE data set. The simplified format is 
therefore cleaner and easier to process. Additionally, it comes with
`TypeOfHazard` for easier mass movement classification.

## Classification

This section details the harmonization steps needed for the mass movement 
classification.

The data set contains three basics hazard classifications (within 
`TypeOfHazard`) namely snowAvalanche, flood and landslide. Each of these
contain more fine grained types within the `QualitativeValue` column.

Each `TypeOfHazard` is processed differently before importing.

> [!NOTE]
> `TypeOfHazard` is used to filter the data and `QualitativeValue` for a 
> more fine-grained mapping of classifications.

### snowAvalanche

... all entries are dropped.

### flood

Contain multiple labels like "starker fluv. Feststofftransport" or
"Murgang, mehrmals beob. (30 - 100 Jahre)". Only "Murgang" are kept and 
classified as "gravity slide or flow".

### landslide

All landslide entries are imported. Since these contain various different
labels a mapping was defined -> see `landslide-mapping.json`.
