"""
Information Gain vs Decision Value (EVSI) Analysis Runner

Analyzes the divergence between variance-reduction Information Gain (IG)
and Expected Value of Sample Information (EVSI) across 200 diverse scenarios.
Identifies high-IG / low-decision-value actions and low-IG / high-decision-value actions.
Outputs raw dataset and JSON statistics.
"""

import os
import csv
import json
import numpy as np
from typing import List, Dict, Tuple
from src.quantum_environment import PhysicalQuantumEvaluator, LinkState, Path
from src.evsi_evaluator import ParticleBeliefState, EVSISolver

def run_ig_vs_evsi_analysis(num_scenarios: int = 200, output_dir: str = "results"):
    os.makedirs(f"{output_dir}/raw", exist_ok=True)
    os.makedirs(f"{output_dir}/processed", exist_ok=True)
    raw_csv_path = f"{output_dir}/raw/ig_vs_evsi_analysis.csv"
    
    fieldnames = [
        "scenario_id", "target_link", "m", "n_shots",
        "ig", "gross_evsi", "net_evsi", "benchmark_cost",
        "p_switch", "prior_best_path", "prior_max_u", "actual_route_changed",
        "true_utility_gain", "disagreement_ig_vs_evsi"
    ]
    
    csv_file = open(raw_csv_path, "w", newline="")
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    
    print(f"Starting Information Gain vs EVSI analysis across {num_scenarios} scenarios...")
    
    paths = [
        Path(path_id="P1", links=["L1_1", "L1_2"], hops=2),
        Path(path_id="P2", links=["L2_1", "L2_2", "L2_3"], hops=3),
        Path(path_id="P3", links=["L3_1", "L3_2", "L3_3"], hops=3),
        Path(path_id="P4", links=["L4_1", "L4_2", "L4_3", "L4_4"], hops=4)
    ]
    
    evaluator = PhysicalQuantumEvaluator(c_fixed=0.001, c_bounce=0.0001)
    solver = EVSISolver(evaluator, num_predictive_samples=15)
    
    records = []
    high_ig_low_evsi_examples = []
    low_ig_high_evsi_examples = []
    
    for scenario_id in range(1, num_scenarios + 1):
        rng = np.random.default_rng(seed=scenario_id * 5000)
        
        # Vary prior uncertainty and mean separation
        if scenario_id % 3 == 0:
            p1_mean, p2_mean = 0.90, 0.70
            std_l1, std_l2 = 0.25, 0.10
        elif scenario_id % 3 == 1:
            p1_mean, p2_mean = 0.82, 0.81
            std_l1, std_l2 = 0.12, 0.12
        else:
            p1_mean, p2_mean = 0.95, 0.50
            std_l1, std_l2 = 0.08, 0.08
            
        link_configs = {
            "L1_1": {"T2": 100.0, "p_gen": 0.8, "delay": 1.0},
            "L1_2": {"T2": 100.0, "p_gen": 0.8, "delay": 1.0},
            "L2_1": {"T2": 100.0, "p_gen": 0.8, "delay": 1.0},
            "L2_2": {"T2": 100.0, "p_gen": 0.8, "delay": 1.0},
            "L2_3": {"T2": 100.0, "p_gen": 0.8, "delay": 1.0},
            "L3_1": {"T2": 100.0, "p_gen": 0.8, "delay": 1.0},
            "L3_2": {"T2": 100.0, "p_gen": 0.8, "delay": 1.0},
            "L3_3": {"T2": 100.0, "p_gen": 0.8, "delay": 1.0},
            "L4_1": {"T2": 100.0, "p_gen": 0.8, "delay": 1.0},
            "L4_2": {"T2": 100.0, "p_gen": 0.8, "delay": 1.0},
            "L4_3": {"T2": 100.0, "p_gen": 0.8, "delay": 1.0},
            "L4_4": {"T2": 100.0, "p_gen": 0.8, "delay": 1.0}
        }
        
        p1_val = float(np.clip(rng.normal(p1_mean, std_l1), 0.1, 0.98))
        p2_val = float(np.clip(rng.normal(p2_mean, std_l2), 0.1, 0.98))
        p3_val = float(np.clip(rng.normal(p2_mean * 0.95, std_l2), 0.1, 0.98))
        p4_val = float(np.clip(rng.normal(p2_mean * 0.90, std_l2), 0.1, 0.98))
        
        true_links = {
            "L1_1": LinkState(link_id="L1_1", A=0.9, p=p1_val, T2=100.0, p_gen=0.8, delay=1.0),
            "L1_2": LinkState(link_id="L1_2", A=0.9, p=p1_val, T2=100.0, p_gen=0.8, delay=1.0),
            "L2_1": LinkState(link_id="L2_1", A=0.9, p=p2_val, T2=100.0, p_gen=0.8, delay=1.0),
            "L2_2": LinkState(link_id="L2_2", A=0.9, p=p2_val, T2=100.0, p_gen=0.8, delay=1.0),
            "L2_3": LinkState(link_id="L2_3", A=0.9, p=p2_val, T2=100.0, p_gen=0.8, delay=1.0),
            "L3_1": LinkState(link_id="L3_1", A=0.9, p=p3_val, T2=100.0, p_gen=0.8, delay=1.0),
            "L3_2": LinkState(link_id="L3_2", A=0.9, p=p3_val, T2=100.0, p_gen=0.8, delay=1.0),
            "L3_3": LinkState(link_id="L3_3", A=0.9, p=p3_val, T2=100.0, p_gen=0.8, delay=1.0),
            "L4_1": LinkState(link_id="L4_1", A=0.9, p=p4_val, T2=100.0, p_gen=0.8, delay=1.0),
            "L4_2": LinkState(link_id="L4_2", A=0.9, p=p4_val, T2=100.0, p_gen=0.8, delay=1.0),
            "L4_3": LinkState(link_id="L4_3", A=0.9, p=p4_val, T2=100.0, p_gen=0.8, delay=1.0),
            "L4_4": LinkState(link_id="L4_4", A=0.9, p=p4_val, T2=100.0, p_gen=0.8, delay=1.0)
        }
        
        belief = ParticleBeliefState(num_particles=30, rng=rng)
        for l_id in ["L1_1", "L1_2"]:
            belief.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=p1_mean, p_std=std_l1)
        for l_id in ["L2_1", "L2_2", "L2_3"]:
            belief.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=p2_mean, p_std=std_l2)
        for l_id in ["L3_1", "L3_2", "L3_3"]:
            belief.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=p2_mean*0.95, p_std=std_l2)
        for l_id in ["L4_1", "L4_2", "L4_3", "L4_4"]:
            belief.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=p2_mean*0.90, p_std=std_l2)
        
        candidate_actions = [
            ("L1_1", 2, 50),
            ("L2_1", 2, 50),
            ("L3_1", 2, 50),
            ("L4_1", 2, 50)
        ]
        
        eval_results = {}
        for (l_id, m, n_s) in candidate_actions:
            eval_res = solver.evaluate_evsi_and_ig(belief, paths, link_configs, target_link=l_id, m=m, n_shots=n_s, rng=rng)
            eval_results[(l_id, m, n_s)] = eval_res
            
        best_ig_action = max(eval_results.keys(), key=lambda k: eval_results[k]['ig'])
        best_evsi_action = max(eval_results.keys(), key=lambda k: eval_results[k]['net_evsi'])
        
        disagreement = 1 if best_ig_action != best_evsi_action else 0
        
        for (l_id, m, n_s), res in eval_results.items():
            obs = evaluator.simulate_bounce_observation(true_links[l_id], m=m, n_shots=n_s, rng=rng)
            
            # Compute route under prior
            prior_u_map = {p.path_id: solver.compute_expected_path_utility(p, belief, link_configs) for p in paths}
            prior_p = max(prior_u_map, key=prior_u_map.get)
            prior_true_u = evaluator.evaluate_route_utility([true_links[l] for l in next(p for p in paths if p.path_id == prior_p).links])
            
            # Posterior route selection
            particles = belief.particles[l_id]
            weights = belief.weights[l_id]
            sigma_bm = 0.05 / np.sqrt(n_s)
            pred_means = particles[:, 0] * (particles[:, 1] ** (2 * m))
            diff = obs - pred_means
            likelihood = np.exp(-0.5 * (diff / sigma_bm) ** 2)
            post_weights = weights * likelihood
            if np.sum(post_weights) > 0:
                post_weights /= np.sum(post_weights)
            else:
                post_weights = weights.copy()

            path_post_u = {}
            for path in paths:
                N = belief.num_particles
                w_prod = np.ones(N)
                tot_delay = 0.0
                p_succ = 1.0
                for link_id in path.links:
                    p_val = particles[:, 1] if link_id == l_id else belief.particles[link_id][:, 1]
                    w_prod *= p_val
                    cfg = link_configs[link_id]
                    tot_delay += cfg['delay']
                    p_succ *= cfg['p_gen']
                tot_latency = tot_delay + ((1.0 / p_succ * 0.1) if p_succ > 0 else 100.0)
                resource_hops = len(path.links)
                f_e2e = np.clip(0.25 + 0.75 * w_prod, 0.25, 1.0)
                u_vec = (f_e2e * p_succ) - (evaluator.alpha * tot_latency) - (evaluator.beta * resource_hops)
                if l_id in path.links:
                    path_u = float(np.sum(u_vec * post_weights))
                else:
                    path_u = float(np.mean(u_vec))
                path_post_u[path.path_id] = path_u

            post_p = max(path_post_u, key=path_post_u.get)
            post_true_u = evaluator.evaluate_route_utility([true_links[l] for l in next(p for p in paths if p.path_id == post_p).links])
            
            route_changed = 1 if post_p != prior_p else 0
            true_gain = float(post_true_u - prior_true_u)
            
            rec = {
                "scenario_id": scenario_id,
                "target_link": l_id,
                "m": m,
                "n_shots": n_s,
                "ig": res['ig'],
                "gross_evsi": res['gross_evsi'],
                "net_evsi": res['net_evsi'],
                "benchmark_cost": res['benchmark_cost'],
                "p_switch": res['p_switch'],
                "prior_best_path": prior_p,
                "prior_max_u": res['prior_max_u'],
                "actual_route_changed": route_changed,
                "true_utility_gain": true_gain,
                "disagreement_ig_vs_evsi": disagreement
            }
            writer.writerow(rec)
            records.append(rec)
            
            # Identify illustrative examples
            if res['ig'] > 0.03 and res['net_evsi'] <= 0.0:
                high_ig_low_evsi_examples.append(rec)
            elif res['ig'] < 0.02 and res['net_evsi'] > 0.005:
                low_ig_high_evsi_examples.append(rec)
                
    csv_file.close()
    
    # Compute summary statistics
    igs = np.array([r['ig'] for r in records])
    evsis = np.array([r['net_evsi'] for r in records])
    route_changes = np.array([r['actual_route_changed'] for r in records])
    true_gains = np.array([r['true_utility_gain'] for r in records])
    disagreements = np.array([r['disagreement_ig_vs_evsi'] for r in records])
    
    corr_ig_evsi = float(np.corrcoef(igs, evsis)[0, 1])
    corr_ig_gain = float(np.corrcoef(igs, true_gains)[0, 1])
    corr_evsi_gain = float(np.corrcoef(evsis, true_gains)[0, 1])
    disagreement_rate = float(np.mean(disagreements))
    
    summary = {
        "num_scenarios": num_scenarios,
        "total_action_evaluations": len(records),
        "disagreement_rate": disagreement_rate,
        "correlation_ig_vs_net_evsi": corr_ig_evsi,
        "correlation_ig_vs_true_gain": corr_ig_gain,
        "correlation_evsi_vs_true_gain": corr_evsi_gain,
        "high_ig_low_evsi_sample_count": len(high_ig_low_evsi_examples),
        "low_ig_high_evsi_sample_count": len(low_ig_high_evsi_examples),
        "sample_high_ig_low_evsi": high_ig_low_evsi_examples[:3],
        "sample_low_ig_high_evsi": low_ig_high_evsi_examples[:3]
    }
    
    with open(f"{output_dir}/processed/ig_vs_evsi_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
        
    print(f"IG vs EVSI Analysis complete!")
    print(f"Disagreement Rate: {disagreement_rate * 100:.1f}%")
    print(f"Corr(IG, EVSI): {corr_ig_evsi:.3f} | Corr(EVSI, True Gain): {corr_evsi_gain:.3f} | Corr(IG, True Gain): {corr_ig_gain:.3f}")

if __name__ == "__main__":
    run_ig_vs_evsi_analysis()
