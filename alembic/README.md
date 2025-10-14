# Landslide DB Setup

Instructions to set up the PostGIS data base with Docker.

## Docker

### 1️⃣ Env variables

First add an `.env` file at the root of the project with following content:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=mysecretpassword  # TODO set a secure password!
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=landslides
```

> [!IMPORTANT]
> Be sure to change the `POSTGRES_PASSWORD` to a password of your choice!

The data base will be created with the details provided in the `.env` file.

### 2️⃣ Build the images

With Docker installed, we have to build the containers first:

```bash
docker compose build
```

### 3️⃣ Initialize the database & Import data

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

### 4️⃣ [Optional] API

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
