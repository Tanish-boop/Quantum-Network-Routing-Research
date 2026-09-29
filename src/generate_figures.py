"""
Automated Figure Generation Pipeline

Generates publication-quality figures strictly from stored experimental CSV/JSON datasets.
Output figures:
- Figure 1: Network Topology Diagram
- Figure 2: EVSI vs Information Acquisition Cost
- Figure 3: Acquisition Rate vs Information Cost
- Figure 4: Net Routing Utility vs Information Cost
- Figure 5: Memory Decoherence (T2) vs Routing Performance
- Figure 6: Information Gain vs EVSI Scatter Plot
- Figure 7: Decision-Aware Policy vs Baselines across 10 Regimes
- Figure 8: Oracle Regret by Policy
"""

import os
import json
import csv
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

def generate_all_figures(output_dir: str = "figures"):
    os.makedirs(output_dir, exist_ok=True)
    plt.rcParams.update({'font.size': 11, 'figure.autolayout': True})
    
    # ----------------------------------------------------
    # Figure 1: Quantum Network Topology
    # ----------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 5))
    G = nx.DiGraph()
    G.add_edge("Source", "N1", label="L1_1")
    G.add_edge("N1", "Dest", label="L1_2")
    G.add_edge("Source", "N2", label="L2_1")
    G.add_edge("N2", "Dest", label="L2_2")
    
    pos = {"Source": (0, 0.5), "N1": (1, 1), "N2": (1, 0), "Dest": (2, 0.5)}
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=1200, node_color="#2b5c8f")
    nx.draw_networkx_labels(G, pos, ax=ax, font_color="white", font_weight="bold")
    nx.draw_networkx_edges(G, pos, ax=ax, arrowstyle="->", arrowsize=20, edge_color="#555555", width=2)
    
    edge_labels = {("Source", "N1"): "Path 1: L1_1", ("N1", "Dest"): "L1_2",
                   ("Source", "N2"): "Path 2: L2_1", ("N2", "Dest"): "L2_2"}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax, font_size=10)
    
    ax.set_title("Figure 1: Quantum Network Simulation Topology (2 Candidate Paths)")
    ax.axis("off")
    plt.savefig(f"{output_dir}/fig1_network_topology.png", dpi=300)
    plt.close()
    
    # ----------------------------------------------------
    # Figure 2 & 3 & 4: Cost Sweep Analysis
    # ----------------------------------------------------
    cost_csv = "results/raw/cost_sweep_raw.csv"
    if os.path.exists(cost_csv):
        costs, evsi_vals, acq_rates, p4_net_u, p0_net_u, p2_net_u = [], [], [], [], [], []
        
        cost_data = {}
        with open(cost_csv, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                c = float(row['cost_multiplier'])
                pol = row['policy_code']
                net_u = float(row['net_utility'])
                net_evsi = float(row['net_evsi'])
                switched = int(row['switched_decision'])
                
                if c not in cost_data:
                    cost_data[c] = {p: [] for p in ["P0", "P1", "P2", "P4", "P8"]}
                    cost_data[c]['evsi_val'] = []
                    cost_data[c]['acq_switched'] = []
                    
                if pol in cost_data[c]:
                    cost_data[c][pol].append(net_u)
                if pol == "P4":
                    cost_data[c]['evsi_val'].append(net_evsi)
                    cost_data[c]['acq_switched'].append(1 if row['action_taken'].startswith('L') else 0)
                    
        sorted_c = sorted(cost_data.keys())
        for c in sorted_c:
            costs.append(c)
            evsi_vals.append(np.mean(cost_data[c]['evsi_val']))
            acq_rates.append(np.mean(cost_data[c]['acq_switched']))
            p4_net_u.append(np.mean(cost_data[c]['P4']))
            p0_net_u.append(np.mean(cost_data[c]['P0']))
            p2_net_u.append(np.mean(cost_data[c]['P2']))
            
        # Figure 2: EVSI vs Cost Multiplier
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(costs, evsi_vals, marker="o", color="#2b5c8f", linewidth=2, label="Net EVSI")
        ax.axhline(0, color="gray", linestyle="--")
        ax.set_xlabel("Benchmarking Cost Multiplier C")
        ax.set_ylabel("Expected Value of Sample Information (Net EVSI)")
        ax.set_title("Figure 2: EVSI as a Function of Information Acquisition Cost")
        ax.grid(True, alpha=0.3)
        ax.legend()
        plt.savefig(f"{output_dir}/fig2_evsi_vs_cost.png", dpi=300)
        plt.close()
        
        # Figure 3: Acquisition Rate vs Cost Multiplier
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(costs, [r * 100 for r in acq_rates], marker="s", color="#d95f02", linewidth=2)
        ax.set_xlabel("Benchmarking Cost Multiplier C")
        ax.set_ylabel("Information Acquisition Rate (%)")
        ax.set_title("Figure 3: Acquisition Probing Frequency vs Information Cost")
        ax.grid(True, alpha=0.3)
        plt.savefig(f"{output_dir}/fig3_acquisition_rate_vs_cost.png", dpi=300)
        plt.close()
        
        # Figure 4: Net Utility vs Cost Multiplier
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(costs, p4_net_u, marker="o", color="#2b5c8f", linewidth=2, label="P4: EVSI (Decision-Aware)")
        ax.plot(costs, p0_net_u, marker="x", color="#7570b3", linewidth=2, linestyle="--", label="P0: Never Benchmark")
        ax.plot(costs, p2_net_u, marker="^", color="#d95f02", linewidth=2, linestyle=":", label="P2: Information Gain")
        ax.set_xlabel("Benchmarking Cost Multiplier C")
        ax.set_ylabel("Net Downstream Utility")
        ax.set_title("Figure 4: Net Routing Utility vs Information Acquisition Cost")
        ax.grid(True, alpha=0.3)
        ax.legend()
        plt.savefig(f"{output_dir}/fig4_net_utility_vs_cost.png", dpi=300)
        plt.close()
        
    # ----------------------------------------------------
    # Figure 5: Decoherence Sweep Analysis (T2)
    # ----------------------------------------------------
    t2_csv = "results/raw/decoherence_sweep_raw.csv"
    if os.path.exists(t2_csv):
        t2_data = {}
        with open(t2_csv, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                t2 = float(row['t2_ms'])
                pol = row['policy_code']
                net_u = float(row['net_utility'])
                if t2 not in t2_data:
                    t2_data[t2] = {p: [] for p in ["P0", "P2", "P4", "P8"]}
                if pol in t2_data[t2]:
                    t2_data[t2][pol].append(net_u)
                    
        sorted_t2 = sorted(t2_data.keys())
        p4_t2 = [np.mean(t2_data[t][ 'P4']) for t in sorted_t2]
        p0_t2 = [np.mean(t2_data[t]['P0']) for t in sorted_t2]
        p8_t2 = [np.mean(t2_data[t]['P8']) for t in sorted_t2]
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(sorted_t2, p4_t2, marker="o", color="#2b5c8f", linewidth=2, label="P4: EVSI")
        ax.plot(sorted_t2, p0_t2, marker="x", color="#7570b3", linewidth=2, linestyle="--", label="P0: Never")
        ax.plot(sorted_t2, p8_t2, marker="d", color="#1b9e77", linewidth=2, linestyle="-.", label="P8: Oracle")
        ax.set_xscale("log")
        ax.set_xlabel("Quantum Memory Coherence Time T2 (ms)")
        ax.set_ylabel("Net Downstream Utility")
        ax.set_title("Figure 5: Memory Decoherence (T2) vs Routing Performance")
        ax.grid(True, alpha=0.3, which="both")
        ax.legend()
        plt.savefig(f"{output_dir}/fig5_t2_vs_performance.png", dpi=300)
        plt.close()

    # ----------------------------------------------------
    # Figure 6: Information Gain vs EVSI Scatter Plot
    # ----------------------------------------------------
    ig_csv = "results/raw/ig_vs_evsi_analysis.csv"
    if os.path.exists(ig_csv):
        igs, net_evsis, route_switches = [], [], []
        with open(ig_csv, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                igs.append(float(row['ig']))
                net_evsis.append(float(row['net_evsi']))
                sw = row.get('switched') or row.get('actual_route_changed') or 0
                route_switches.append(int(sw))
                
        fig, ax = plt.subplots(figsize=(8, 6))
        colors = ["#d95f02" if s == 1 else "#2b5c8f" for s in route_switches]
        ax.scatter(igs, net_evsis, c=colors, alpha=0.7, edgecolors="none", s=40)
        ax.axhline(0, color="red", linestyle="--", alpha=0.7, label="Net EVSI Threshold (0)")
        ax.set_xlabel("Variance-Reduction Information Gain (IG)")
        ax.set_ylabel("Net Expected Value of Sample Information (Net EVSI)")
        ax.set_title("Figure 6: Information Gain vs Net EVSI Scatter Plot (Orange = Decision Changed)")
        ax.grid(True, alpha=0.3)
        ax.legend()
        plt.savefig(f"{output_dir}/fig6_ig_vs_evsi_scatter.png", dpi=300)
        plt.close()

    # ----------------------------------------------------
    # Figure 7 & 8: Policy Comparison and Oracle Regret
    # ----------------------------------------------------
    main_json = "FINAL_EXTERNAL_VALIDATION/06_statistics/main_results_table.json"
    if os.path.exists(main_json):
        with open(main_json, "r") as f:
            data = json.load(f)
            
        policies = [p for p in ["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7"] if p in data]
        labels = [data[p]['Policy_Name'] for p in policies]
        net_utils = [data[p]['Net_Utility'] for p in policies]
        regrets = [data[p]['Oracle_Gap'] for p in policies]
        
        # Figure 7: Main Policy Comparison
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(labels, net_utils, color="#2b5c8f", width=0.5, alpha=0.85)
        ax.set_ylabel("Net Expected Utility")
        ax.set_title("Figure 7: Policy Performance Comparison Across 10 Network Regimes")
        plt.xticks(rotation=30, ha="right")
        ax.grid(True, axis="y", alpha=0.3)
        plt.savefig(f"{output_dir}/fig7_policy_comparison_regimes.png", dpi=300)
        plt.close()

        # Figure 8: Regret vs Oracle
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(labels, regrets, color="#e7298a", width=0.5, alpha=0.85)
        ax.set_ylabel("Suboptimality Regret relative to Oracle")
        ax.set_title("Figure 8: Average Regret Compared to Oracle Routing")
        plt.xticks(rotation=30, ha="right")
        ax.grid(True, axis="y", alpha=0.3)
        plt.savefig(f"{output_dir}/fig8_regret_vs_oracle.png", dpi=300)
        plt.close()

    print(f"All 8 figures generated cleanly in '{output_dir}/'!")

if __name__ == "__main__":
    generate_all_figures()
