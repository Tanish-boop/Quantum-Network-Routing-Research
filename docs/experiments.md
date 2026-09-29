# Experiments & Regime Matrix Guide

---

## 1. 10 Network Regimes
The paired evaluation campaign tests 9 decision policies across 10 network regimes (500 seeds/regime = 45,000 total evaluations):

1. **A_obvious_route**: Clearly separated route utilities ($A_{p1}=0.95, A_{p2}=0.50$).
2. **B_close_route**: Close competing routes ($A_{p1}=0.82, A_{p2}=0.81$).
3. **C_high_uncertainty**: High network-state uncertainty ($\sigma=0.20$).
4. **D_low_uncertainty**: Low network-state uncertainty ($\sigma=0.02$).
5. **E_short_T2**: Short quantum-memory lifetime ($T_2=5.0$ ms).
6. **F_long_T2**: Long quantum-memory lifetime ($T_2=500.0$ ms).
7. **G_low_cost**: Low benchmarking cost ($c_{\text{fixed}}=0.0001$).
8. **H_high_cost**: High benchmarking cost ($c_{\text{fixed}}=0.05$).
9. **I_route_crossing**: Route-ranking crossing regimes.
10. **J_high_ig_nuisance**: High-information nuisance measurement (falsification test case for Information Gain).

## 2. Parameter Sweeps
- **Cost Sweep (`experiments/run_cost_sweep.py`)**: Sweeps $C \in [0.0, 0.30]$.
- **Decoherence Sweep (`experiments/run_decoherence_sweep.py`)**: Sweeps $T_2 \in [1.0, 1000.0]$ ms.
- **IG vs EVSI Divergence (`experiments/run_information_gain_analysis.py`)**: Evaluates 200 random network scenarios.
