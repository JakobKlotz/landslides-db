## Version: `0.1.1`

### 🛠 Dev changes

- Refactored the project into an installable Python package. This allows for 
consistent and simplified module imports for the data import logic across the 
project.
- Incorporated the `TARGET_CRS` re-projection in the `BaseProcessor` class 
for a unified approach.

## Version: `0.1.0`

First instance of the data base with records from four different sources.

### 🌟 Features

- Unified records of landslides and other mass movements in Austria
- Docker services to setup the data base and a dedicated API 
(which is optional) but can serve as an entrypoint for further applications
- Automatic duplicate check during import, based on event dates and a 500-meter
radius
- Each record is linked to its original source for data provenance
- Unified event classifications such as gravity slides or rockfalls
