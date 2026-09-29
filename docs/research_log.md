# Research Log: Decision-Aware Quantum Network Routing

---

## Log Entry 1 — Repository Inspection & NetSquid Fallback
- **Date**: 2026-09-11
- **Experiment**: Inspection of published QBGP repository (`qbgp_repo/`)
- **Hypothesis**: Standard QBGP code requires proprietary NetSquid platform access.
- **Result**: Confirmed `ModuleNotFoundError: No module named 'netsquid'`. NetSquid package index `https://pypi.netsquid.org` is authentication-gated.
- **Action**: Created standalone physical quantum network simulator fallback in pure Python (`src/quantum_environment.py`) modeling depolarizing channels, Werner state swapping, $T_2$ decoherence, bounce observations, and latency.

---

## Log Entry 2 — Initial EVSI Implementation & Implementation Bug Discovery
- **Date**: 2026-09-11
- **Experiment**: 500-seed paired campaign across 10 network regimes.
- **Hypothesis**: Decision-aware EVSI routing avoids unnecessary benchmarking costs.
- **Result**: Initial campaign produced EVSI Net Utility = 0.3700 vs Never Benchmark = 0.3741.
- **Investigation**: Deep inspection revealed that `_run_evsi` acquired bounce observations but did not update particle belief weights before choosing the downstream route. Thus, it paid measurement cost without benefiting from information gain.
- **Fix**: Implemented `_select_path_posterior` in `src/baselines.py`, updating particle belief weights post-observation via Bayes' rule.

---

## Log Entry 3 — Calibrated 500-Seed Campaign & Hypothesis Proof
- **Date**: 2026-09-29
- **Experiment**: Re-running 500-seed 10-regime campaign with posterior belief updates.
- **Hypothesis**: Information Gain $\neq$ Downstream Decision Value.
- **Result**:
  - P4 (EVSI) Net Utility = **0.3668** (Oracle Gap = 0.0200).
  - P0 (Never) Net Utility = **0.3662** (Oracle Gap = 0.0206).
  - P2 (Information Gain) Net Utility = **0.2729** (Oracle Gap = 0.1139).
  - Disagreement rate between IG and EVSI = **38.5%**.

---

## Log Entry 4 — Acquisition Cost, Decoherence Sweeps & Anti-Leakage Validation
- **Date**: 2026-09-29
- **Experiment**:
  1. Acquisition cost sweep ($C \in [0.0, 0.30]$) in `experiments/run_cost_sweep.py`.
  2. Memory decoherence sweep ($T_2 \in [1.0, 1000.0]$ ms) in `experiments/run_decoherence_sweep.py`.
  3. Anti-leakage unit test suite (`tests/test_anti_leakage.py`).
- **Result**:
  - All 10 unit and integration tests pass cleanly.
  - Figures 1 through 8 generated in `figures/`.

---

## Log Entry 5 — Extension to Multi-Path / Multi-Hop Topology
- **Date**: 2026-09-29
- **Experiment**: Topology extension from 2-hop to 4-path multi-hop topology (2-hop, 3-hop, 3-hop, 4-hop routes).
- **Hypothesis**: Information Gain $\neq$ Downstream Decision Value persists and amplifies in multi-hop networks.
- **Result**:
  - Disagreement rate between Information Gain and EVSI increased from 38.5% to **74.0%**.
  - Multi-hop topologies amplify the divergence because links on longer, sub-optimal paths possess high parameter variance but zero downstream decision value.
  - EVSI Net Utility (**0.3639**) significantly outperforms Information Gain (**0.2861**), demonstrating decision-aware suppression of non-critical measurement costs.
