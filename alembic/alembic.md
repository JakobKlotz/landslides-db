# For Developers

Following steps are needed for initial development and database setup with 
`alembic`.

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
