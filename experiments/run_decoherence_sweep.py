"""
Memory Decoherence (T2) Sweep Experiment Runner

Sweeps quantum memory coherence time T2 across [1.0, 5.0, 10.0, 25.0, 50.0, 100.0, 250.0, 500.0, 1000.0] ms.
Evaluates policies P0 to P8 across paired seeds.
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
T2_VALUES = [1.0, 5.0, 10.0, 25.0, 50.0, 100.0, 250.0, 500.0, 1000.0]

def run_decoherence_sweep(num_seeds: int = 100, output_dir: str = "results"):
    os.makedirs(f"{output_dir}/raw", exist_ok=True)
    os.makedirs(f"{output_dir}/processed", exist_ok=True)
    raw_csv_path = f"{output_dir}/raw/decoherence_sweep_raw.csv"
    
    fieldnames = [
        "t2_ms", "seed", "policy_code", "policy_name", "selected_path",
        "true_downstream_utility", "net_utility", "benchmark_cost", "shots_fired",
        "action_taken", "switched_decision", "gross_evsi", "net_evsi",
        "p_switch", "classical_decision_cost_sec", "total_cost", "oracle_regret"
    ]
    
    csv_file = open(raw_csv_path, "w", newline="")
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    
    print(f"Starting Memory Decoherence (T2) Sweep across {len(T2_VALUES)} T2 levels x {num_seeds} paired seeds...")
    
    paths = [
        Path(path_id="P1", links=["L1_1", "L1_2"], hops=2),
        Path(path_id="P2", links=["L2_1", "L2_2", "L2_3"], hops=3),
        Path(path_id="P3", links=["L3_1", "L3_2", "L3_3"], hops=3),
        Path(path_id="P4", links=["L4_1", "L4_2", "L4_3", "L4_4"], hops=4)
    ]
    
    evaluator = PhysicalQuantumEvaluator(c_fixed=0.001, c_bounce=0.0001)
    solver = EVSISolver(evaluator, num_predictive_samples=10)
    harness = BaselinePoliciesHarness(evaluator, solver)
    
    records_written = 0
    for t2_val in T2_VALUES:
        link_configs = {
            "L1_1": {"T2": t2_val, "p_gen": 0.8, "delay": 1.0},
            "L1_2": {"T2": t2_val, "p_gen": 0.8, "delay": 1.0},
            "L2_1": {"T2": t2_val, "p_gen": 0.8, "delay": 1.0},
            "L2_2": {"T2": t2_val, "p_gen": 0.8, "delay": 1.0},
            "L2_3": {"T2": t2_val, "p_gen": 0.8, "delay": 1.0},
            "L3_1": {"T2": t2_val, "p_gen": 0.8, "delay": 1.0},
            "L3_2": {"T2": t2_val, "p_gen": 0.8, "delay": 1.0},
            "L3_3": {"T2": t2_val, "p_gen": 0.8, "delay": 1.0},
            "L4_1": {"T2": t2_val, "p_gen": 0.8, "delay": 1.0},
            "L4_2": {"T2": t2_val, "p_gen": 0.8, "delay": 1.0},
            "L4_3": {"T2": t2_val, "p_gen": 0.8, "delay": 1.0},
            "L4_4": {"T2": t2_val, "p_gen": 0.8, "delay": 1.0}
        }
        
        candidate_actions = [
            ("L1_1", 2, 50),
            ("L1_1", 4, 50),
            ("L2_1", 2, 50),
            ("L2_1", 4, 50),
            ("L3_1", 2, 50),
            ("L4_1", 2, 50)
        ]
        
        for seed in range(1, num_seeds + 1):
            rng = np.random.default_rng(seed=seed * 3000 + int(t2_val))
            
            p1_val = float(np.clip(rng.normal(0.85, 0.10), 0.1, 0.98))
            p2_val = float(np.clip(rng.normal(0.80, 0.10), 0.1, 0.98))
            p3_val = float(np.clip(rng.normal(0.76, 0.10), 0.1, 0.98))
            p4_val = float(np.clip(rng.normal(0.72, 0.10), 0.1, 0.98))
            
            true_links = {
                "L1_1": LinkState(link_id="L1_1", A=0.9, p=p1_val, T2=t2_val, p_gen=0.8, delay=1.0),
                "L1_2": LinkState(link_id="L1_2", A=0.9, p=p1_val, T2=t2_val, p_gen=0.8, delay=1.0),
                "L2_1": LinkState(link_id="L2_1", A=0.9, p=p2_val, T2=t2_val, p_gen=0.8, delay=1.0),
                "L2_2": LinkState(link_id="L2_2", A=0.9, p=p2_val, T2=t2_val, p_gen=0.8, delay=1.0),
                "L2_3": LinkState(link_id="L2_3", A=0.9, p=p2_val, T2=t2_val, p_gen=0.8, delay=1.0),
                "L3_1": LinkState(link_id="L3_1", A=0.9, p=p3_val, T2=t2_val, p_gen=0.8, delay=1.0),
                "L3_2": LinkState(link_id="L3_2", A=0.9, p=p3_val, T2=t2_val, p_gen=0.8, delay=1.0),
                "L3_3": LinkState(link_id="L3_3", A=0.9, p=p3_val, T2=t2_val, p_gen=0.8, delay=1.0),
                "L4_1": LinkState(link_id="L4_1", A=0.9, p=p4_val, T2=t2_val, p_gen=0.8, delay=1.0),
                "L4_2": LinkState(link_id="L4_2", A=0.9, p=p4_val, T2=t2_val, p_gen=0.8, delay=1.0),
                "L4_3": LinkState(link_id="L4_3", A=0.9, p=p4_val, T2=t2_val, p_gen=0.8, delay=1.0),
                "L4_4": LinkState(link_id="L4_4", A=0.9, p=p4_val, T2=t2_val, p_gen=0.8, delay=1.0)
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
                res['t2_ms'] = t2_val
                res['seed'] = seed
                res['oracle_regret'] = float(oracle_u - res['net_utility'])
                writer.writerow(res)
                records_written += 1
                
    csv_file.close()
    print(f"Decoherence sweep finished! Saved {records_written} rows to {raw_csv_path}")

if __name__ == "__main__":
    run_decoherence_sweep()
