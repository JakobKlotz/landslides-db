## Version: `0.1.1`

### 🌟 Features

- For quick access without setting up the data base, a GeoPackage dump is 
available in [`db-dump/`](./db-dump)
- Individual processed source files are now stored in a new 
`data/processed-layers` directory to avoid confusion with the main dump.
- Added a documentation site with:
    - About: project overview and goals
    - Quick Start: step-by-step usage guide
    - Configuration: options and examples (coming soon)

Provides a single, user-friendly reference to replace the README files.

### 🛠 Dev changes

- Refactored the project into an installable Python package. This allows for 
consistent and simplified module imports for the data import logic across the 
project.
- Incorporated the `TARGET_CRS` re-projection in the `BaseProcessor` class 
for a unified approach.
- `typer` was added as dependency to convert `scripts/import.py` to a simple
CLI
    - A `--dump-layers` flag has been added to the import CLI. This flag must
    now be used to explicitly generate the individual processed files.

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
