from __future__ import annotations

import csv
import io
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

BASE = Path(__file__).resolve().parent
DB = Path(os.getenv("DEMO_DB", BASE / "sentineltrace.db"))

app = FastAPI(title="SentinelTrace API", version="0.1.0", description="SIH26151 defensive attribution-support prototype")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS actors (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  confidence REAL NOT NULL,
  status TEXT NOT NULL,
  last_scan TEXT NOT NULL,
  summary TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS entities (
  id TEXT PRIMARY KEY,
  actor_id TEXT NOT NULL,
  type TEXT NOT NULL,
  value TEXT NOT NULL,
  label TEXT NOT NULL,
  FOREIGN KEY(actor_id) REFERENCES actors(id)
);
CREATE TABLE IF NOT EXISTS relationships (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,
  target TEXT NOT NULL,
  relation TEXT NOT NULL,
  confidence REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS evidence (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  actor_id TEXT NOT NULL,
  signal_type TEXT NOT NULL,
  description TEXT NOT NULL,
  source TEXT NOT NULL,
  observed_at TEXT NOT NULL,
  reliability REAL NOT NULL,
  confidence REAL NOT NULL,
  FOREIGN KEY(actor_id) REFERENCES actors(id)
);
"""


def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    return c


def seed_if_empty():
    c = conn()
    if c.execute("SELECT COUNT(*) FROM actors").fetchone()[0]:
        c.close(); return
    actors = [
        ("actor-001", "Orion-17", "marketplace", 0.86, "analyst-review", "2026-09-28", "Synthetic actor profile combining infrastructure, identifier and behavioural signals."),
        ("actor-002", "CinderFox", "forum", 0.71, "needs-review", "2026-09-27", "Synthetic cross-source persona cluster with mixed corroboration."),
        ("actor-003", "Northstar", "fraud", 0.64, "needs-review", "2026-09-26", "Synthetic profile showing conflicting evidence and a confidence downgrade."),
    ]
    c.executemany("INSERT INTO actors VALUES (?,?,?,?,?,?,?)", actors)
    entities = [
        ("handle-orion", "actor-001", "handle", "orion17", "Handle: orion17"),
        ("pgp-orion", "actor-001", "pgp", "PGP-DEMO-7A21", "PGP: PGP-DEMO-7A21"),
        ("wallet-orion", "actor-001", "wallet", "WALLET-DEMO-A1", "Wallet: WALLET-DEMO-A1"),
        ("infra-orion", "actor-001", "infrastructure", "INFRA-DEMO-03", "Infrastructure: INFRA-DEMO-03"),
        ("handle-cinder", "actor-002", "handle", "cinder_fox", "Handle: cinder_fox"),
        ("pgp-cinder", "actor-002", "pgp", "PGP-DEMO-CC14", "PGP: PGP-DEMO-CC14"),
        ("wallet-cinder", "actor-002", "wallet", "WALLET-DEMO-C2", "Wallet: WALLET-DEMO-C2"),
        ("handle-north", "actor-003", "handle", "northstar_x", "Handle: northstar_x"),
        ("wallet-north", "actor-003", "wallet", "WALLET-DEMO-N8", "Wallet: WALLET-DEMO-N8"),
    ]
    c.executemany("INSERT INTO entities VALUES (?,?,?,?,?)", entities)
    rels = [
        ("actor-001", "handle-orion", "uses-handle", .92), ("actor-001", "pgp-orion", "uses-pgp", .88),
        ("actor-001", "wallet-orion", "associated-wallet", .67), ("actor-001", "infra-orion", "infrastructure-signal", .81),
        ("actor-002", "handle-cinder", "uses-handle", .89), ("actor-002", "pgp-cinder", "uses-pgp", .77),
        ("actor-002", "wallet-cinder", "associated-wallet", .58), ("actor-003", "handle-north", "uses-handle", .84),
        ("actor-003", "wallet-north", "associated-wallet", .49),
        ("handle-orion", "handle-cinder", "stylometric-similarity", .62),
        ("wallet-orion", "wallet-cinder", "transaction-relationship-demo", .55),
    ]
    c.executemany("INSERT INTO relationships(source,target,relation,confidence) VALUES (?,?,?,?)", rels)
    evidence = [
        ("actor-001", "infrastructure", "Synthetic certificate fingerprint overlaps with a candidate clearnet infrastructure record.", "demo-certificate-feed", "2026-09-26T10:20:00Z", .92, .81),
        ("actor-001", "identifier", "Same synthetic PGP identifier appears across two source records.", "demo-marketplace-records", "2026-09-27T08:00:00Z", .96, .88),
        ("actor-001", "behavioural", "Stylometric feature profile is similar across synthetic samples.", "demo-forum-corpus", "2026-09-28T14:30:00Z", .73, .62),
        ("actor-002", "identifier", "Handle and PGP overlap across synthetic forum records.", "demo-forum-records", "2026-09-26T12:00:00Z", .87, .77),
        ("actor-002", "behavioural", "Behavioural continuity signal is moderate and requires analyst review.", "demo-forum-corpus", "2026-09-27T11:10:00Z", .71, .65),
        ("actor-003", "financial", "Synthetic wallet relationship is weak and does not independently establish identity.", "demo-blockchain-snapshot", "2026-09-25T09:00:00Z", .68, .49),
        ("actor-003", "conflict", "A synthetic source contains a conflicting handle-history signal; confidence reduced.", "demo-source-7", "2026-09-26T16:45:00Z", .81, .34),
    ]
    c.executemany("INSERT INTO evidence(actor_id,signal_type,description,source,observed_at,reliability,confidence) VALUES (?,?,?,?,?,?,?)", evidence)
    c.commit(); c.close()


seed_if_empty()

@app.get("/api/health")
def health():
    return {"status":"ok", "mode":"synthetic-demo", "database":"sqlite-demo", "timestamp":datetime.now(timezone.utc).isoformat()}

@app.get("/api/actors")
def actors(q: str | None = None):
    c = conn()
    if q:
        rows = c.execute("SELECT * FROM actors WHERE name LIKE ? OR category LIKE ? ORDER BY confidence DESC", (f"%{q}%", f"%{q}%")).fetchall()
    else:
        rows = c.execute("SELECT * FROM actors ORDER BY confidence DESC").fetchall()
    c.close()
    return [dict(r) for r in rows]

@app.get("/api/actors/{actor_id}")
def actor(actor_id: str):
    c = conn()
    a = c.execute("SELECT * FROM actors WHERE id=?", (actor_id,)).fetchone()
    if not a:
        c.close(); raise HTTPException(404, "Actor not found")
    entities = [dict(r) for r in c.execute("SELECT * FROM entities WHERE actor_id=?", (actor_id,)).fetchall()]
    evidence = [dict(r) for r in c.execute("SELECT * FROM evidence WHERE actor_id=? ORDER BY observed_at DESC", (actor_id,)).fetchall()]
    c.close()
    return {"actor":dict(a), "entities":entities, "evidence":evidence}

@app.get("/api/graph")
def graph(actor_id: str | None = None):
    c = conn()
    if actor_id:
        nodes = c.execute("SELECT id, name AS label, 'actor' AS type FROM actors WHERE id=? UNION ALL SELECT id, label, type FROM entities WHERE actor_id=?", (actor_id, actor_id)).fetchall()
        rels = c.execute("SELECT source,target,relation,confidence FROM relationships WHERE source=? OR target IN (SELECT id FROM entities WHERE actor_id=?)", (actor_id, actor_id)).fetchall()
    else:
        nodes = c.execute("SELECT id, name AS label, 'actor' AS type FROM actors UNION ALL SELECT id,label,type FROM entities").fetchall()
        rels = c.execute("SELECT source,target,relation,confidence FROM relationships").fetchall()
    c.close()
    return {"nodes":[dict(r) for r in nodes], "links":[dict(r) for r in rels]}

@app.get("/api/actors/{actor_id}/export.json")
def export_json(actor_id: str):
    return JSONResponse(content=actor(actor_id))

@app.get("/api/actors/{actor_id}/export.csv")
def export_csv(actor_id: str):
    data = actor(actor_id)
    out = io.StringIO(); w = csv.writer(out)
    w.writerow(["actor_id","actor","category","confidence","status","signal_type","description","source","observed_at","reliability"])
    for e in data["evidence"]:
        a=data["actor"]
        w.writerow([a["id"],a["name"],a["category"],a["confidence"],a["status"],e["signal_type"],e["description"],e["source"],e["observed_at"],e["reliability"]])
    return StreamingResponse(iter([out.getvalue()]), media_type="text/csv", headers={"Content-Disposition":f"attachment; filename={actor_id}.csv"})

@app.get("/api/actors/{actor_id}/cti.json")
def export_cti(actor_id: str):
    data = actor(actor_id)
    a=data["actor"]
    # MISP/OpenCTI-compatible export shape for demo interoperability; not a claim of native platform ingestion.
    return {
      "schema":"sentineltrace-cti-demo-v1",
      "type":"threat-intelligence-case",
      "actor":{"id":a["id"],"name":a["name"],"confidence":a["confidence"]},
      "observables":data["entities"],
      "evidence":data["evidence"],
      "analyst_review":a["status"]
    }

# Optional production static build.
STATIC = BASE / "static"
if STATIC.exists():
    app.mount("/", StaticFiles(directory=STATIC, html=True), name="static")
