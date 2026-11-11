# readability-wrapper

A front-end for [Mercury Web Parser](https://mercury.postlight.com/web-parser/) that allows you to read the main content on pages without all the unnecessary cruft

** Note ** The hosted Mercury Web Parser API will shut down on April 15, 2019. You will need to self-host [Mercury Parser API](https://github.com/postlight/mercury-parser-api) on AWS.

## Development

This project uses [uv](https://docs.astral.sh/uv/) to manage the Python interpreter
and dependencies. The Python version is pinned in `.python-version`, dependencies are
declared in `pyproject.toml`, and the exact resolved versions are locked in `uv.lock`.

### Prerequisites

- [uv](https://docs.astral.sh/uv/) — installs and manages both Python and packages.
- A self-hosted [Mercury Parser API](https://github.com/postlight/mercury-parser-api) instance (see note above).

### Setup

```sh
uv sync
```

This creates a virtualenv in `.venv` (using the Python version from `.python-version`)
and installs the runtime and development dependencies from `pyproject.toml`.

### Configuration

Copy `.env.example` to `.env` and fill in the values:

- `MERCURY_API_URL` — URL of your self-hosted Mercury Parser API.
- `MERCURY_API_KEY` — API key for the above.

### Running

```sh
uv run app.py
```

Serves the app at <http://127.0.0.1:5000>.

### Testing

```sh
uv run pytest     # run the test suite
uv run flake8     # lint the code
```

### Managing dependencies

```sh
uv add <package>       # add a runtime dependency
uv add --dev <package> # add a development dependency
uv lock --upgrade      # update all dependencies to their latest versions
```
