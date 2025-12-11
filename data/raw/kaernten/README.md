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

