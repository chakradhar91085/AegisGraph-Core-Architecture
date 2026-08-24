import json
import os
import csv
import matplotlib.pyplot as plt

def load_data(filepath="scripts/phase4d_evaluation.json"):
    with open(filepath, "r") as f:
        return json.load(f)

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def create_figure_1(aegis_data, out_dir):
    """Figure 1 - EWMA Risk Progression"""
    scenarios_to_plot = [
        "A_BENIGN_SINGLE_LOOKUP",
        "C_RAPID_REPEATED_PROBING",
        "G_SUSTAINED_RAPID_ENTITY_FOCUSED",
        "H_SUSTAINED_MULTI_VECTOR_GRAPH"
    ]
    
    plt.figure(figsize=(10, 6))
    
    for s_name in scenarios_to_plot:
        if s_name in aegis_data:
            queries = aegis_data[s_name]
            q_nums = [q["query_number"] for q in queries]
            ewma = [q["EWMA_risk"] for q in queries]
            plt.plot(q_nums, ewma, marker='o', label=s_name.replace("_", " "))
    
    plt.axhline(y=0.3, color='y', linestyle='--', alpha=0.7, label='Threshold (MEDIUM)')
    plt.axhline(y=0.7, color='r', linestyle='--', alpha=0.7, label='Threshold (HIGH)')
    
    plt.title("Figure 1: EWMA Risk Progression")
    plt.xlabel("Query Number")
    plt.ylabel("EWMA Risk (0.0 - 1.0)")
    plt.ylim(0, 1.0)
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig1_ewma_risk_progression.png"))
    plt.close()

def create_figure_2(aegis_data, out_dir):
    """Figure 2 - Security Signal Progression"""
    s_name = "H_SUSTAINED_MULTI_VECTOR_GRAPH"
    if s_name not in aegis_data:
        return
        
    queries = aegis_data[s_name]
    q_nums = [q["query_number"] for q in queries]
    s_sem = [q.get("S_sem", 0) for q in queries]
    s_temp = [q.get("S_temp", 0) for q in queries]
    s_ent = [q.get("S_ent", 0) for q in queries]
    s_graph = [q.get("S_graph", 0) for q in queries]
    
    plt.figure(figsize=(10, 6))
    plt.plot(q_nums, s_sem, marker='o', label='Semantic Drift (S_sem)')
    plt.plot(q_nums, s_temp, marker='s', label='Temporal Freq (S_temp)')
    plt.plot(q_nums, s_ent, marker='^', label='Entity Focus (S_ent)')
    plt.plot(q_nums, s_graph, marker='d', label='Graph Footprint (S_graph)')
    
    plt.title(f"Figure 2: Security Signal Progression ({s_name})")
    plt.xlabel("Query Number")
    plt.ylabel("Signal Value (0.0 - 1.0)")
    plt.ylim(0, 1.05)
    plt.grid(True, alpha=0.3)
    plt.legend(loc='best')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig2_security_signal_progression.png"))
    plt.close()

def create_figure_3(base_data, aegis_data, out_dir):
    """Figure 3 - Baseline vs AegisGraph Exposure"""
    scenarios = list(aegis_data.keys())
    
    base_exposure = []
    aegis_exposure = []
    
    for s in scenarios:
        b_val = sum(q.get("records_passed_to_context_builder", 0) for q in base_data.get(s, []))
        a_val = sum(q.get("records_passed_to_context_builder", 0) for q in aegis_data.get(s, []))
        base_exposure.append(b_val)
        aegis_exposure.append(a_val)
        
    x = range(len(scenarios))
    width = 0.35
    
    plt.figure(figsize=(12, 6))
    plt.bar([i - width/2 for i in x], base_exposure, width, label='Baseline Exposure')
    plt.bar([i + width/2 for i in x], aegis_exposure, width, label='AegisGraph Exposure')
    
    plt.title("Figure 3: Controlled Data Exposure Comparison")
    plt.xlabel("Scenario")
    plt.ylabel("Total Records Passed to Context")
    plt.xticks(x, [s.replace("_", "\n")[:20] for s in scenarios], rotation=45, ha="right")
    plt.grid(True, alpha=0.3, axis='y')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig3_baseline_vs_aegisgraph_exposure.png"))
    plt.close()

def create_figure_4(base_data, aegis_data, out_dir):
    """Figure 4 - Exposure Reduction by Scenario"""
    scenarios = list(aegis_data.keys())
    reductions = []
    valid_scenarios = []
    
    for s in scenarios:
        b_val = sum(q.get("records_passed_to_context_builder", 0) for q in base_data.get(s, []))
        a_val = sum(q.get("records_passed_to_context_builder", 0) for q in aegis_data.get(s, []))
        
        if b_val > 0:
            reduction = ((b_val - a_val) / b_val) * 100
            reductions.append(reduction)
            valid_scenarios.append(s)
            
    plt.figure(figsize=(10, 6))
    bars = plt.bar(range(len(valid_scenarios)), reductions)
    
    plt.title("Figure 4: Exposure Reduction by Scenario")
    plt.xlabel("Scenario")
    plt.ylabel("Exposure Reduction (%)")
    plt.xticks(range(len(valid_scenarios)), [s.replace("_", "\n")[:20] for s in valid_scenarios], rotation=45, ha="right")
    
    # Add values on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 1, f"{yval:.1f}%", ha='center', va='bottom')
        
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig4_exposure_reduction.png"))
    plt.close()

def create_figure_5(aegis_data, out_dir):
    """Figure 5 - Adaptive Policy Behavior"""
    s_name = "H_SUSTAINED_MULTI_VECTOR_GRAPH"
    if s_name not in aegis_data:
        return
        
    queries = aegis_data[s_name]
    q_nums = [q["query_number"] for q in queries]
    ewma = [q["EWMA_risk"] for q in queries]
    ctx_limits = [q["effective_context_limit"] for q in queries]
    depth_limits = [q["effective_graph_depth"] for q in queries]
    
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    ax1.set_xlabel('Query Number')
    ax1.set_ylabel('EWMA Risk', color='tab:red')
    ax1.plot(q_nums, ewma, marker='o', color='tab:red', label='EWMA Risk')
    ax1.tick_params(axis='y', labelcolor='tab:red')
    ax1.set_ylim(0, 1.0)
    
    ax2 = ax1.twinx()
    ax2.set_ylabel('Effective Limits', color='tab:blue')
    ax2.plot(q_nums, ctx_limits, marker='s', color='tab:blue', linestyle='--', label='Context Limit')
    ax2.plot(q_nums, depth_limits, marker='^', color='tab:green', linestyle=':', label='Graph Depth')
    ax2.tick_params(axis='y', labelcolor='tab:blue')
    ax2.set_ylim(0, 25)
    
    plt.title(f"Figure 5: Adaptive Policy Behavior ({s_name})")
    fig.tight_layout()
    
    # Combine legends
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper center')
    
    plt.savefig(os.path.join(out_dir, "fig5_adaptive_policy_behavior.png"))
    plt.close()

def create_figure_6(aegis_data, out_dir):
    """Figure 6 - Query Blocking Summary"""
    scenarios = list(aegis_data.keys())
    blocked_counts = []
    
    for s in scenarios:
        count = sum(1 for q in aegis_data.get(s, []) if q.get("blocked_by_policy", False))
        blocked_counts.append(count)
        
    plt.figure(figsize=(10, 6))
    bars = plt.bar(range(len(scenarios)), blocked_counts, color='tab:orange')
    
    plt.title("Figure 6: Query Blocking Summary by Scenario")
    plt.xlabel("Scenario")
    plt.ylabel("Number of Blocked Queries")
    plt.xticks(range(len(scenarios)), [s.replace("_", "\n")[:20] for s in scenarios], rotation=45, ha="right")
    
    # Add values on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, f"{int(yval)}", ha='center', va='bottom')
        
    plt.grid(True, alpha=0.3, axis='y')
    plt.yticks(range(0, max(blocked_counts) + 2))
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig6_query_blocking_summary.png"))
    plt.close()

def write_csv_summary(base_data, aegis_data, out_file):
    scenarios = list(aegis_data.keys())
    
    with open(out_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "Scenario", 
            "Baseline Exposure", 
            "AegisGraph Exposure", 
            "Exposure Reduction %", 
            "Max EWMA Risk", 
            "Final EWMA Risk", 
            "Blocked Queries", 
            "Total Queries"
        ])
        
        for s in scenarios:
            queries = aegis_data.get(s, [])
            total_queries = len(queries)
            if total_queries == 0:
                continue
                
            b_val = sum(q.get("records_passed_to_context_builder", 0) for q in base_data.get(s, []))
            a_val = sum(q.get("records_passed_to_context_builder", 0) for q in queries)
            
            reduction = ((b_val - a_val) / b_val * 100) if b_val > 0 else 0
            
            ewmas = [q["EWMA_risk"] for q in queries]
            max_ewma = max(ewmas)
            final_ewma = ewmas[-1]
            
            blocked = sum(1 for q in queries if q.get("blocked_by_policy", False))
            
            writer.writerow([
                s,
                b_val,
                a_val,
                f"{reduction:.2f}",
                f"{max_ewma:.4f}",
                f"{final_ewma:.4f}",
                blocked,
                total_queries
            ])

def main():
    data = load_data()
    base_data = data.get("BASELINE", {})
    aegis_data = data.get("AEGISGRAPH", {})
    
    out_dir = "docs/figures"
    ensure_dir(out_dir)
    
    print("Generating Figure 1...")
    create_figure_1(aegis_data, out_dir)
    print("Generating Figure 2...")
    create_figure_2(aegis_data, out_dir)
    print("Generating Figure 3...")
    create_figure_3(base_data, aegis_data, out_dir)
    print("Generating Figure 4...")
    create_figure_4(base_data, aegis_data, out_dir)
    print("Generating Figure 5...")
    create_figure_5(aegis_data, out_dir)
    print("Generating Figure 6...")
    create_figure_6(aegis_data, out_dir)
    
    csv_file = "scripts/phase5_results_summary.csv"
    print(f"Generating CSV Summary: {csv_file}")
    write_csv_summary(base_data, aegis_data, csv_file)
    
    print("All tasks completed successfully.")

if __name__ == "__main__":
    main()
