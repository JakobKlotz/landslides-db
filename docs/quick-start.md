---
outline: deep
---

# Setup

Follow these couple of steps to spin up your own PostGIS instance of the 
landslides data base using Docker.

## Prerequisites

It is assumed that Git is installed on your system.
Two more tools are required to follow the steps below:

- [Docker](https://www.docker.com)
- [Git LFS](https://git-lfs.com/)

Install both to proceed.

> [!NOTE]
> Since this project is dependent on larger files to fill the data base, git 
> LFS is required to pull these files from the repository. After installation,
> be sure to run `git lfs install` once. A `git clone` of the repository will
> then pull the required files automatically.

## Setup Steps

### Environment

With the repository cloned, navigate to the project folder and set up the
environment variables. To do so, create an `.env` file at the root of the 
project with following content:

```dotenv {2}
POSTGRES_USER=postgres
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=landslides
```

> [!IMPORTANT]
> Be sure to change the `POSTGRES_PASSWORD` to a password of your choice!

The data base will be created with the details provided in your `.env` file.

### Build the images

With Docker installed, we have to build the containers first:

```bash
docker compose build
```

### Initialize the database & Import data

Next up, we can initialize the data base with:

```bash
docker compose up -d db
```

The initialization might take a couple of seconds, you can check the logs with

```bash
docker compose logs -f db
```

Wait until you see a line like:

```bash
2025-10-14 13:58:49.274 UTC [1] LOG:  database system is ready to accept connections
```

Once the database is ready, we can import the data with the `importer` service:

```bash
docker compose up importer
```

Upon completion, the `importer` service will exit automatically.
You can now access the database at `localhost:5432` with a PostGIS enabled 
client (e.g. [`pgAdmin`](https://www.pgadmin.org/)).

### [Optional] API

Using [`pg_tileserv`](https://github.com/CrunchyData/pg_tileserv), an API
is provided to access the data. This service is optional, but could provide
an entrypoint for further applications.
To start the service, run:

```bash
docker compose up -d api
```

Navigate to [http://localhost:7800](http://localhost:7800) to preview
the endpoints. `public.landslides_view` provides a comprehensive view of the
landslide data including sources and classifications.

<div style="text-align:center">
  <img
    src="./api-preview.png" alt="Landslides View in the API preview"
    loading="lazy" width="100%" style="border-radius: 10px;"
  >
  <figcaption>
    Preview of the data using the APIs interactive viewer
  </figcaption>
</div>