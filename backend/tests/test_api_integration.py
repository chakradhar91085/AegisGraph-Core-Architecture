import unittest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app

class TestAPIIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("app.api.chat.graph_rag_service.generate_answer")
    def test_new_session_generation(self, mock_generate_answer):
        # Mock the service response
        mock_generate_answer.return_value = {
            "answer": "Mock Answer",
            "intent": "employee_lookup",
            "retrieval": {"result_count": 1},
            "telemetry": {"smoothed_risk": 0.05}
        }
        
        # Request without session_id
        response = self.client.post("/api/v1/chat", json={"query": "Who is Alice?"})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("session_id", data)
        self.assertTrue(len(data["session_id"]) > 0)
        self.assertEqual(data["answer"], "Mock Answer")
        
        # Verify the generated session_id was passed to GraphRAGService
        passed_session_id = mock_generate_answer.call_args[1].get("session_id")
        self.assertEqual(passed_session_id, data["session_id"])

    @patch("app.api.chat.graph_rag_service.generate_answer")
    def test_session_continuity(self, mock_generate_answer):
        # Mock the service response
        mock_generate_answer.return_value = {
            "answer": "Mock Answer",
            "intent": "sent_emails",
            "retrieval": {"result_count": 5},
            "telemetry": {"smoothed_risk": 0.25}
        }
        
        custom_session = "frontend-persistent-session-123"
        
        # Request WITH session_id
        response = self.client.post("/api/v1/chat", json={
            "query": "What emails did she send?",
            "session_id": custom_session
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Assert the same session ID was returned and passed along
        self.assertEqual(data["session_id"], custom_session)
        passed_session_id = mock_generate_answer.call_args[1].get("session_id")
        self.assertEqual(passed_session_id, custom_session)

    def test_retrieval_bypass_removed(self):
        # Ensure the direct retrieval route returns 404 (Not Found)
        response = self.client.post("/api/v1/retrieval/query", json={
            "query": "Bypass query",
            "limit": 100,
            "max_depth": 5
        })
        
        self.assertEqual(response.status_code, 404)

    @patch("app.rag.service.ollama_client.generate")
    def test_end_to_end_telemetry_fields(self, mock_llm_generate):
        # Mock the LLM to return a fast answer, let everything else run normally
        mock_llm_generate.return_value = "Mocked LLM Answer"
        
        response = self.client.post("/api/v1/chat", json={
            "query": "Who is Christopher Calger?"
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify telemetry exists
        self.assertIn("telemetry", data)
        telemetry = data["telemetry"]
        
        # Verify policy fields are present
        self.assertIn("policy", telemetry)
        policy = telemetry["policy"]
        self.assertIn("risk_level", policy)
        self.assertIn("attenuation_factor", policy)
        self.assertIn("effective_context_limit", policy)
        self.assertIn("effective_graph_depth", policy)
        
        # Verify blocked_by_policy is present
        self.assertIn("blocked_by_policy", telemetry)
        self.assertFalse(telemetry["blocked_by_policy"]) # Should not be blocked for this simple query

class TestSuite:
    @staticmethod
    def test_all():
        unittest.main(module=__name__, exit=False)

if __name__ == "__main__":
    unittest.main()
