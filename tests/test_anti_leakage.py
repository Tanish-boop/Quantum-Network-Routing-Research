"""
Anti-Leakage Validation Unit & Integration Tests

Verifies that the routing controller and EVSI solver strictly operate on
available particle belief states and noisy observations, without inspecting
hidden ground-truth LinkState values during decision making.
"""

import unittest
import numpy as np
from src.quantum_environment import PhysicalQuantumEvaluator, LinkState, Path
from src.evsi_evaluator import ParticleBeliefState, EVSISolver
from src.baselines import BaselinePoliciesHarness

class TestAntiLeakage(unittest.TestCase):

    def setUp(self):
        self.evaluator = PhysicalQuantumEvaluator(c_fixed=0.001, c_bounce=0.0001)
        self.solver = EVSISolver(self.evaluator, num_predictive_samples=10)
        self.harness = BaselinePoliciesHarness(self.evaluator, self.solver)

        self.paths = [
            Path(path_id="P1", links=["L1_1", "L1_2"], hops=2),
            Path(path_id="P2", links=["L2_1", "L2_2", "L2_3"], hops=3),
            Path(path_id="P3", links=["L3_1", "L3_2", "L3_3"], hops=3),
            Path(path_id="P4", links=["L4_1", "L4_2", "L4_3", "L4_4"], hops=4)
        ]

        self.link_configs = {
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

        self.candidate_actions = [
            ("L1_1", 2, 50),
            ("L2_1", 2, 50),
            ("L3_1", 2, 50),
            ("L4_1", 2, 50)
        ]

    def test_evsi_solver_has_no_access_to_ground_truth(self):
        """
        Verifies that EVSISolver.evaluate_evsi_and_ig functions without receiving
        or accessing ground-truth LinkState objects.
        """
        rng = np.random.default_rng(seed=123)
        belief = ParticleBeliefState(num_particles=20, rng=rng)
        for l_id in ["L1_1", "L1_2"]:
            belief.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=0.85, p_std=0.10)
        for l_id in ["L2_1", "L2_2", "L2_3"]:
            belief.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=0.80, p_std=0.10)
        for l_id in ["L3_1", "L3_2", "L3_3"]:
            belief.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=0.76, p_std=0.10)
        for l_id in ["L4_1", "L4_2", "L4_3", "L4_4"]:
            belief.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=0.72, p_std=0.10)

        # Evaluate EVSI - passed ONLY belief, paths, link_configs (no ground truth object passed)
        res = self.solver.evaluate_evsi_and_ig(
            belief, self.paths, self.link_configs, target_link="L1_1", m=2, n_shots=50, rng=rng
        )

        self.assertIn('gross_evsi', res)
        self.assertIn('net_evsi', res)
        self.assertIn('ig', res)

    def test_decision_policy_invariance_to_hidden_ground_truth(self):
        """
        Verifies that given the EXACT SAME prior belief, modifying the hidden ground-truth
        state DOES NOT change the controller's acquisition decision or predicted EVSI.
        """
        rng1 = np.random.default_rng(seed=999)
        rng2 = np.random.default_rng(seed=999)

        # Identical Beliefs
        belief1 = ParticleBeliefState(num_particles=20, rng=rng1)
        belief2 = ParticleBeliefState(num_particles=20, rng=rng2)
        for l_id in ["L1_1", "L1_2"]:
            belief1.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=0.85, p_std=0.10)
            belief2.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=0.85, p_std=0.10)
        for l_id in ["L2_1", "L2_2", "L2_3"]:
            belief1.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=0.80, p_std=0.10)
            belief2.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=0.80, p_std=0.10)
        for l_id in ["L3_1", "L3_2", "L3_3"]:
            belief1.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=0.76, p_std=0.10)
            belief2.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=0.76, p_std=0.10)
        for l_id in ["L4_1", "L4_2", "L4_3", "L4_4"]:
            belief1.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=0.72, p_std=0.10)
            belief2.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=0.72, p_std=0.10)

        # Two completely DIFFERENT hidden ground-truth states
        ground_truth_A = {
            "L1_1": LinkState(link_id="L1_1", A=0.9, p=0.95, T2=100.0, p_gen=0.8, delay=1.0),
            "L1_2": LinkState(link_id="L1_2", A=0.9, p=0.95, T2=100.0, p_gen=0.8, delay=1.0),
            "L2_1": LinkState(link_id="L2_1", A=0.9, p=0.40, T2=100.0, p_gen=0.8, delay=1.0),
            "L2_2": LinkState(link_id="L2_2", A=0.9, p=0.40, T2=100.0, p_gen=0.8, delay=1.0),
            "L2_3": LinkState(link_id="L2_3", A=0.9, p=0.40, T2=100.0, p_gen=0.8, delay=1.0),
            "L3_1": LinkState(link_id="L3_1", A=0.9, p=0.40, T2=100.0, p_gen=0.8, delay=1.0),
            "L3_2": LinkState(link_id="L3_2", A=0.9, p=0.40, T2=100.0, p_gen=0.8, delay=1.0),
            "L3_3": LinkState(link_id="L3_3", A=0.9, p=0.40, T2=100.0, p_gen=0.8, delay=1.0),
            "L4_1": LinkState(link_id="L4_1", A=0.9, p=0.40, T2=100.0, p_gen=0.8, delay=1.0),
            "L4_2": LinkState(link_id="L4_2", A=0.9, p=0.40, T2=100.0, p_gen=0.8, delay=1.0),
            "L4_3": LinkState(link_id="L4_3", A=0.9, p=0.40, T2=100.0, p_gen=0.8, delay=1.0),
            "L4_4": LinkState(link_id="L4_4", A=0.9, p=0.40, T2=100.0, p_gen=0.8, delay=1.0)
        }

        ground_truth_B = {
            "L1_1": LinkState(link_id="L1_1", A=0.9, p=0.30, T2=100.0, p_gen=0.8, delay=1.0),
            "L1_2": LinkState(link_id="L1_2", A=0.9, p=0.30, T2=100.0, p_gen=0.8, delay=1.0),
            "L2_1": LinkState(link_id="L2_1", A=0.9, p=0.99, T2=100.0, p_gen=0.8, delay=1.0),
            "L2_2": LinkState(link_id="L2_2", A=0.9, p=0.99, T2=100.0, p_gen=0.8, delay=1.0),
            "L2_3": LinkState(link_id="L2_3", A=0.9, p=0.99, T2=100.0, p_gen=0.8, delay=1.0),
            "L3_1": LinkState(link_id="L3_1", A=0.9, p=0.99, T2=100.0, p_gen=0.8, delay=1.0),
            "L3_2": LinkState(link_id="L3_2", A=0.9, p=0.99, T2=100.0, p_gen=0.8, delay=1.0),
            "L3_3": LinkState(link_id="L3_3", A=0.9, p=0.99, T2=100.0, p_gen=0.8, delay=1.0),
            "L4_1": LinkState(link_id="L4_1", A=0.9, p=0.99, T2=100.0, p_gen=0.8, delay=1.0),
            "L4_2": LinkState(link_id="L4_2", A=0.9, p=0.99, T2=100.0, p_gen=0.8, delay=1.0),
            "L4_3": LinkState(link_id="L4_3", A=0.9, p=0.99, T2=100.0, p_gen=0.8, delay=1.0),
            "L4_4": LinkState(link_id="L4_4", A=0.9, p=0.99, T2=100.0, p_gen=0.8, delay=1.0)
        }

        # Run P4 (EVSI policy) on both
        res_A = self.harness.run_policy("P4", ground_truth_A, self.link_configs, belief1, self.paths, self.candidate_actions, np.random.default_rng(777))
        res_B = self.harness.run_policy("P4", ground_truth_B, self.link_configs, belief2, self.paths, self.candidate_actions, np.random.default_rng(777))

        # Net EVSI evaluated BEFORE observation must be IDENTICAL because ground truth is hidden
        self.assertAlmostEqual(res_A['net_evsi'], res_B['net_evsi'], places=5)
        self.assertEqual(res_A['gross_evsi'], res_B['gross_evsi'])

    def test_end_to_end_causal_flow_integration(self):
        """
        Integration test verifying causal order:
        Ground Truth -> Observation -> Belief Update -> Route Selection -> Outcome Evaluation.
        """
        rng = np.random.default_rng(seed=42)
        true_state = {
            "L1_1": LinkState(link_id="L1_1", A=0.9, p=0.70, T2=100.0, p_gen=0.8, delay=1.0),
            "L1_2": LinkState(link_id="L1_2", A=0.9, p=0.70, T2=100.0, p_gen=0.8, delay=1.0),
            "L2_1": LinkState(link_id="L2_1", A=0.9, p=0.85, T2=100.0, p_gen=0.8, delay=1.0),
            "L2_2": LinkState(link_id="L2_2", A=0.9, p=0.85, T2=100.0, p_gen=0.8, delay=1.0),
            "L2_3": LinkState(link_id="L2_3", A=0.9, p=0.85, T2=100.0, p_gen=0.8, delay=1.0),
            "L3_1": LinkState(link_id="L3_1", A=0.9, p=0.80, T2=100.0, p_gen=0.8, delay=1.0),
            "L3_2": LinkState(link_id="L3_2", A=0.9, p=0.80, T2=100.0, p_gen=0.8, delay=1.0),
            "L3_3": LinkState(link_id="L3_3", A=0.9, p=0.80, T2=100.0, p_gen=0.8, delay=1.0),
            "L4_1": LinkState(link_id="L4_1", A=0.9, p=0.75, T2=100.0, p_gen=0.8, delay=1.0),
            "L4_2": LinkState(link_id="L4_2", A=0.9, p=0.75, T2=100.0, p_gen=0.8, delay=1.0),
            "L4_3": LinkState(link_id="L4_3", A=0.9, p=0.75, T2=100.0, p_gen=0.8, delay=1.0),
            "L4_4": LinkState(link_id="L4_4", A=0.9, p=0.75, T2=100.0, p_gen=0.8, delay=1.0)
        }

        belief = ParticleBeliefState(num_particles=20, rng=rng)
        for l_id in ["L1_1", "L1_2"]:
            belief.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=0.85, p_std=0.10)
        for l_id in ["L2_1", "L2_2", "L2_3"]:
            belief.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=0.70, p_std=0.10)
        for l_id in ["L3_1", "L3_2", "L3_3"]:
            belief.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=0.75, p_std=0.10)
        for l_id in ["L4_1", "L4_2", "L4_3", "L4_4"]:
            belief.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=0.75, p_std=0.10)

        res = self.harness.run_policy("P4", true_state, self.link_configs, belief, self.paths, self.candidate_actions, rng)

        self.assertIn('selected_path', res)
        self.assertIn('true_downstream_utility', res)
        self.assertIn('net_utility', res)

if __name__ == "__main__":
    unittest.main()
