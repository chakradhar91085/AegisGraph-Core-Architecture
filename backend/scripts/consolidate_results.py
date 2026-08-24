import json
import csv
import os

def load_json(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r') as f:
        return json.load(f)

def load_csv(filepath):
    if not os.path.exists(filepath):
        return None
    data = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def main():
    print("Loading data...")
    p4_json = load_json("scripts/phase4d_evaluation.json")
    val_json = load_json("scripts/validation_results.json")
    p5c_json = load_json("scripts/phase5c_performance.json")
    p5_csv = load_csv("scripts/phase5_results_summary.csv")
    
    # We will build final_experimental_results.json
    final_results = {
        "metadata": {
            "title": "AegisGraph Final Experimental Results",
            "phase": "5D",
            "description": "Consolidated and validated metrics from all Phase 4 and Phase 5 evaluations."
        },
        "exposure_and_utility": {},
        "risk_progression": {},
        "policy_behavior": {},
        "performance_overhead": {}
    }
    
    # Cross validate CSV vs JSON
    # The CSV should match p4_json exactly
    aegis_data = p4_json.get("AEGISGRAPH", {})
    base_data = p4_json.get("BASELINE", {})
    
    for row in p5_csv:
        scenario = row["Scenario"]
        final_results["exposure_and_utility"][scenario] = {
            "baseline_exposure": int(row["Baseline Exposure"]),
            "aegisgraph_exposure": int(row["AegisGraph Exposure"]),
            "exposure_reduction_pct": float(row["Exposure Reduction %"]),
            "blocked_queries": int(row["Blocked Queries"]),
            "total_queries": int(row["Total Queries"])
        }
        
        final_results["risk_progression"][scenario] = {
            "max_ewma_risk": float(row["Max EWMA Risk"]),
            "final_ewma_risk": float(row["Final EWMA Risk"])
        }
        
        # Verify JSON
        queries = aegis_data.get(scenario, [])
        max_ewma = max(q["EWMA_risk"] for q in queries) if queries else 0.0
        blocked = sum(1 for q in queries if q.get("blocked_by_policy", False))
        
        assert abs(max_ewma - float(row["Max EWMA Risk"])) < 0.001, f"Mismatch in {scenario} max EWMA"
        assert blocked == int(row["Blocked Queries"]), f"Mismatch in {scenario} blocked queries"
        
        # Verify HIGH risk was not reached (threshold is usually 0.70)
        reached_high = any(q["risk_level"] == "HIGH" for q in queries)
        final_results["risk_progression"][scenario]["reached_high_risk"] = reached_high
        
        # Extract Policy Behavior for the scenario
        # We will track the min context limit and min graph depth reached
        min_ctx = min(q["effective_context_limit"] for q in queries) if queries else 20
        min_depth = min(q["effective_graph_depth"] for q in queries) if queries else 5
        min_attenuation = min(q["attenuation_factor"] for q in queries) if queries else 1.0
        
        final_results["policy_behavior"][scenario] = {
            "min_attenuation_factor": min_attenuation,
            "min_effective_context_limit": min_ctx,
            "min_effective_graph_depth": min_depth
        }

    # Add performance overhead
    if p5c_json:
        final_results["performance_overhead"] = p5c_json
        
    with open("scripts/final_experimental_results.json", "w") as f:
        json.dump(final_results, f, indent=2)
        
    print("Cross validation complete. No inconsistencies found.")
    print("Saved final_experimental_results.json")

if __name__ == "__main__":
    main()
