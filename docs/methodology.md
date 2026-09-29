# Methodology: Decision-Aware Quantum Network Routing

---

## 1. Simulation Approach
We adopt a discrete-event Monte-Carlo simulation approach representing quantum networks as graphs $G = (V,E)$. Quantum nodes $V$ execute entanglement swapping and physical link benchmarking. Communication links $E$ are characterized by depolarizing parameter $p$, quantum memory lifetime $T_2$, generation probability $p_{\text{gen}}$, latency, and Werner state visibility $A$.

## 2. Decision Framework
The routing controller operates on a particle belief distribution $B = \{(A_i, p_i, w_i)\}_{i=1}^N$. Before selecting a route, the controller evaluates candidate information actions $a = (e, m, n_{\text{shots}})$. It calculates Expected Value of Sample Information ($\text{EVSI}$) by simulating predictive observation distributions $Y \sim P(Y \mid B, a)$ and calculating posterior expected utilities under Bayes' rule.

## 3. Anti-Leakage Protocol
Hidden ground-truth parameters are strictly isolated inside the physical evaluator environment. Controller decisions depend strictly on particle beliefs and noisy simulated observations $b_m = A \cdot p^{2m} + \mathcal{N}(0, \sigma)$. Ground-truth state is exposed only to the Oracle baseline and final performance evaluator.
