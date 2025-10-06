# Landslide DB Setup

## Docker

### 1️⃣ Env variables

First add an `.env` file at the root of the project with following content:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=mysecretpassword  # TODO choose a new password
POSTGRES_HOST=db  # PostGIS service in docker compose
POSTGRES_PORT=5432
POSTGRES_DB=landslides
```

Change the `POSTGRES_PASSWORD`!

### 2️⃣ Build the images

With Docker installed, build and start the containers with:

```bash
docker compose build
docker compose up -d db  # wait until the db accepts connections
docker compose up importer  # to import the data, after the import step, the
# container is shut down
```

Access the database at `localhost:5432` with a PostGIS enabled client
(e.g. [`pgAdmin`](https://www.pgadmin.org/)).

### 3️⃣ [Optional] API

Using [`pg_tileserv`](https://github.com/CrunchyData/pg_tileserv), an API
is provided to access the data. This service is optional, but could provide
an entrypoint for further applications.
To start the service, run:

```bash
docker compose up -d api
```

Navigate to [http://localhost:7800](http://localhost:7800) to preview
the endpoints. `public.landslides_view` provides a comprehensive view of the
landslide data.

---

## For developers

Following steps are needed for initial development and database setup.

## `alembic` setup

Init the folder structure:

```bash
alembic init alembic
```

### Customize files

Create a dedicated `.env` for the database secrets and switch to `env.py`, 
add lines to load the variables. 

### Autogenerate revision

With `alembic` autogenerate the first revision from the `sqlalchemy` models:

```bash
alembic revision --autogenerate -m "db table structure"
```

Navigate to the first revision and ensure that the `postgis` extension is
enabled. Add following at the beginning of `upgrade()`:

```python
op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
```

... and at the end to `downgrade()`:

```python
op.execute("DROP EXTENSION postgis")
```

### Apply revision

```bash
alembic upgrade head
```

### Helpers

Couple of commands that are often necessary:

Reset to base, with:

```bash
alembic downgrade base
```
