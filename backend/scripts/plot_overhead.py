import json
import os
import matplotlib.pyplot as plt

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def load_data(filepath="scripts/phase5c_performance.json"):
    with open(filepath, "r") as f:
        return json.load(f)

def create_overhead_figure(data, out_dir):
    sec = data.get("security_computation_statistics", {})
    base = data.get("baseline_retrieval_statistics", {})
    prot = data.get("protected_retrieval_statistics", {})

    labels = ['Baseline Retrieval', 'Security Overhead', 'Protected Retrieval']
    
    # We will plot the mean latencies
    base_val = base.get("mean_ms", 0)
    sec_val = sec.get("mean_ms", 0)
    prot_val = prot.get("mean_ms", 0)
    
    values = [base_val, sec_val, prot_val]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, values, color=['#2ca02c', '#d62728', '#1f77b4'])
    
    plt.title("Figure 7: AegisGraph Performance Overhead (per query)")
    plt.ylabel("Mean Latency (ms)")
    
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + (max(values)*0.02), f"{yval:.2f} ms", ha='center', va='bottom', fontweight='bold')
        
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig7_security_overhead.png"))
    plt.close()

def main():
    try:
        data = load_data()
        out_dir = "docs/figures"
        ensure_dir(out_dir)
        print("Generating Figure 7...")
        create_overhead_figure(data, out_dir)
        print("Figure 7 generated successfully.")
    except Exception as e:
        print(f"Error generating plot: {e}")

if __name__ == "__main__":
    main()
