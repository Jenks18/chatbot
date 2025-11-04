Dev run instructions (SQLite fallback)

This file documents how to run the backend locally for development without installing Postgres system libs.

1) Activate your virtualenv (assumes `venv` exists):

```bash
cd /Users/iannjenga/Desktop/chatbot/backend
source venv/bin/activate
```

2) Install dev-only Python requirements (does NOT include `psycopg2-binary`):

```bash
pip install -r requirements-dev.txt
```

3) Enable the SQLite dev fallback (either set DEV_SQLITE=1 or set DATABASE_URL to a sqlite URI).

You can set it in your shell for the run:

```bash
export DEV_SQLITE=1
# or create a .env file in backend/ with DEV_SQLITE=1
```

4) Start the backend (from `backend/`):

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

5) Verify health endpoint:

```bash
curl http://localhost:8000/health
```

Notes:
- This change is strictly for local development. Production deployments should continue to set `DATABASE_URL` to the Postgres instance and install `psycopg2-binary` (or use the system package). Do not change production environment variables on a live deployment.
- If you later need to run the reference-fetch pipeline (admin endpoint), install `httpx` and `beautifulsoup4` (already in requirements-dev), but if you install `psycopg2-binary` you'll need system libs (libpq/OpenSSL) on macOS via Homebrew.
