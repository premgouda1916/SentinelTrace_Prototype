# SentinelTrace — SIH26151 Working Prototype

A defensive, analyst-in-the-loop prototype for **SIH26151 — Dark Web Threat Actor De-anonymization**.

> **Important:** The bundled dataset is synthetic/demo data. The prototype does not access real dark-web services, perform exploitation, bypass access controls, or claim automatic real-world identity attribution. It demonstrates the requested workflow using authorized/lawfully accessible inputs.

## What is implemented

- FastAPI backend
- React + D3.js analyst dashboard
- Evidence-backed actor profiles
- Relationship graph for handles, PGP identifiers, wallets, infrastructure and sources
- Confidence + provenance records
- Timeline filtering
- CSV and JSON export
- MISP/OpenCTI-style CTI export payloads
- Synthetic demo dataset
- PostgreSQL/OpenSearch integration hooks via environment variables
- Apache AGE schema/migration example in `docs/age_schema.sql`

## Quick start — backend demo

```bash
cd backend
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# Linux/macOS:
# source .venv/bin/activate
pip install -r requirements.txt
python seed_demo.py
uvicorn app:app --reload --port 8000
```

Open http://127.0.0.1:8000/docs for the API or http://127.0.0.1:8000 for the demo UI if the React build has been copied into `backend/static`.

## React dashboard

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server normally runs on http://127.0.0.1:5173 and calls the FastAPI API on port 8000.

## Production/deployment profile

The prototype is designed to move from SQLite demo mode to PostgreSQL and OpenSearch by setting:

- `DATABASE_URL=postgresql+psycopg://...`
- `OPENSEARCH_URL=http://...`

The source contains the adapter boundary; hosted blockchain explorer services are optional and are not required for the demo.

## Live demo / QR code

A QR code should only point to a **real public HTTPS deployment**. Do not put `localhost` in the final SIH PPT. After deployment, run:

```bash
python scripts/generate_qr.py https://YOUR-PUBLIC-DEMO-URL
```

This creates `qr_code.png` and prints the URL to use in the PPT.
