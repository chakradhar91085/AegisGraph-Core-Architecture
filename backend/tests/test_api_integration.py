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

        # Request without a session_token -> a fresh, server-generated session
        response = self.client.post("/api/v1/chat", json={"query": "Who is Alice?"})

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("session_id", data)
        self.assertTrue(len(data["session_id"]) > 0)
        self.assertIn("session_token", data)
        self.assertTrue(len(data["session_token"]) > 0)
        self.assertEqual(data["answer"], "Mock Answer")

        # Verify the generated session_id was passed to GraphRAGService
        passed_session_id = mock_generate_answer.call_args[1].get("session_id")
        self.assertEqual(passed_session_id, data["session_id"])

    @patch("app.api.chat.graph_rag_service.generate_answer")
    def test_forged_session_token_is_not_trusted(self, mock_generate_answer):
        # This is the vulnerability this endpoint used to have: a client
        # could pick any string as its "session id" and the server would
        # treat it as an existing, continuing session -- silently resetting
        # or hijacking accumulated risk state. A client-chosen string that
        # isn't a real signed ticket must now be treated as brand new.
        mock_generate_answer.return_value = {
            "answer": "Mock Answer",
            "intent": "sent_emails",
            "retrieval": {"result_count": 5},
            "telemetry": {"smoothed_risk": 0.25}
        }

        forged_token = "attacker-chosen-session-id"
        response = self.client.post("/api/v1/chat", json={
            "query": "What emails did she send?",
            "session_token": forged_token
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertNotEqual(data["session_id"], forged_token)
        passed_session_id = mock_generate_answer.call_args[1].get("session_id")
        self.assertNotEqual(passed_session_id, forged_token)
        self.assertEqual(passed_session_id, data["session_id"])

    @patch("app.api.chat.graph_rag_service.generate_answer")
    def test_session_continuity_via_issued_token(self, mock_generate_answer):
        # Genuine continuity DOES still work -- but only through a token the
        # server itself issued, never through a client-chosen identifier.
        mock_generate_answer.return_value = {
            "answer": "Mock Answer",
            "intent": "sent_emails",
            "retrieval": {"result_count": 5},
            "telemetry": {"smoothed_risk": 0.25}
        }

        first = self.client.post("/api/v1/chat", json={"query": "Who is Alice?", "role": "Analyst"})
        first_data = first.json()
        token = first_data["session_token"]
        session_id = first_data["session_id"]

        second = self.client.post("/api/v1/chat", json={
            "query": "What emails did she send?",
            "session_token": token
        })
        second_data = second.json()

        self.assertEqual(second_data["session_id"], session_id)
        passed_session_id = mock_generate_answer.call_args[1].get("session_id")
        self.assertEqual(passed_session_id, session_id)

    @patch("app.api.chat.graph_rag_service.generate_answer")
    def test_role_cannot_be_changed_mid_session(self, mock_generate_answer):
        # The other half of the same vulnerability: a client could claim a
        # different (higher-privilege) role on a later message of the same
        # conversation. Role is now locked into the session token at
        # creation time and later claims are ignored.
        mock_generate_answer.return_value = {
            "answer": "Mock Answer",
            "intent": "employee_lookup",
            "retrieval": {"result_count": 1},
            "telemetry": {"smoothed_risk": 0.05}
        }

        first = self.client.post("/api/v1/chat", json={"query": "Who is Alice?", "role": "Auditor"})
        token = first.json()["session_token"]
        self.assertEqual(mock_generate_answer.call_args[1].get("role"), "Auditor")

        self.client.post("/api/v1/chat", json={
            "query": "What emails did she send?",
            "session_token": token,
            "role": "Standard"
        })
        self.assertEqual(mock_generate_answer.call_args[1].get("role"), "Auditor")

    def test_retrieval_bypass_removed(self):
        # Ensure the direct retrieval route returns 404 (Not Found)
        response = self.client.post("/api/v1/retrieval/query", json={
            "query": "Bypass query",
            "limit": 100,
            "max_depth": 5
        })
        
        self.assertEqual(response.status_code, 404)

    @patch("app.llm.ollama_provider.OllamaProvider.generate")
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
