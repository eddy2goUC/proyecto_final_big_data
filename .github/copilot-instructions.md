## Quick Context

This repository is a small Python project for a Big Data course. Primary code lives under `Helpers/` (utility modules). There is no single Flask entrypoint discovered; only dependencies are declared in `requirements.txt`.

## Big picture
- **Purpose:** Utility helpers for file ingestion (ZIP download/extract) and simple MongoDB user management.
- **Major components:**
  - `Helpers/funciones.py`: file operations (download, unzip, allowed extensions).
  - `Helpers/mongoDB.py`: a lightweight MongoDB wrapper (connect, CRUD for users, MD5 password hashing).
  - `requirements.txt`: external dependencies (Flask, pymongo, elasticsearch, etc.).

## Important patterns & conventions (do not change without approval)
- **Module style:** small classes with `@staticmethod` helpers (`Funciones`) and an OOP wrapper for DB (`MongoDB`).
- **Password hashing:** repository uses `hashlib.md5` in `Helpers/mongoDB.py` when creating/validating users. This is an observable pattern — do not silently replace it with a different scheme in PRs; instead add a migration plan if requested.
- **File filtering:** `Funciones.descomprimir_zip_local` filters extracted files to `['.txt', '.pdf']` and reports `carpeta`, `nombre`, `ruta`, `extension`.
- **Error handling:** helpers print exceptions and return safe defaults (e.g., `[]` or `False`). Follow existing style when adding new helpers.

## Developer workflows (what I could discover)
- Setup: create a Python venv and install dependencies:

```
python -m venv .venv
.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

- Secrets: there is an `.env` file in workspace root; assume DB URIs and credentials are loaded from environment. Never hardcode secrets in new code or in this instructions file.
- Running: no `app.py`/`wsgi.py` discovered. If adding runtime behaviour, prefer adding a clear entrypoint (e.g., `run.py`) and document it in `README.md`.

## Integration and external deps
- `requirements.txt` includes `Flask`, `pymongo`, `python-dotenv`, `elasticsearch==8.11.0`. Expect MongoDB and optionally Elasticsearch connections. When adding code that uses these services, mock external calls in unit tests.

## Examples (how to interact with existing helpers)
- Instantiate DB wrapper:

```
from Helpers.mongoDB import MongoDB
db = MongoDB(uri="mongodb://...", db_name="mydb")
db.test_connection()
```

- Use file helpers to download/unzip:

```
from Helpers.funciones import Funciones
archivos = Funciones.descargar_y_descomprimir_zip(url, carpeta_destino)
```

## PR guidance for AI agents
- Preserve existing public APIs in `Helpers/*` unless asked to refactor; prefer additive changes.
- When changing auth/storage schemes, include a migration plan and tests — don't silently swap hashing.
- Keep logging/exception style consistent (prints and safe returns) unless you refactor project-wide.

If anything here is unclear or you'd like me to include more examples (tests, CLI runs, or a recommended app entrypoint), tell me which area to expand.
