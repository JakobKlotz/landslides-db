# Contributions

I'm really glad, you found your way here. 👋🏽 Contributions are welcomed, 
thank you in advance for improving the project! Credit will always be given!

## How to contribute

1. **Report Issues**: If you find a bug or have a feature request, please open 
an issue.
2. **Submit Pull Requests**: Eager to submit code changes? Fork the repository,
create a branch, make your changes, and submit a pull request. Please refer to
the instructions below on how to setup your development environment.

> [!NOTE]
> If you're addressing an open issue, consider commenting on the issue to let
> others know you're working on it.

---

## Development setup

Follow these steps to set up your development environment.

### 1️⃣ Python packages 

The project is setup with `uv`. Simply follow their installation instructions
[here](https://docs.astral.sh/uv/#installation).

Next, install the project with:

```bash
uv sync
```

### 2️⃣ Code formatting & linting

For a consistent codebase, we use `pre-commit` to format and lint all
Python scripts. Upon initial setup install `pre-commit` with:

```bash
uv tool install pre-commit
```

To automatically format and lint the code we make use of hooks, install them
with:

```bash
pre-commit install --install-hooks
```

Now every time you make a commit, all your code is automatically processed to 
ensure that the code is consistently styled.

### 3️⃣ `git lfs`

To manage raw data (i.e., simply large files that we've downloaded)
from different sources, git large file storage (lfs) is used. Install it if you
haven't already - [link](https://git-lfs.com/).

Put files within `data/raw/`. By default, `.gpkg` files are being tracked by
`git lfs` (see `.gitattributes`). If you want to track a specific file or 
another file extension expand `.gitattributes`.

---

Thank you for improving this project! 😊

Jakob
