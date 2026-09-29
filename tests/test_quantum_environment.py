"""
Unit tests for Quantum Environment and Physical Route Evaluator.
"""

import unittest
import numpy as np
from src.quantum_environment import PhysicalQuantumEvaluator, LinkState, Path

class TestQuantumEnvironment(unittest.TestCase):

    def setUp(self):
        self.evaluator = PhysicalQuantumEvaluator(c_fixed=0.001, c_bounce=0.0001)

    def test_link_state_properties(self):
        link = LinkState(link_id="L1", A=0.9, p=0.80, T2=100.0, p_gen=0.8, delay=1.0)
        self.assertEqual(link.fidelity, 0.90)  # (1+0.8)/2
        self.assertEqual(link.visibility, 0.80)

    def test_e2e_fidelity_decay(self):
        links = [
            LinkState(link_id="L1", A=0.9, p=0.80, T2=100.0, p_gen=0.8, delay=1.0),
            LinkState(link_id="L2", A=0.9, p=0.80, T2=50.0, p_gen=0.8, delay=1.0)
        ]
        # Without wait
        f_no_wait = self.evaluator.compute_e2e_fidelity(links, wait_time=0.0)
        self.assertAlmostEqual(f_no_wait, 0.25 + 0.75 * (0.80 * 0.80), places=4)

        # With wait time equal to min T2 (50ms)
        f_wait = self.evaluator.compute_e2e_fidelity(links, wait_time=50.0)
        expected_w = 0.64 * np.exp(-1.0)
        self.assertAlmostEqual(f_wait, 0.25 + 0.75 * expected_w, places=4)
        self.assertLess(f_wait, f_no_wait)

    def test_success_prob_and_latency(self):
        links = [
            LinkState(link_id="L1", A=0.9, p=0.80, T2=100.0, p_gen=0.8, delay=1.0),
            LinkState(link_id="L2", A=0.9, p=0.80, T2=100.0, p_gen=0.5, delay=1.0)
        ]
        p_succ = self.evaluator.compute_success_prob(links)
        self.assertAlmostEqual(p_succ, 0.40, places=4)

        latency = self.evaluator.compute_latency(links)
        # delay = 2.0, expected_wait = (1/0.40)*0.1 = 0.25 ms => total 2.25 ms
        self.assertAlmostEqual(latency, 2.25, places=4)

    def test_route_utility(self):
        links = [LinkState(link_id="L1", A=0.9, p=0.80, T2=100.0, p_gen=0.8, delay=1.0)]
        u = self.evaluator.evaluate_route_utility(links)
        self.assertIsInstance(u, float)

    def test_bounce_observation(self):
        link = LinkState(link_id="L1", A=0.9, p=0.80, T2=100.0, p_gen=0.8, delay=1.0)
        rng = np.random.default_rng(seed=42)
        obs = self.evaluator.simulate_bounce_observation(link, m=2, n_shots=100, rng=rng)
        self.assertTrue(0.0 <= obs <= 1.0)

if __name__ == "__main__":
    unittest.main()
