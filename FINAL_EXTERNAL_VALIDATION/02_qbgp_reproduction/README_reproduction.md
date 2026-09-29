# Experiment 1 Reproduction Report: Published QBGP Baseline

## Executive Summary
- **Repository URL**: `https://github.com/lizhuohua/quantum-bgp-online-path-selection`
- **Git Commit Hash**: `457f51b2cc8682aa811a9664c564bcaf9ab7121e`
- **Execution Status**: `FAIL — Dependency Blocked (NetSquid required)`
- **NetSquid Used**: No (NetSquid package absent in Python environment).

---

## 1. Exact Command Executed
```bash
cd qbgp_repo
python main.py
```

---

## 2. Execution Outcome
- **Exit Code**: `1`
- **Error Class**: `ModuleNotFoundError`
- **Stack Trace Summary**:
  ```text
  File "qbgp_repo\main.py", line 3, in <module>
    import plots
  File "qbgp_repo\plots\__init__.py", line 2, in <module>
    from .average_fidelity_vs_with_or_without_benchmarking_vs_l import ...
  File "qbgp_repo\plots\average_fidelity_vs_with_or_without_benchmarking_vs_l.py", line 7, in <module>
    from components import QuantumNetwork
  File "qbgp_repo\components.py", line 4, in <module>
    import netsquid as ns
  ModuleNotFoundError: No module named 'netsquid'
  ```

---

## 3. NetSquid Usage Verification
NetSquid was **not** used during execution. The Python interpreter failed at the first module import level (`import netsquid as ns` inside `components.py`).

---

## 4. Output Matching & Figures Reproduced
- **Outputs Match Paper**: N/A (execution failed prior to simulation initialization).
- **Figures Reproduced**: 0 / 12 figures.

---

## 5. Environment & Setup Requirements
- **OS**: Windows 11 (win32, x64)
- **Python Version**: `3.13.4`
- **NetworkX**: `3.5`
- **NumPy**: `2.3.2`
- **SciPy**: `1.16.1`
- **Matplotlib**: `3.11.1`
- **NetSquid Status**: Missing. NetSquid is a proprietary discrete-event quantum network simulation platform hosted on a private PyPI index (`https://pypi.netsquid.org`) requiring community forum credentials for installation.

---

## 6. Scientific Integrity & Reproduction Policy
In accordance with explicit research guidelines:
- The published QBGP source code was **NOT modified** to bypass NetSquid or mock simulator classes.
- The failure was logged exactly as encountered.
- The repository remains pristine for exact execution should NetSquid credentials be provided in future research phases.
