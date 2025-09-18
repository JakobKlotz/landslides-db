# Landslides DB

Austrian landslide inventory.
... an attempt to build the most comprehensive landslide database.

## Project installation

The project is setup with `uv`. Simply follow their installation instructions
[here](https://docs.astral.sh/uv/#installation).

Next, install the project with:

```bash
uv sync
```

That's it! 🚀

## Code formatting & linting

For a consistent codebase, we use `pre-commit` to format and lint all
Python scripts. Upon initial setup install `pre-commit` with:

```bash
uv tool install pre-commit
```

To automatically format and lint the code we make use of so called hooks, 
install them with:

```bash
pre-commit install --install-hooks
```

That's it. Now every time you make a commit, all your code is automatically
processed to ensure that we end up with a consistently styled code base.
