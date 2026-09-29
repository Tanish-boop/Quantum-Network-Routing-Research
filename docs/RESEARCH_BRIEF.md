# Research Handoff Brief: Decision-Aware Quantum Network Routing

**Subject**: Executive Research Summary  
**Focus**: Decision-Aware Link Benchmarking via Expected Value of Sample Information (EVSI) in Multi-Hop Quantum Networks

---

## 1. Research Question
In quantum networks operating under parameter uncertainty and quantum memory decoherence ($T_2$), when is it beneficial for a routing controller to acquire additional network-state information (e.g., via active bounce measurements) prior to selecting an end-to-end entanglement route?

---

## 2. Motivation & Theoretical Gap
Existing link-state benchmarking approaches frequently rely on **variance-reduction Information Gain (IG)**. However, in multi-hop networks:
$$\text{Information Gain } \neq \text{ Downstream Decision Value}$$
High parameter uncertainty on a link does not imply that measuring that link will alter the optimal routing decision. Measuring links on sub-optimal candidate paths consumes quantum channel time and accelerates memory decoherence without improving the downstream route selection.

---

## 3. Proposed EVSI Approach
We formulate a decision-theoretic framework using **Expected Value of Sample Information (EVSI)**:
$$\text{EVSI}(a) = \mathbb{E}_{y}\left[ \max_{k} \mathbb{E}_{b_{t+1}(y)} [U(P_k)] \right] - \max_{k} \mathbb{E}_{b_t} [U(P_k)]$$
$$\text{Net\_EVSI}(a) = \text{EVSI}(a) - C(a)$$

where $C(a)$ is the physical measurement acquisition cost. The controller executes a candidate benchmarking action $a$ if and only if $\text{Net\_EVSI}(a) > 0$.

---

## 4. Experimental Setup & Topology
- **Simulator**: Discrete-event quantum network simulation model (`PhysicalQuantumEvaluator` and `ParticleBeliefState`).
- **Topology**: 4-Path Multi-Hop Network:
  - $P_1$: 2-hop route ($L1\_1, L1\_2$)
  - $P_2$: 3-hop route ($L2\_1, L2\_2, L2\_3$)
  - $P_3$: 3-hop route ($L3\_1, L3\_2, L3\_3$)
  - $P_4$: 4-hop route ($L4\_1, L4\_2, L4\_3, L4\_4$)
- **Evaluated Policies**: 9 baseline and proposed policies ($P_0$: Never, $P_1$: Always, $P_2$: Info Gain, $P_3$: Confidence, $P_4$: EVSI, $P_5$: LinkSelFiE, $P_6$: BeQuP-Link, $P_7$: BeQuP-Path, $P_8$: Oracle).

---

## 5. Main Finding: IG vs. EVSI Divergence
Across tested candidate measurement actions, **15.4%** of candidate actions exhibit high Variance-Reduction IG ($\ge 75\text{th}$ percentile) but negative Net EVSI ($\text{Net\_EVSI} \le 0$). 
Executing these actions yields a **0.0% route-switch rate**, demonstrating that Information Gain triggers non-decision-critical ("nuisance") probing that EVSI correctly suppresses.

---

## 6. Decision-Boundary Results ($1,000$ Controlled Scenarios, $|U(P_1) - U(P_2)| < 0.05$)
In competitive decision-boundary scenarios where 2-hop $P_1$ ($p \approx 0.65$) and 3-hop $P_2$ ($p \approx 0.95$) have close prior expected utilities:

| Policy Code | Policy Name | Net Utility | 95% Bootstrap CI | Benchmark Cost | Route Switch Rate | Oracle Regret |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **P0** | **Never Benchmark** | 0.2155 | [0.2112, 0.2198] | 0.0000 | 0.0% | 0.0415 |
| **P2** | **Information Gain** | 0.2127 | [0.2084, 0.2170] | 0.0110 | 15.9% | 0.0443 |
| **P4** | **EVSI (Our Method)** | **0.2203** | **[0.2160, 0.2246]** | **0.0090** | **36.5%** | **0.0367** |
| **P8** | **Oracle (Upper Bound)**| 0.2570 | [0.2526, 0.2613] | 0.0000 | 0.0% | 0.0000 |

**Result**: EVSI achieves the highest observed net utility among non-oracle policies, reducing suboptimality regret relative to Oracle routing by **17.2%** over Information Gain.

---

## 7. Conditional Gating Verification
From 45,000 policy evaluations across 10 network regimes:
- $P(\text{route changes} \mid \text{Net\_EVSI} > 0) = \mathbf{30.3\%}$ ($485$ switches out of $1,599$ positive actions).
- $P(\text{route changes} \mid \text{Net\_EVSI} \le 0) = \mathbf{0.0\%}$ ($0$ switches out of $3,401$ negative actions).

---

## 8. Key Limitations & Scope
1. Results represent **preliminary simulation evidence** on a discrete-event simulator prototype.
2. Hardware testbed validation and dynamic background entanglement traffic loading remain future work.
3. Anti-leakage isolation is strictly enforced: ground-truth state is concealed from the controller and used only for evaluation.

---

## 9. Reproducibility Quick Start
```powershell
pip install -r requirements.txt
python experiments/run_canonical_experiment.py
python -m unittest discover -s tests
```

---

## 10. Current Research Status
**Status**: Preliminary simulation validation completed.  
**Repository Artifacts**: Fully reproducible canonical scripts, decision audit CSVs, and generated figure artifacts.
