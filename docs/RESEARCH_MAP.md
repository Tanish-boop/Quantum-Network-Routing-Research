# Research Repository Map & Component Directory

---

## 1. Research Workflow Architecture

```
Research Question
  └─► docs/RESEARCH_BRIEF.md
  
Mathematical Model (Fidelity, Latency, Decoherence, EVSI)
  └─► docs/mathematical_model.md
  
Physical Quantum Environment & Link State Simulator
  └─► src/quantum_environment.py
  
Particle Filter & Vectorized EVSI Solver
  └─► src/evsi_evaluator.py
  
Policy Harness (P0 - P8 Baselines)
  └─► src/baselines.py
  
Information Isolation & Anti-Leakage Audit
  └─► tests/test_anti_leakage.py
  
Canonical Experiment Runner (10 Regimes + 1,000 Boundary Scenarios)
  └─► experiments/run_canonical_experiment.py
  
Statistical Analysis Engine
  └─► src/statistical_analysis.py
  
Figure Generation Pipeline
  └─► src/generate_figures.py
  
Canonical Experimental Results & Audit
  ├─► docs/CANONICAL_FINAL_RESULTS.md
  ├─► results/final_canonical_summary.json
  ├─► results/final_canonical_campaign.csv
  └─► results/final_canonical_decision_audit.csv
  
Limitations & Future Scope Boundaries
  └─► docs/limitations.md
```

---

## 2. Directory & Source File Mapping

| Research Component | Source Code / Document File | Description |
| :--- | :--- | :--- |
| **Research Question & Brief** | [docs/RESEARCH_BRIEF.md](file:///c:/Users/hp/OneDrive/Desktop/Quantum%20Computing%20Reaserch/docs/RESEARCH_BRIEF.md) | Executive 2-page research handoff brief. |
| **Canonical Results Summary** | [docs/CANONICAL_FINAL_RESULTS.md](file:///c:/Users/hp/OneDrive/Desktop/Quantum%20Computing%20Reaserch/docs/CANONICAL_FINAL_RESULTS.md) | Canonical results, reconciliation, CIs, and claims. |
| **Methodology** | [docs/methodology.md](file:///c:/Users/hp/OneDrive/Desktop/Quantum%20Computing%20Reaserch/docs/methodology.md) | Experimental methodology and campaign design. |
| **Mathematical Formulation** | [docs/mathematical_model.md](file:///c:/Users/hp/OneDrive/Desktop/Quantum%20Computing%20Reaserch/docs/mathematical_model.md) | Complete LaTeX mathematical derivations. |
| **Experiment Specifications** | [docs/experiments.md](file:///c:/Users/hp/OneDrive/Desktop/Quantum%20Computing%20Reaserch/docs/experiments.md) | Detailed regime parameter configurations. |
| **Reproducibility Guide** | [docs/reproducibility.md](file:///c:/Users/hp/OneDrive/Desktop/Quantum%20Computing%20Reaserch/docs/reproducibility.md) | Step-by-step reproduction instructions. |
| **Research Limitations** | [docs/limitations.md](file:///c:/Users/hp/OneDrive/Desktop/Quantum%20Computing%20Reaserch/docs/limitations.md) | Modeling boundaries and scope limitations. |
| **Physical Quantum Simulator** | [src/quantum_environment.py](file:///c:/Users/hp/OneDrive/Desktop/Quantum%20Computing%20Reaserch/src/quantum_environment.py) | Discrete-event quantum link and route utility model. |
| **EVSI & Particle Solver** | [src/evsi_evaluator.py](file:///c:/Users/hp/OneDrive/Desktop/Quantum%20Computing%20Reaserch/src/evsi_evaluator.py) | Vectorized particle belief state and EVSI solver. |
| **Policy Harness** | [src/baselines.py](file:///c:/Users/hp/OneDrive/Desktop/Quantum%20Computing%20Reaserch/src/baselines.py) | Harness for policies P0 through P8. |
| **Statistical Engine** | [src/statistical_analysis.py](file:///c:/Users/hp/OneDrive/Desktop/Quantum%20Computing%20Reaserch/src/statistical_analysis.py) | Bootstrap CI and Cohen's d statistical functions. |
| **Figure Generator** | [src/generate_figures.py](file:///c:/Users/hp/OneDrive/Desktop/Quantum%20Computing%20Reaserch/src/generate_figures.py) | Automated matplotlib figure creation. |
| **Canonical Script** | [experiments/run_canonical_experiment.py](file:///c:/Users/hp/OneDrive/Desktop/Quantum%20Computing%20Reaserch/experiments/run_canonical_experiment.py) | Unified deterministic canonical experiment runner. |
| **Unit Test Suite** | [tests/](file:///c:/Users/hp/OneDrive/Desktop/Quantum%20Computing%20Reaserch/tests/) | 10 unit tests covering physical model, EVSI, and anti-leakage. |
