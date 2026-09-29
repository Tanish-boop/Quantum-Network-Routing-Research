"""
Physically Grounded Discrete-Event Quantum Network Simulator

CLASSIFICATION LABEL: SIMULATOR_RECONSTRUCTION — NOT NETSQUID

Models physical link states, Werner state swapping fidelity decay, memory T2 decoherence,
bounce measurement model b_m = A * p^(2m), latency, and frozen route utilities.
"""

import numpy as np
import yaml
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

SIMULATOR_TYPE = "SIMULATOR_RECONSTRUCTION — NOT NETSQUID"

@dataclass
class LinkState:
    link_id: str
    A: float              # Initial state parameter / visibility scale (0 < A <= 1)
    p: float              # Depolarizing parameter (0 < p <= 1), link fidelity F = (1+p)/2
    T2: float             # Quantum memory coherence time (ms)
    p_gen: float          # Entanglement generation success probability per trial
    delay: float          # Transmission latency per link (ms)

    @property
    def fidelity(self) -> float:
        return (1.0 + self.p) / 2.0

    @property
    def visibility(self) -> float:
        return self.p

@dataclass
class Path:
    path_id: str
    links: List[str]
    hops: int

class PhysicalQuantumEvaluator:
    """
    Physical Quantum Network Route Evaluator.
    Loads frozen utility definition from configs/utility_definition.yaml.
    """
    def __init__(self, config_path: str = "configs/utility_definition.yaml", c_fixed: Optional[float] = None, c_bounce: Optional[float] = None):
        try:
            with open(config_path, "r") as f:
                cfg = yaml.safe_load(f)["utility_definition"]["parameters"]
                self.alpha = cfg["alpha"]
                self.beta = cfg["beta"]
                self.c_fixed = c_fixed if c_fixed is not None else cfg["c_fixed"]
                self.c_bounce = c_bounce if c_bounce is not None else cfg["c_bounce"]
        except Exception:
            self.alpha = 0.05
            self.beta = 0.02
            self.c_fixed = c_fixed if c_fixed is not None else 0.001
            self.c_bounce = c_bounce if c_bounce is not None else 0.0001

    def compute_e2e_fidelity(self, path_links: List[LinkState], wait_time: float = 0.0) -> float:
        if not path_links:
            return 0.25
        w_prod = 1.0
        min_t2 = float('inf')
        for link in path_links:
            w_prod *= link.visibility
            if link.T2 < min_t2:
                min_t2 = link.T2
        
        decoherence_factor = np.exp(-wait_time / min_t2) if min_t2 > 0 else 0.0
        w_e2e = w_prod * decoherence_factor
        f_e2e = 0.25 + 0.75 * w_e2e
        return float(np.clip(f_e2e, 0.25, 1.0))

    def compute_success_prob(self, path_links: List[LinkState]) -> float:
        if not path_links:
            return 0.0
        p_succ = 1.0
        for link in path_links:
            p_succ *= link.p_gen
        return float(p_succ)

    def compute_latency(self, path_links: List[LinkState]) -> float:
        if not path_links:
            return float('inf')
        tot_delay = sum(link.delay for link in path_links)
        p_succ = self.compute_success_prob(path_links)
        wait_trials = (1.0 / p_succ) if p_succ > 0 else 1000.0
        expected_wait = wait_trials * 0.1
        return float(tot_delay + expected_wait)

    def evaluate_route_utility(self, path_links: List[LinkState], wait_time: float = 0.0) -> float:
        f_e2e = self.compute_e2e_fidelity(path_links, wait_time)
        p_succ = self.compute_success_prob(path_links)
        latency = self.compute_latency(path_links)
        resource_hops = len(path_links)
        utility = (f_e2e * p_succ) - (self.alpha * latency) - (self.beta * resource_hops)
        return float(utility)

    def simulate_bounce_observation(self, link: LinkState, m: int, n_shots: int = 100, rng: Optional[np.random.Generator] = None) -> float:
        if rng is None:
            rng = np.random.default_rng()
        true_val = link.A * (link.p ** (2 * m))
        sigma_bm = 0.05
        noise = rng.normal(0, sigma_bm / np.sqrt(n_shots))
        obs = true_val + noise
        return float(np.clip(obs, 0.0, 1.0))

    def compute_benchmark_cost(self, m: int, n_shots: int = 100) -> float:
        return self.c_fixed + self.c_bounce * m * n_shots
