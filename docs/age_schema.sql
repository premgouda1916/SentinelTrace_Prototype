-- Optional Apache AGE migration for the production graph layer.
-- The demo itself keeps a relational fallback so it runs without AGE.
CREATE EXTENSION IF NOT EXISTS age;
LOAD 'age';
SET search_path = ag_catalog, "$user", public;
SELECT create_graph('sentineltrace');

-- Example graph model:
-- (Actor)-[:USES_HANDLE]->(Handle)
-- (Actor)-[:USES_PGP]->(PGP)
-- (Actor)-[:ASSOCIATED_WITH]->(Wallet)
-- (Actor)-[:HAS_INFRA_SIGNAL]->(Infrastructure)
-- (Entity)-[:SUPPORTED_BY]->(Evidence)
