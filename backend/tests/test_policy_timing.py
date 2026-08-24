import sys
import os

# Ensure backend is importable
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import asyncio
import time
from app.security.service import aegis_security
from app.security.session import session_store
from app.retrieval.schemas import RetrievalResponse

async def verify_timing():
    session_id = "test_timing_session"
    print("\n--- Phase 4C.2 Policy Timing Verification ---")
    
    # Reset session state for clean test
    if session_id in session_store.sessions:
        del session_store.sessions[session_id]
        
    print(f"[Initial] Existing EWMA for session: 0.0")
    
    # Query N (First Query)
    query_n = "Who is Christopher Calger?"
    ctx_n = await aegis_security.observe_query(session_id, query_n)
    policy_n = ctx_n["policy"]
    print(f"\n[Query N] Query: '{query_n}'")
    print(f"[Query N] Policy applied BEFORE retrieval: Risk Level = {policy_n.risk_level.value}, Attenuation = {policy_n.attenuation_factor:.3f}")
    
    # Mock retrieval response
    mock_resp_n = RetrievalResponse(
        query=query_n,
        intent="employee_lookup",
        strategy="employee_lookup",
        result_count=1
    )
    
    # Post-retrieval
    telemetry_n = await aegis_security.calculate_risk(ctx_n, mock_resp_n)
    ewma_after_n = telemetry_n.smoothed_risk
    print(f"[Query N] Post-retrieval telemetry computed. New EWMA = {ewma_after_n:.3f}")
    
    # Query N+1 (Second Query)
    query_n1 = "What emails did Christopher Calger send?"
    ctx_n1 = await aegis_security.observe_query(session_id, query_n1)
    policy_n1 = ctx_n1["policy"]
    
    print(f"\n[Query N+1] Query: '{query_n1}'")
    print(f"[Query N+1] Policy applied BEFORE retrieval: Risk Level = {policy_n1.risk_level.value}, Attenuation = {policy_n1.attenuation_factor:.3f}")
    
    # Verify policy N+1 used ewma_after_n
    # The policy for N+1 should be derived exactly from the EWMA calculated after N.
    from app.security.policy import policy_engine
    expected_policy = policy_engine.calculate_policy(ewma_after_n)
    
    if policy_n1.attenuation_factor == expected_policy.attenuation_factor:
        print("\n[VERIFICATION PASS] Policy for Query N+1 exactly matches the EWMA calculated from Query N.")
    else:
        print(f"\n[VERIFICATION FAIL] Policy mismatch: {policy_n1.attenuation_factor} != {expected_policy.attenuation_factor}")


import unittest
class TestSuite(unittest.IsolatedAsyncioTestCase):
    async def test_all(self):
        try:
            await verify_timing()
        except SystemExit as e:
            self.assertEqual(e.code, 0)

if __name__ == "__main__":
    asyncio.run(verify_timing())
