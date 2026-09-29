# Deployment notes

## Local prototype
The repository runs immediately with SQLite for the synthetic demo. This makes the hackathon prototype deterministic and easy to review.

## PostgreSQL + Apache AGE
For the production architecture, migrate the relational store to PostgreSQL and apply `age_schema.sql`. The API's graph contract remains `/api/graph`, so the React/D3 layer does not need to change.

## OpenSearch
Index evidence documents using `opensearch_mapping.json`. The UI can continue to call the FastAPI search endpoint while OpenSearch handles full-text/indicator retrieval behind it.

## Collection boundary
Do not point the demo at real onion services or unauthorized targets. Add only authorized/lawfully accessible source adapters, respect applicable policies, and keep an audit trail.
