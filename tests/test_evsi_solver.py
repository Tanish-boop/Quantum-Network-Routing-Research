"""
Unit tests for Particle Belief State and EVSI Solver.
"""

import unittest
import numpy as np
from src.quantum_environment import PhysicalQuantumEvaluator, Path
from src.evsi_evaluator import ParticleBeliefState, EVSISolver

class TestEVSISolver(unittest.TestCase):

    def setUp(self):
        self.evaluator = PhysicalQuantumEvaluator(c_fixed=0.001, c_bounce=0.0001)
        self.solver = EVSISolver(self.evaluator, num_predictive_samples=10)
        self.rng = np.random.default_rng(seed=42)

        self.paths = [
            Path(path_id="P1", links=["L1_1", "L1_2"], hops=2),
            Path(path_id="P2", links=["L2_1", "L2_2"], hops=2)
        ]

        self.link_configs = {
            "L1_1": {"T2": 100.0, "p_gen": 0.8, "delay": 1.0},
            "L1_2": {"T2": 100.0, "p_gen": 0.8, "delay": 1.0},
            "L2_1": {"T2": 100.0, "p_gen": 0.8, "delay": 1.0},
            "L2_2": {"T2": 100.0, "p_gen": 0.8, "delay": 1.0}
        }

    def test_particle_belief_initialization(self):
        belief = ParticleBeliefState(num_particles=25, rng=self.rng)
        belief.initialize_link_prior("L1_1", A_mean=0.9, A_std=0.05, p_mean=0.85, p_std=0.10)
        self.assertIn("L1_1", belief.particles)
        self.assertEqual(belief.particles["L1_1"].shape, (25, 2))
        self.assertEqual(len(belief.weights["L1_1"]), 25)

    def test_evsi_and_ig_evaluation(self):
        belief = ParticleBeliefState(num_particles=20, rng=self.rng)
        for l_id in ["L1_1", "L1_2", "L2_1", "L2_2"]:
            belief.initialize_link_prior(l_id, A_mean=0.9, A_std=0.05, p_mean=0.85, p_std=0.10)

        res = self.solver.evaluate_evsi_and_ig(
            belief, self.paths, self.link_configs, target_link="L1_1", m=2, n_shots=50, rng=self.rng
        )

        self.assertIn("gross_evsi", res)
        self.assertIn("net_evsi", res)
        self.assertIn("ig", res)
        self.assertIn("p_switch", res)
        self.assertGreaterEqual(res["ig"], 0.0)
        self.assertAlmostEqual(res["net_evsi"], res["gross_evsi"] - res["benchmark_cost"], places=5)

if __name__ == "__main__":
    unittest.main()
