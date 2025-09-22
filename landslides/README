# Landslide DB Setup

## Docker

### 1️⃣ Env variables

First add an `.env` file at the root of the project with following content:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=mysecretpassword  # TODO choose a new password
POSTGRES_HOST=postgis  # PostGIS service in docker compose
POSTGRES_PORT=5432
POSTGRES_DB=landslides
```

Change the `POSTGRES_PASSWORD`!

### 2️⃣ Build the images

```bash
docker compose build
docker compose up -d postgis  # wait until the db accepts connections
docker compose up import  # to import the data, after the import step, the
# container is shut down
```

## Initial Development Setup

Following steps are needed for initial development and database setup.

## `alembic` setup

Init the folder structure:

```bash
alembic init landslides
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

Enter the container within `psql`:

```bash
docker exec -it landslides-db psql -U postgres -d landslides
```

Show tables, get first 10 rows and exit:

```bash
\dt
SELECT * FROM landslides LIMIT 10;
\q
```
