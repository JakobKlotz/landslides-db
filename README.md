# Landslides DB

Austrian landslide inventory.
... an attempt to build the most comprehensive landslide database.

## Project installation

### 1️⃣ Python packages 

The project is setup with `uv`. Simply follow their installation instructions
[here](https://docs.astral.sh/uv/#installation).

Next, install the project with:

```bash
uv sync
```

That's it! 🚀

### 2️⃣ Code formatting & linting

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

### 3️⃣ `git lfs`

To manage raw data (i.e., simply large files that we've downloaded)
from different sources, git large file storage (lfs) is used. Install it if you
haven't already - [link](https://git-lfs.com/).

Put files within `data/raw/`. By default, `.gpkg` files are being tracked by
`git lfs` (see `.gitattributes`). If you want to track a specific file or 
another file extension expand `.gitattributes`.
