# Research Limitations & Scope Boundaries

---

## 1. Executive Context
To ensure scientific credibility, this document explicitly outlines the scope boundaries, modeling assumptions, and limitations of the current Decision-Aware Quantum Network Routing simulator.

---

## 2. Modeling Limitations

### A. Discrete-Event Simulation Prototype
- The current implementation is a discrete-event simulation model (`PhysicalQuantumEvaluator`) incorporating Werner-state entanglement swapping, quantum memory decoherence ($T_2$), success probability scaling, and measurement latency.
- It is **not yet validated on physical quantum hardware testbeds** (e.g., nitrogen-vacancy center or trapped-ion hardware nodes).

### B. Static Request Arrival & Traffic Loading
- Benchmark evaluations operate under single-packet / single-route selection decision rounds.
- **Dynamic background entanglement traffic** (multiplexed request queues, competing link reservations, dynamic buffer contention) is pending future implementation.

### C. Acquisition Cost Calibration Dependence
- The net benefit of EVSI-driven active benchmarking depends on the relative calibration of measurement cost parameters ($c_{\text{fixed}}$, $c_{\text{bounce}}$) against quantum memory decay rate ($1/T_2$).
- If measurement costs are excessively high relative to route utility variance, benchmarking is rightfully suppressed ($\text{Net\_EVSI} \le 0$), collapsing performance to Never Benchmark ($P_0$).

### D. Topology Scope
- Experimental findings are established on a 4-path multi-hop topology ($P_1$: 2-hop, $P_2$: 3-hop, $P_3$: 3-hop, $P_4$: 4-hop).
- While theoretical proofs for Information Gain vs. EVSI divergence generalize to arbitrary topologies, broader empirical validation across large-scale mesh topologies remains future work.

---

## 3. Scope Boundaries & Claims

- **Preliminary Simulation Evidence**: All numerical results represent preliminary discrete-event simulation evidence.
- **No Universal Superiority Claim**: We do NOT claim universal superiority of EVSI over Never Benchmark in non-competitive regimes where one path holds overwhelming structural dominance. EVSI is superior specifically in **decision-boundary regimes** ($|U(P_1) - U(P_2)| < 0.05$) where competing routes have close prior utilities.
