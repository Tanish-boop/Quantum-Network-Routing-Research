"""
Acquisition Cost Sweep Experiment Runner

Sweeps information acquisition cost multiplier C across [0.0, 0.01, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30].
Evaluates policies P0 to P8 using paired Monte Carlo seeds.
Saves raw CSV and processed summary.
"""

import os
import csv
import json
import numpy as np
from typing import List, Dict, Tuple
from src.quantum_environment import PhysicalQuantumEvaluator, LinkState, Path
from src.evsi_evaluator import ParticleBeliefState, EVSISolver
from src.baselines import BaselinePoliciesHarness, POLICY_MAP

POLICY_CODES = ["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"]
COST_MULTIPLIERS = [0.0, 0.01, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30]

def run_cost_sweep(num_seeds: int = 100, output_dir: str = "results"):
    os.makedirs(f"{output_dir}/raw", exist_ok=True)
    os.makedirs(f"{output_dir}/processed", exist_ok=True)
    raw_csv_path = f"{output_dir}/raw/cost_sweep_raw.csv"
    
    fieldnames = [
        "cost_multiplier", "seed", "policy_code", "policy_name", "selected_path",
        "true_downstream_utility", "net_utility", "benchmark_cost", "shots_fired",
        "action_taken", "switched_decision", "gross_evsi", "net_evsi",
        "p_switch", "classical_decision_cost_sec", "total_cost", "oracle_regret"
    ]
    
    csv_file = open(raw_csv_path, "w", newline="")
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    
    print(f"Starting Cost Sweep across {len(COST_MULTIPLIERS)} cost levels x {num_seeds} paired seeds...")
    
    paths = [
        Path(path_id="P1", links=["L1_1", "L1_2"], hops=2),
        Path(path_id="P2", links=["L2_1", "L2_2", "L2_3"], hops=3),
        Path(path_id="P3", links=["L3_1", "L3_2", "L3_3"], hops=3),
        Path(path_id="P4", links=["L4_1", "L4_2", "L4_3", "L4_4"], hops=4)
    ]
    
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
    
    candidate_actions = [
        ("L1_1", 2, 50),
        ("L1_1", 4, 50),
        ("L2_1", 2, 50),
        ("L2_1", 4, 50),
        ("L3_1", 2, 50),
        ("L4_1", 2, 50)
    ]
    
    records_written = 0
    for c_mult in COST_MULTIPLIERS:
        c_fixed = 0.001 * (1.0 if c_mult == 0.0 else c_mult * 10.0)
        c_bounce = 0.0001 * (1.0 if c_mult == 0.0 else c_mult * 10.0)
        
        evaluator = PhysicalQuantumEvaluator(c_fixed=c_fixed, c_bounce=c_bounce)
        solver = EVSISolver(evaluator, num_predictive_samples=10)
        harness = BaselinePoliciesHarness(evaluator, solver)
        
        for seed in range(1, num_seeds + 1):
            rng = np.random.default_rng(seed=seed * 2000 + int(c_mult * 100))
            
            p1_val = float(np.clip(rng.normal(0.85, 0.10), 0.1, 0.98))
            p2_val = float(np.clip(rng.normal(0.80, 0.10), 0.1, 0.98))
            p3_val = float(np.clip(rng.normal(0.76, 0.10), 0.1, 0.98))
            p4_val = float(np.clip(rng.normal(0.72, 0.10), 0.1, 0.98))
            
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
            
            belief = ParticleBeliefState(num_particles=20, rng=rng)
            for l_id in ["L1_1", "L1_2"]:
                belief.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=0.85, p_std=0.10)
            for l_id in ["L2_1", "L2_2", "L2_3"]:
                belief.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=0.80, p_std=0.10)
            for l_id in ["L3_1", "L3_2", "L3_3"]:
                belief.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=0.76, p_std=0.10)
            for l_id in ["L4_1", "L4_2", "L4_3", "L4_4"]:
                belief.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=0.72, p_std=0.10)
            
            oracle_res = harness.run_policy("P8", true_links, link_configs, belief, paths, candidate_actions, rng)
            oracle_u = oracle_res['net_utility']
            
            for pol_code in POLICY_CODES:
                res = harness.run_policy(pol_code, true_links, link_configs, belief, paths, candidate_actions, rng)
                res['cost_multiplier'] = c_mult
                res['seed'] = seed
                res['oracle_regret'] = float(oracle_u - res['net_utility'])
                writer.writerow(res)
                records_written += 1
                
    csv_file.close()
    print(f"Cost sweep finished! Saved {records_written} rows to {raw_csv_path}")

if __name__ == "__main__":
    run_cost_sweep()
