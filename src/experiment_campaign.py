"""
Paired Campaign Engine for 500+ Paired Seeds Across 10 Regimes

CLASSIFICATION LABEL: SIMULATOR_RECONSTRUCTION — NOT NETSQUID
"""

import os
import json
import csv
import time
import numpy as np
from typing import List, Dict, Tuple, Optional

from src.quantum_environment import PhysicalQuantumEvaluator, LinkState, Path, SIMULATOR_TYPE
from src.evsi_evaluator import ParticleBeliefState, EVSISolver
from src.baselines import BaselinePoliciesHarness, POLICY_MAP

POLICY_CODES = ["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"]

REGIMES = {
    "A_obvious_route": {
        "description": "Clearly separated route utilities",
        "A_p1": 0.95, "A_p2": 0.50,
        "p_std": 0.05, "T2": 100.0, "c_fixed": 0.001, "c_bounce": 0.0001
    },
    "B_close_route": {
        "description": "Close competing routes",
        "A_p1": 0.82, "A_p2": 0.81,
        "p_std": 0.05, "T2": 100.0, "c_fixed": 0.001, "c_bounce": 0.0001
    },
    "C_high_uncertainty": {
        "description": "High network-state uncertainty",
        "A_p1": 0.85, "A_p2": 0.80,
        "p_std": 0.20, "T2": 100.0, "c_fixed": 0.001, "c_bounce": 0.0001
    },
    "D_low_uncertainty": {
        "description": "Low network-state uncertainty",
        "A_p1": 0.85, "A_p2": 0.80,
        "p_std": 0.02, "T2": 100.0, "c_fixed": 0.001, "c_bounce": 0.0001
    },
    "E_short_T2": {
        "description": "Short quantum-memory T2",
        "A_p1": 0.85, "A_p2": 0.80,
        "p_std": 0.08, "T2": 5.0, "c_fixed": 0.001, "c_bounce": 0.0001
    },
    "F_long_T2": {
        "description": "Long quantum-memory T2",
        "A_p1": 0.85, "A_p2": 0.80,
        "p_std": 0.08, "T2": 500.0, "c_fixed": 0.001, "c_bounce": 0.0001
    },
    "G_low_cost": {
        "description": "Low benchmarking cost",
        "A_p1": 0.85, "A_p2": 0.80,
        "p_std": 0.08, "T2": 100.0, "c_fixed": 0.0001, "c_bounce": 0.00001
    },
    "H_high_cost": {
        "description": "High benchmarking cost",
        "A_p1": 0.85, "A_p2": 0.80,
        "p_std": 0.08, "T2": 100.0, "c_fixed": 0.05, "c_bounce": 0.005
    },
    "I_route_crossing": {
        "description": "Route-ranking-crossing regimes",
        "A_p1": 0.88, "A_p2": 0.78,
        "p_std": 0.12, "T2": 80.0, "c_fixed": 0.002, "c_bounce": 0.0002
    },
    "J_high_ig_nuisance": {
        "description": "High-information nuisance measurements (IG(a1)>IG(a2) but EVSI(a1)<EVSI(a2))",
        "A_p1": 0.90, "A_p2": 0.70,
        "p_std": 0.25, "T2": 100.0, "c_fixed": 0.001, "c_bounce": 0.0001
    }
}

class CampaignRunner:
    def __init__(self, seeds_per_regime: int = 500):
        self.seeds_per_regime = seeds_per_regime

    def run_campaign(self, base_output_dir: str = "FINAL_EXTERNAL_VALIDATION"):
        print(f"Starting Paired Campaign across 10 Regimes ({self.seeds_per_regime} paired seeds/regime)...")
        print(f"Simulator Classification: {SIMULATOR_TYPE}")

        # Directory structure
        subdirs = [
            "01_environment", "02_qbgp_reproduction", "03_physical_reconstruction",
            "04_evsi", "05_raw_data", "06_statistics", "07_figures",
            "08_baselines", "09_reports", "10_logs"
        ]
        for sd in subdirs:
            os.makedirs(f"{base_output_dir}/{sd}", exist_ok=True)

        os.makedirs("results/evsi_physical_reconstruction", exist_ok=True)

        config_data = {
            "simulator_type": SIMULATOR_TYPE,
            "seeds_per_regime": self.seeds_per_regime,
            "policy_map": POLICY_MAP,
            "regimes": REGIMES
        }

        with open(f"{base_output_dir}/09_reports/experiment_config.json", "w") as f:
            json.dump(config_data, f, indent=2)
        with open("results/evsi_physical_reconstruction/config.json", "w") as f:
            json.dump(config_data, f, indent=2)

        raw_csv_path = f"{base_output_dir}/05_raw_data/paired_campaign_raw.csv"
        
        fieldnames = [
            "regime", "seed", "policy_code", "policy_name", "selected_path",
            "true_downstream_utility", "net_utility", "benchmark_cost", "shots_fired",
            "action_taken", "switched_decision", "gross_evsi", "net_evsi",
            "p_switch", "classical_decision_cost_sec", "total_cost"
        ]

        csv_file = open(raw_csv_path, "w", newline="")
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        all_results = []
        ig_vs_evsi_disagreements = []

        for regime_name, r_cfg in REGIMES.items():
            print(f"---> Executing Regime: {regime_name} ({r_cfg['description']})")
            evaluator = PhysicalQuantumEvaluator(c_fixed=r_cfg['c_fixed'], c_bounce=r_cfg['c_bounce'])
            solver = EVSISolver(evaluator, num_predictive_samples=10)
            harness = BaselinePoliciesHarness(evaluator, solver)

            paths = [
                Path(path_id="P1", links=["L1_1", "L1_2"], hops=2),
                Path(path_id="P2", links=["L2_1", "L2_2", "L2_3"], hops=3),
                Path(path_id="P3", links=["L3_1", "L3_2", "L3_3"], hops=3),
                Path(path_id="P4", links=["L4_1", "L4_2", "L4_3", "L4_4"], hops=4)
            ]

            link_configs = {
                "L1_1": {"T2": r_cfg['T2'], "p_gen": 0.8, "delay": 1.0},
                "L1_2": {"T2": r_cfg['T2'], "p_gen": 0.8, "delay": 1.0},
                "L2_1": {"T2": r_cfg['T2'], "p_gen": 0.8, "delay": 1.0},
                "L2_2": {"T2": r_cfg['T2'], "p_gen": 0.8, "delay": 1.0},
                "L2_3": {"T2": r_cfg['T2'], "p_gen": 0.8, "delay": 1.0},
                "L3_1": {"T2": r_cfg['T2'], "p_gen": 0.8, "delay": 1.0},
                "L3_2": {"T2": r_cfg['T2'], "p_gen": 0.8, "delay": 1.0},
                "L3_3": {"T2": r_cfg['T2'], "p_gen": 0.8, "delay": 1.0},
                "L4_1": {"T2": r_cfg['T2'], "p_gen": 0.8, "delay": 1.0},
                "L4_2": {"T2": r_cfg['T2'], "p_gen": 0.8, "delay": 1.0},
                "L4_3": {"T2": r_cfg['T2'], "p_gen": 0.8, "delay": 1.0},
                "L4_4": {"T2": r_cfg['T2'], "p_gen": 0.8, "delay": 1.0}
            }

            candidate_actions = [
                ("L1_1", 2, 50),
                ("L1_1", 4, 50),
                ("L2_1", 2, 50),
                ("L2_1", 4, 50),
                ("L3_1", 2, 50),
                ("L4_1", 2, 50)
            ]

            for seed in range(1, self.seeds_per_regime + 1):
                rng = np.random.default_rng(seed=seed * 1000 + hash(regime_name) % 10000)

                p1_val = float(np.clip(rng.normal(r_cfg['A_p1'], r_cfg['p_std']), 0.1, 0.98))
                p2_val = float(np.clip(rng.normal(r_cfg['A_p2'], r_cfg['p_std']), 0.1, 0.98))
                p3_val = float(np.clip(rng.normal(r_cfg['A_p2'] * 0.95, r_cfg['p_std']), 0.1, 0.98))
                p4_val = float(np.clip(rng.normal(r_cfg['A_p2'] * 0.90, r_cfg['p_std']), 0.1, 0.98))
                
                true_links = {
                    "L1_1": LinkState(link_id="L1_1", A=0.9, p=p1_val, T2=r_cfg['T2'], p_gen=0.8, delay=1.0),
                    "L1_2": LinkState(link_id="L1_2", A=0.9, p=p1_val, T2=r_cfg['T2'], p_gen=0.8, delay=1.0),
                    "L2_1": LinkState(link_id="L2_1", A=0.9, p=p2_val, T2=r_cfg['T2'], p_gen=0.8, delay=1.0),
                    "L2_2": LinkState(link_id="L2_2", A=0.9, p=p2_val, T2=r_cfg['T2'], p_gen=0.8, delay=1.0),
                    "L2_3": LinkState(link_id="L2_3", A=0.9, p=p2_val, T2=r_cfg['T2'], p_gen=0.8, delay=1.0),
                    "L3_1": LinkState(link_id="L3_1", A=0.9, p=p3_val, T2=r_cfg['T2'], p_gen=0.8, delay=1.0),
                    "L3_2": LinkState(link_id="L3_2", A=0.9, p=p3_val, T2=r_cfg['T2'], p_gen=0.8, delay=1.0),
                    "L3_3": LinkState(link_id="L3_3", A=0.9, p=p3_val, T2=r_cfg['T2'], p_gen=0.8, delay=1.0),
                    "L4_1": LinkState(link_id="L4_1", A=0.9, p=p4_val, T2=r_cfg['T2'], p_gen=0.8, delay=1.0),
                    "L4_2": LinkState(link_id="L4_2", A=0.9, p=p4_val, T2=r_cfg['T2'], p_gen=0.8, delay=1.0),
                    "L4_3": LinkState(link_id="L4_3", A=0.9, p=p4_val, T2=r_cfg['T2'], p_gen=0.8, delay=1.0),
                    "L4_4": LinkState(link_id="L4_4", A=0.9, p=p4_val, T2=r_cfg['T2'], p_gen=0.8, delay=1.0)
                }

                belief = ParticleBeliefState(num_particles=20, rng=rng)
                for l_id in ["L1_1", "L1_2"]:
                    belief.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=r_cfg['A_p1'], p_std=r_cfg['p_std'])
                for l_id in ["L2_1", "L2_2", "L2_3"]:
                    belief.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=r_cfg['A_p2'], p_std=r_cfg['p_std'])
                for l_id in ["L3_1", "L3_2", "L3_3"]:
                    belief.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=r_cfg['A_p2']*0.95, p_std=r_cfg['p_std'])
                for l_id in ["L4_1", "L4_2", "L4_3", "L4_4"]:
                    belief.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=r_cfg['A_p2']*0.90, p_std=r_cfg['p_std'])

                if regime_name == "J_high_ig_nuisance" and seed <= 20:
                    eval_a1 = solver.evaluate_evsi_and_ig(belief, paths, link_configs, "L1_1", m=2, n_shots=50, rng=rng)
                    eval_a2 = solver.evaluate_evsi_and_ig(belief, paths, link_configs, "L2_1", m=2, n_shots=50, rng=rng)
                    if eval_a1['ig'] > eval_a2['ig'] and eval_a1['net_evsi'] < eval_a2['net_evsi']:
                        ig_vs_evsi_disagreements.append({
                            "seed": seed, "regime": regime_name,
                            "a1": "L1_1_m2", "IG_a1": eval_a1['ig'], "Gross_EVSI_a1": eval_a1['gross_evsi'], "Net_EVSI_a1": eval_a1['net_evsi'],
                            "a2": "L2_1_m2", "IG_a2": eval_a2['ig'], "Gross_EVSI_a2": eval_a2['gross_evsi'], "Net_EVSI_a2": eval_a2['net_evsi'],
                            "P_switch_a1": eval_a1['p_switch'], "P_switch_a2": eval_a2['p_switch']
                        })

                for pol_code in POLICY_CODES:
                    res = harness.run_policy(pol_code, true_links, link_configs, belief, paths, candidate_actions, rng)
                    res['regime'] = regime_name
                    res['seed'] = seed
                    writer.writerow(res)
                    all_results.append(res)

        csv_file.close()

        with open(f"{base_output_dir}/05_raw_data/ig_vs_evsi_disagreements.json", "w") as f:
            json.dump(ig_vs_evsi_disagreements, f, indent=2)

        print(f"Paired campaign run complete! Saved {len(all_results)} records to {raw_csv_path}")
        return raw_csv_path
