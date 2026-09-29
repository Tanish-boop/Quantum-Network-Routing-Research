"""
Vectorized Posterior-Predictive EVSI Solver Module

CLASSIFICATION LABEL: SIMULATOR_RECONSTRUCTION — NOT NETSQUID
"""

import numpy as np
import time
from typing import List, Dict, Tuple, Optional
from src.quantum_environment import PhysicalQuantumEvaluator, LinkState, Path

class ParticleBeliefState:
    def __init__(self, num_particles: int = 30, rng: Optional[np.random.Generator] = None):
        if rng is None:
            rng = np.random.default_rng()
        self.num_particles = num_particles
        self.rng = rng
        self.particles: Dict[str, np.ndarray] = {}
        self.weights: Dict[str, np.ndarray] = {}

    def initialize_link_prior(self, link_id: str, A_mean: float, A_std: float, p_mean: float, p_std: float):
        A_samples = np.clip(self.rng.normal(A_mean, A_std, self.num_particles), 0.1, 1.0)
        p_samples = np.clip(self.rng.normal(p_mean, p_std, self.num_particles), 0.1, 0.99)
        self.particles[link_id] = np.column_stack((A_samples, p_samples))
        self.weights[link_id] = np.ones(self.num_particles) / self.num_particles

class EVSISolver:
    def __init__(self, evaluator: PhysicalQuantumEvaluator, num_predictive_samples: int = 15):
        self.evaluator = evaluator
        self.num_predictive_samples = num_predictive_samples

    def compute_expected_path_utility(self, path: Path, belief: ParticleBeliefState, link_configs: Dict[str, Dict[str, float]]) -> float:
        N = belief.num_particles
        w_prod = np.ones(N)
        min_t2 = float('inf')
        tot_delay = 0.0
        p_succ = 1.0

        for link_id in path.links:
            p_val = belief.particles[link_id][:, 1]
            w_prod *= p_val
            cfg = link_configs[link_id]
            if cfg['T2'] < min_t2:
                min_t2 = cfg['T2']
            tot_delay += cfg['delay']
            p_succ *= cfg['p_gen']

        expected_wait = (1.0 / p_succ * 0.1) if p_succ > 0 else 100.0
        tot_latency = tot_delay + expected_wait
        resource_hops = len(path.links)

        f_e2e = 0.25 + 0.75 * w_prod  # approximate waiting time = 0 for prior mean
        f_e2e = np.clip(f_e2e, 0.25, 1.0)

        utility = (f_e2e * p_succ) - (self.evaluator.alpha * tot_latency) - (self.evaluator.beta * resource_hops)
        return float(np.sum(utility * belief.weights[path.links[0]]))

    def evaluate_evsi_and_ig(
        self,
        belief: ParticleBeliefState,
        paths: List[Path],
        link_configs: Dict[str, Dict[str, float]],
        target_link: str,
        m: int,
        n_shots: int = 100,
        rng: Optional[np.random.Generator] = None
    ) -> Dict[str, float]:
        start_time = time.time()
        if rng is None:
            rng = np.random.default_rng()

        path_prior_utilities = {}
        for p in paths:
            path_prior_utilities[p.path_id] = self.compute_expected_path_utility(p, belief, link_configs)
        
        best_prior_path = max(path_prior_utilities, key=path_prior_utilities.get)
        prior_max_u = path_prior_utilities[best_prior_path]

        particles = belief.particles[target_link]
        weights = belief.weights[target_link]
        sigma_bm = 0.05 / np.sqrt(n_shots)
        
        sampled_indices = rng.choice(belief.num_particles, size=self.num_predictive_samples, p=weights)
        
        A_vals = particles[sampled_indices, 0]
        p_vals = particles[sampled_indices, 1]
        obs_Y = rng.normal(A_vals * (p_vals ** (2 * m)), sigma_bm)
        obs_Y = np.clip(obs_Y, 0.0, 1.0)

        # Vectorized likelihood calculation: shape (num_samples, num_particles)
        pred_means = particles[:, 0] * (particles[:, 1] ** (2 * m)) # (N,)
        diff = obs_Y[:, np.newaxis] - pred_means[np.newaxis, :]    # (M, N)
        likelihoods = np.exp(-0.5 * (diff / sigma_bm) ** 2)

        post_weights = weights[np.newaxis, :] * likelihoods        # (M, N)
        sums = np.sum(post_weights, axis=1, keepdims=True)
        sums[sums == 0] = 1.0
        post_weights /= sums

        posterior_max_utilities = []
        switches = 0
        ig_list = []
        prior_var = float(np.var(particles[:, 1]))

        for j in range(self.num_predictive_samples):
            pw_j = post_weights[j, :]
            path_post_u = {}

            for path in paths:
                N = belief.num_particles
                w_prod = np.ones(N)
                min_t2 = float('inf')
                tot_delay = 0.0
                p_succ = 1.0

                for link_id in path.links:
                    p_val = particles[:, 1] if link_id == target_link else belief.particles[link_id][:, 1]
                    w_prod *= p_val
                    cfg = link_configs[link_id]
                    if cfg['T2'] < min_t2:
                        min_t2 = cfg['T2']
                    tot_delay += cfg['delay']
                    p_succ *= cfg['p_gen']

                tot_latency = tot_delay + ((1.0 / p_succ * 0.1) if p_succ > 0 else 100.0)
                resource_hops = len(path.links)
                f_e2e = np.clip(0.25 + 0.75 * w_prod, 0.25, 1.0)
                u_vec = (f_e2e * p_succ) - (self.evaluator.alpha * tot_latency) - (self.evaluator.beta * resource_hops)

                if target_link in path.links:
                    path_u = float(np.sum(u_vec * pw_j))
                else:
                    path_u = float(np.mean(u_vec))
                path_post_u[path.path_id] = path_u

            best_post_p = max(path_post_u, key=path_post_u.get)
            post_max_u = path_post_u[best_post_p]
            posterior_max_utilities.append(post_max_u)

            if best_post_p != best_prior_path:
                switches += 1

            post_var = float(np.sum(pw_j * (particles[:, 1] - np.sum(pw_j * particles[:, 1])) ** 2))
            ig_list.append(max(0.0, prior_var - post_var))

        expected_post_u = float(np.mean(posterior_max_utilities))
        benchmark_cost = self.evaluator.compute_benchmark_cost(m, n_shots)
        
        gross_evsi = expected_post_u - prior_max_u
        net_evsi = gross_evsi - benchmark_cost
        p_switch = switches / self.num_predictive_samples
        mean_ig = float(np.mean(ig_list))
        
        calc_time = time.time() - start_time

        return {
            'target_link': target_link,
            'm': m,
            'n_shots': n_shots,
            'gross_evsi': gross_evsi,
            'net_evsi': net_evsi,
            'evsi': net_evsi,
            'ig': mean_ig,
            'p_switch': p_switch,
            'prior_best_path': best_prior_path,
            'prior_max_u': prior_max_u,
            'benchmark_cost': benchmark_cost,
            'calc_time_sec': calc_time
        }
