import sys
import os

# Ensure backend is importable
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.security.policy import policy_engine
from app.security.models import RiskLevel
from app.core.config import settings

PASS = 0
FAIL = 0

def report(name: str, passed: bool, detail: str = ""):
    global PASS, FAIL
    status = "PASS" if passed else "FAIL"
    if passed:
        PASS += 1
    else:
        FAIL += 1
    detail_str = f" -- {detail}" if detail else ""
    print(f"  [{status}] {name}{detail_str}")

def _test_policy_levels():
    print("\n--- Test: Policy Risk Levels ---")
    
    # 1. Very low risk → LOW
    pol_low = policy_engine.calculate_policy(0.1)
    report("Very low risk -> LOW", pol_low.risk_level == RiskLevel.LOW, f"Got: {pol_low.risk_level.value}")
    
    # 2. Risk around/below threshold → MEDIUM
    pol_med = policy_engine.calculate_policy(0.5)
    report("Risk 0.5 -> MEDIUM", pol_med.risk_level == RiskLevel.MEDIUM, f"Got: {pol_med.risk_level.value}")
    
    # 3. High risk → HIGH
    pol_high = policy_engine.calculate_policy(0.9)
    report("High risk -> HIGH", pol_high.risk_level == RiskLevel.HIGH, f"Got: {pol_high.risk_level.value}")

def _test_policy_constraints():
    print("\n--- Test: Policy Formula Constraints ---")
    
    pol_0 = policy_engine.calculate_policy(0.0)
    pol_1 = policy_engine.calculate_policy(1.0)
    
    # 4. Attenuation factor remains in [0,1]
    report("Risk 0.0 Attenuation factor in [0,1]", 0.0 <= pol_0.attenuation_factor <= 1.0)
    report("Risk 1.0 Attenuation factor in [0,1]", 0.0 <= pol_1.attenuation_factor <= 1.0)
    
    # 5. Effective context limit never falls below 1
    # Check bounds across 0 to 1
    min_context = min(policy_engine.calculate_policy(r/100.0).effective_context_limit for r in range(101))
    report("Effective context limit >= 1", min_context >= 1)
    
    # 6. Effective graph depth never becomes negative
    min_depth = min(policy_engine.calculate_policy(r/100.0).effective_graph_depth for r in range(101))
    report("Effective graph depth >= 0", min_depth >= 0)
    
    # 7. Risk = 0
    report("Risk 0.0 attenuation factor near 1.0", pol_0.attenuation_factor > 0.95, f"Got: {pol_0.attenuation_factor:.3f}")
    
    # 8. Risk = 1
    report("Risk 1.0 attenuation factor near 0.0", pol_1.attenuation_factor < 0.05, f"Got: {pol_1.attenuation_factor:.3f}")

def _test_policy_monotonicity():
    print("\n--- Test: Monotonicity ---")
    
    prev_attenuation = 2.0
    is_monotonic = True
    
    for i in range(101):
        risk = i / 100.0
        pol = policy_engine.calculate_policy(risk)
        
        # Attenuation should decrease or stay same as risk increases
        if pol.attenuation_factor > prev_attenuation:
            is_monotonic = False
            print(f"Monotonicity failed at risk {risk}: {pol.attenuation_factor} > {prev_attenuation}")
            break
            
        prev_attenuation = pol.attenuation_factor
        
    report("Attenuation factor monotonically decreases", is_monotonic)

def sample_policies():
    print("\n--- Sample Policies ---")
    risks = [0.0, 0.3, 0.55, 0.8, 1.0]
    
    print(f"{'Risk':<5} | {'Level':<6} | {'Atten (kappa)':<13} | {'Context Limit':<13} | {'Graph Depth':<11}")
    print("-" * 60)
    
    for r in risks:
        pol = policy_engine.calculate_policy(r)
        print(f"{pol.risk_score:<5.2f} | {pol.risk_level.value:<6} | {pol.attenuation_factor:<9.4f} | {pol.effective_context_limit:<13} | {pol.effective_graph_depth:<11}")

def main():
    print("=" * 60)
    print("  AEGISGRAPH PHASE 4C.1 — ADAPTIVE POLICY TESTS")
    print("=" * 60)
    
    _test_policy_levels()
    _test_policy_constraints()
    _test_policy_monotonicity()
    sample_policies()
    
    total = PASS + FAIL
    print(f"\n{'=' * 60}")
    print(f"  RESULTS: {PASS}/{total} passed, {FAIL} failed")
    print(f"{'=' * 60}")
    
    if FAIL > 0:
        sys.exit(1)


import unittest
class TestSuite(unittest.TestCase):
    def test_all(self):
        try:
            main()
        except SystemExit as e:
            self.assertEqual(e.code, 0)

if __name__ == "__main__":
    main()
