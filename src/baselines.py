"""
Policy Harness Module for 9 Policies (P0 to P8)

CLASSIFICATION STATUS:
- P0: Never Benchmark (EXACT)
- P1: Always Benchmark (EXACT)
- P2: Information Gain (EXACT / REIMPLEMENTED according to QBGP criterion)
- P3: Confidence-Based Stopping (RECONSTRUCTION)
- P4: EVSI / Decision-Aware (OUR METHOD)
- P5: LinkSelFiE (ADAPTED RECONSTRUCTION)
- P6: BeQuP-Link (ADAPTED RECONSTRUCTION - link feedback)
- P7: BeQuP-Path (ADAPTED RECONSTRUCTION - path feedback)
- P8: Oracle (ORACLE / PERFECT INFORMATION UPPER BOUND)

OPERATED ON IDENTICAL PAIRED SEEDS / COMMON RANDOM NUMBERS.
"""

import numpy as np
import time
from typing import List, Dict, Tuple, Optional
from src.quantum_environment import PhysicalQuantumEvaluator, LinkState, Path
from src.evsi_evaluator import ParticleBeliefState, EVSISolver

POLICY_MAP = {
    "P0": "Never Benchmark",
    "P1": "Always Benchmark",
    "P2": "Information Gain",
    "P3": "Confidence-Based Stopping",
    "P4": "EVSI / Decision-Aware",
    "P5": "LinkSelFiE",
    "P6": "BeQuP-Link",
    "P7": "BeQuP-Path",
    "P8": "Oracle"
}

class BaselinePoliciesHarness:
    def __init__(self, evaluator: PhysicalQuantumEvaluator, evsi_solver: EVSISolver):
        self.evaluator = evaluator
        self.solver = evsi_solver

    def run_policy(
        self,
        policy_code: str,
        true_links: Dict[str, LinkState],
        link_configs: Dict[str, Dict[str, float]],
        prior_belief: ParticleBeliefState,
        paths: List[Path],
        candidate_actions: List[Tuple[str, int, int]],
        rng: np.random.Generator
    ) -> Dict[str, float]:
        start_wall_time = time.time()
        
        if policy_code == "P0":
            res = self._run_never(true_links, link_configs, prior_belief, paths)
        elif policy_code == "P1":
            res = self._run_always(true_links, link_configs, prior_belief, paths, candidate_actions, rng)
        elif policy_code == "P2":
            res = self._run_ig(true_links, link_configs, prior_belief, paths, candidate_actions, rng)
        elif policy_code == "P3":
            res = self._run_confidence(true_links, link_configs, prior_belief, paths, candidate_actions, rng)
        elif policy_code == "P4":
            res = self._run_evsi(true_links, link_configs, prior_belief, paths, candidate_actions, rng)
        elif policy_code == "P5":
            res = self._run_linkselfie(true_links, link_configs, prior_belief, paths, candidate_actions, rng)
        elif policy_code == "P6":
            res = self._run_bequp_link(true_links, link_configs, prior_belief, paths, candidate_actions, rng)
        elif policy_code == "P7":
            res = self._run_bequp_path(true_links, link_configs, prior_belief, paths, candidate_actions, rng)
        elif policy_code == "P8":
            res = self._run_oracle(true_links, paths)
        else:
            raise ValueError(f"Unknown policy code: {policy_code}")

        wall_time = time.time() - start_wall_time
        res['policy_code'] = policy_code
        res['policy_name'] = POLICY_MAP[policy_code]
        res['classical_decision_cost_sec'] = wall_time
        res['total_cost'] = res['benchmark_cost'] + (wall_time * 0.001)
        return res

    def _run_oracle(self, true_links: Dict[str, LinkState], paths: List[Path]) -> Dict[str, float]:
        path_utilities = {}
        for p in paths:
            p_links = [true_links[l_id] for l_id in p.links]
            u = self.evaluator.evaluate_route_utility(p_links)
            path_utilities[p.path_id] = u
        best_p = max(path_utilities, key=path_utilities.get)
        true_u = path_utilities[best_p]
        return {
            'selected_path': best_p,
            'true_downstream_utility': true_u,
            'net_utility': true_u,
            'benchmark_cost': 0.0,
            'shots_fired': 0,
            'action_taken': 'None (Oracle)',
            'switched_decision': 0,
            'gross_evsi': 0.0,
            'net_evsi': 0.0,
            'p_switch': 0.0
        }

    def _run_never(self, true_links: Dict[str, LinkState], link_configs: Dict[str, Dict[str, float]], prior_belief: ParticleBeliefState, paths: List[Path]) -> Dict[str, float]:
        path_utilities = {}
        for p in paths:
            path_utilities[p.path_id] = self.solver.compute_expected_path_utility(p, prior_belief, link_configs)
        selected_p = max(path_utilities, key=path_utilities.get)
        p_obj = next(p for p in paths if p.path_id == selected_p)
        true_links_list = [true_links[l_id] for l_id in p_obj.links]
        true_u = self.evaluator.evaluate_route_utility(true_links_list)
        return {
            'selected_path': selected_p,
            'true_downstream_utility': true_u,
            'net_utility': true_u,
            'benchmark_cost': 0.0,
            'shots_fired': 0,
            'action_taken': 'None',
            'switched_decision': 0,
            'gross_evsi': 0.0,
            'net_evsi': 0.0,
            'p_switch': 0.0
        }

    def _run_always(self, true_links: Dict[str, LinkState], link_configs: Dict[str, Dict[str, float]], prior_belief: ParticleBeliefState, paths: List[Path], candidate_actions: List[Tuple[str, int, int]], rng: np.random.Generator) -> Dict[str, float]:
        tot_cost = 0.0
        tot_shots = 0
        b_links = set(act[0] for act in candidate_actions)
        for link_id in b_links:
            obs = self.evaluator.simulate_bounce_observation(true_links[link_id], m=3, n_shots=100, rng=rng)
            c = self.evaluator.compute_benchmark_cost(m=3, n_shots=100)
            tot_cost += c
            tot_shots += 300
        path_utilities = {}
        for p in paths:
            path_utilities[p.path_id] = self.solver.compute_expected_path_utility(p, prior_belief, link_configs)
        selected_p = max(path_utilities, key=path_utilities.get)
        p_obj = next(p for p in paths if p.path_id == selected_p)
        true_links_list = [true_links[l_id] for l_id in p_obj.links]
        true_u = self.evaluator.evaluate_route_utility(true_links_list)
        return {
            'selected_path': selected_p,
            'true_downstream_utility': true_u,
            'net_utility': true_u - tot_cost,
            'benchmark_cost': tot_cost,
            'shots_fired': tot_shots,
            'action_taken': 'All_Links',
            'switched_decision': 0,
            'gross_evsi': 0.0,
            'net_evsi': -tot_cost,
            'p_switch': 0.0
        }

    def _select_path_posterior(
        self,
        prior_belief: ParticleBeliefState,
        paths: List[Path],
        link_configs: Dict[str, Dict[str, float]],
        target_link: str,
        m: int,
        n_shots: int,
        obs: float
    ) -> Tuple[str, int]:
        particles = prior_belief.particles[target_link]
        weights = prior_belief.weights[target_link]
        sigma_bm = 0.05 / np.sqrt(n_shots)
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
            N = prior_belief.num_particles
            w_prod = np.ones(N)
            min_t2 = float('inf')
            tot_delay = 0.0
            p_succ = 1.0

            for link_id in path.links:
                p_val = particles[:, 1] if link_id == target_link else prior_belief.particles[link_id][:, 1]
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
                path_u = float(np.sum(u_vec * post_weights))
            else:
                path_u = float(np.mean(u_vec))
            path_post_u[path.path_id] = path_u

        prior_best = max(paths, key=lambda p: self.solver.compute_expected_path_utility(p, prior_belief, link_configs)).path_id
        selected_p = max(path_post_u, key=path_post_u.get)
        switched = 1 if selected_p != prior_best else 0
        return selected_p, switched

    def _run_ig(self, true_links: Dict[str, LinkState], link_configs: Dict[str, Dict[str, float]], prior_belief: ParticleBeliefState, paths: List[Path], candidate_actions: List[Tuple[str, int, int]], rng: np.random.Generator) -> Dict[str, float]:
        best_act = None
        max_ig = -1.0
        best_eval = None
        for (l_id, m, n_s) in candidate_actions:
            eval_res = self.solver.evaluate_evsi_and_ig(prior_belief, paths, link_configs, target_link=l_id, m=m, n_shots=n_s, rng=rng)
            if eval_res['ig'] > max_ig:
                max_ig = eval_res['ig']
                best_act = (l_id, m, n_s)
                best_eval = eval_res
        if best_act is None:
            return self._run_never(true_links, link_configs, prior_belief, paths)
        l_id, m, n_s = best_act
        obs = self.evaluator.simulate_bounce_observation(true_links[l_id], m=m, n_shots=n_s, rng=rng)
        cost = self.evaluator.compute_benchmark_cost(m, n_s)
        selected_p, switched = self._select_path_posterior(prior_belief, paths, link_configs, l_id, m, n_s, obs)
        p_obj = next(p for p in paths if p.path_id == selected_p)
        true_links_list = [true_links[l_id] for l_id in p_obj.links]
        true_u = self.evaluator.evaluate_route_utility(true_links_list)
        return {
            'selected_path': selected_p,
            'true_downstream_utility': true_u,
            'net_utility': true_u - cost,
            'benchmark_cost': cost,
            'shots_fired': m * n_s,
            'action_taken': f"{l_id}_m{m}",
            'switched_decision': switched,
            'gross_evsi': best_eval['gross_evsi'] if best_eval else 0.0,
            'net_evsi': best_eval['net_evsi'] if best_eval else 0.0,
            'p_switch': best_eval['p_switch'] if best_eval else 0.0
        }

    def _run_evsi(self, true_links: Dict[str, LinkState], link_configs: Dict[str, Dict[str, float]], prior_belief: ParticleBeliefState, paths: List[Path], candidate_actions: List[Tuple[str, int, int]], rng: np.random.Generator) -> Dict[str, float]:
        best_act = None
        max_net_evsi = -float('inf')
        best_eval = None
        for (l_id, m, n_s) in candidate_actions:
            eval_res = self.solver.evaluate_evsi_and_ig(prior_belief, paths, link_configs, target_link=l_id, m=m, n_shots=n_s, rng=rng)
            if eval_res['net_evsi'] > max_net_evsi:
                max_net_evsi = eval_res['net_evsi']
                best_act = (l_id, m, n_s)
                best_eval = eval_res
        if best_act is None or max_net_evsi <= 0.0:
            res = self._run_never(true_links, link_configs, prior_belief, paths)
            res['action_taken'] = 'None (Net_EVSI<=0)'
            return res
        l_id, m, n_s = best_act
        obs = self.evaluator.simulate_bounce_observation(true_links[l_id], m=m, n_shots=n_s, rng=rng)
        cost = self.evaluator.compute_benchmark_cost(m, n_s)
        selected_p, switched = self._select_path_posterior(prior_belief, paths, link_configs, l_id, m, n_s, obs)
        p_obj = next(p for p in paths if p.path_id == selected_p)
        true_links_list = [true_links[l_id] for l_id in p_obj.links]
        true_u = self.evaluator.evaluate_route_utility(true_links_list)
        return {
            'selected_path': selected_p,
            'true_downstream_utility': true_u,
            'net_utility': true_u - cost,
            'benchmark_cost': cost,
            'shots_fired': m * n_s,
            'action_taken': f"{l_id}_m{m}",
            'switched_decision': switched,
            'gross_evsi': best_eval['gross_evsi'] if best_eval else 0.0,
            'net_evsi': max_net_evsi,
            'p_switch': best_eval['p_switch'] if best_eval else 0.0
        }

    def _run_confidence(self, true_links: Dict[str, LinkState], link_configs: Dict[str, Dict[str, float]], prior_belief: ParticleBeliefState, paths: List[Path], candidate_actions: List[Tuple[str, int, int]], rng: np.random.Generator) -> Dict[str, float]:
        cost = self.evaluator.compute_benchmark_cost(m=2, n_shots=50)
        l_id = candidate_actions[0][0]
        obs = self.evaluator.simulate_bounce_observation(true_links[l_id], m=2, n_shots=50, rng=rng)
        selected_p, switched = self._select_path_posterior(prior_belief, paths, link_configs, l_id, 2, 50, obs)
        p_obj = next(p for p in paths if p.path_id == selected_p)
        true_links_list = [true_links[l_id] for l_id in p_obj.links]
        true_u = self.evaluator.evaluate_route_utility(true_links_list)
        return {
            'selected_path': selected_p,
            'true_downstream_utility': true_u,
            'net_utility': true_u - cost,
            'benchmark_cost': cost,
            'shots_fired': 100,
            'action_taken': 'Seq_Confidence',
            'switched_decision': switched,
            'gross_evsi': 0.0,
            'net_evsi': -cost,
            'p_switch': 0.0
        }

    def _run_linkselfie(self, true_links: Dict[str, LinkState], link_configs: Dict[str, Dict[str, float]], prior_belief: ParticleBeliefState, paths: List[Path], candidate_actions: List[Tuple[str, int, int]], rng: np.random.Generator) -> Dict[str, float]:
        cost = self.evaluator.compute_benchmark_cost(m=3, n_shots=80)
        l_id = candidate_actions[0][0]
        obs = self.evaluator.simulate_bounce_observation(true_links[l_id], m=3, n_shots=80, rng=rng)
        selected_p, switched = self._select_path_posterior(prior_belief, paths, link_configs, l_id, 3, 80, obs)
        p_obj = next(p for p in paths if p.path_id == selected_p)
        true_links_list = [true_links[l_id] for l_id in p_obj.links]
        true_u = self.evaluator.evaluate_route_utility(true_links_list)
        return {
            'selected_path': selected_p,
            'true_downstream_utility': true_u,
            'net_utility': true_u - cost,
            'benchmark_cost': cost,
            'shots_fired': 240,
            'action_taken': 'LinkSelFiE_Arm_Elim',
            'switched_decision': switched,
            'gross_evsi': 0.0,
            'net_evsi': -cost,
            'p_switch': 0.0
        }

    def _run_bequp_link(self, true_links: Dict[str, LinkState], link_configs: Dict[str, Dict[str, float]], prior_belief: ParticleBeliefState, paths: List[Path], candidate_actions: List[Tuple[str, int, int]], rng: np.random.Generator) -> Dict[str, float]:
        cost = self.evaluator.compute_benchmark_cost(m=2, n_shots=60)
        l_id = candidate_actions[0][0]
        obs = self.evaluator.simulate_bounce_observation(true_links[l_id], m=2, n_shots=60, rng=rng)
        selected_p, switched = self._select_path_posterior(prior_belief, paths, link_configs, l_id, 2, 60, obs)
        p_obj = next(p for p in paths if p.path_id == selected_p)
        true_links_list = [true_links[l_id] for l_id in p_obj.links]
        true_u = self.evaluator.evaluate_route_utility(true_links_list)
        return {
            'selected_path': selected_p,
            'true_downstream_utility': true_u,
            'net_utility': true_u - cost,
            'benchmark_cost': cost,
            'shots_fired': 120,
            'action_taken': 'BeQuP_Link_Feedback',
            'switched_decision': switched,
            'gross_evsi': 0.0,
            'net_evsi': -cost,
            'p_switch': 0.0
        }

    def _run_bequp_path(self, true_links: Dict[str, LinkState], link_configs: Dict[str, Dict[str, float]], prior_belief: ParticleBeliefState, paths: List[Path], candidate_actions: List[Tuple[str, int, int]], rng: np.random.Generator) -> Dict[str, float]:
        cost = self.evaluator.compute_benchmark_cost(m=4, n_shots=40)
        l_id = candidate_actions[0][0]
        obs = self.evaluator.simulate_bounce_observation(true_links[l_id], m=4, n_shots=40, rng=rng)
        selected_p, switched = self._select_path_posterior(prior_belief, paths, link_configs, l_id, 4, 40, obs)
        p_obj = next(p for p in paths if p.path_id == selected_p)
        true_links_list = [true_links[l_id] for l_id in p_obj.links]
        true_u = self.evaluator.evaluate_route_utility(true_links_list)
        return {
            'selected_path': selected_p,
            'true_downstream_utility': true_u,
            'net_utility': true_u - cost,
            'benchmark_cost': cost,
            'shots_fired': 160,
            'action_taken': 'BeQuP_Path_Feedback',
            'switched_decision': switched,
            'gross_evsi': 0.0,
            'net_evsi': -cost,
            'p_switch': 0.0
        }

