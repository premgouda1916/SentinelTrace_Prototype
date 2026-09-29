import unittest
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

from fastapi.testclient import TestClient
from app import app, conn, seed_if_empty

class TestSentinelTraceAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        seed_if_empty()
        cls.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["mode"], "synthetic-demo")
        self.assertEqual(data["database"], "sqlite-demo")
        self.assertIn("timestamp", data)

    def test_actors_list(self):
        response = self.client.get("/api/actors")
        self.assertEqual(response.status_code, 200)
        actors = response.json()
        self.assertIsInstance(actors, list)
        self.assertGreaterEqual(len(actors), 3)
        actor_ids = [a["id"] for a in actors]
        self.assertIn("actor-001", actor_ids)
        self.assertIn("actor-002", actor_ids)
        self.assertIn("actor-003", actor_ids)

    def test_actors_search(self):
        response = self.client.get("/api/actors?q=Orion")
        self.assertEqual(response.status_code, 200)
        actors = response.json()
        self.assertTrue(any(a["id"] == "actor-001" for a in actors))

    def test_actor_detail_found(self):
        response = self.client.get("/api/actors/actor-001")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("actor", data)
        self.assertIn("entities", data)
        self.assertIn("evidence", data)
        self.assertEqual(data["actor"]["id"], "actor-001")
        self.assertGreater(len(data["entities"]), 0)
        self.assertGreater(len(data["evidence"]), 0)

    def test_actor_detail_not_found(self):
        response = self.client.get("/api/actors/nonexistent-actor")
        self.assertEqual(response.status_code, 404)

    def test_graph_endpoint(self):
        # All graph
        response = self.client.get("/api/graph")
        self.assertEqual(response.status_code, 200)
        graph = response.json()
        self.assertIn("nodes", graph)
        self.assertIn("links", graph)

        # Filtered graph
        response_actor = self.client.get("/api/graph?actor_id=actor-001")
        self.assertEqual(response_actor.status_code, 200)
        graph_actor = response_actor.json()
        self.assertTrue(any(n["id"] == "actor-001" for n in graph_actor["nodes"]))

    def test_export_json(self):
        response = self.client.get("/api/actors/actor-001/export.json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["actor"]["id"], "actor-001")

    def test_export_csv(self):
        response = self.client.get("/api/actors/actor-001/export.csv")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"].split(";")[0], "text/csv")
        csv_text = response.text
        self.assertIn("actor_id,actor,category", csv_text)
        self.assertIn("actor-001", csv_text)

    def test_export_cti(self):
        response = self.client.get("/api/actors/actor-001/cti.json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["schema"], "sentineltrace-cti-demo-v1")
        self.assertEqual(data["type"], "threat-intelligence-case")
        self.assertEqual(data["actor"]["id"], "actor-001")
        self.assertIn("observables", data)
        self.assertIn("evidence", data)

if __name__ == "__main__":
    unittest.main()
