# Reproducibility Guide

---

## Seed Control
All Monte-Carlo simulations utilize explicit NumPy random number generators (`np.random.default_rng(seed)`).
Common random numbers are used across all policies P0–P8 within each seed to enable paired evaluations.

## Reproduction Steps

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run test suite:
   ```bash
   python -m unittest discover -s tests -p "test_*.py"
   ```
3. Execute 500-seed campaign and generate figures:
   ```bash
   python -c "from src.experiment_campaign import CampaignRunner; from src.statistical_analysis import Analyzer; runner = CampaignRunner(seeds_per_regime=500); raw_csv = runner.run_campaign(); analyzer = Analyzer(raw_csv); analyzer.analyze_all()"
   python experiments/run_cost_sweep.py
   python experiments/run_decoherence_sweep.py
   python experiments/run_information_gain_analysis.py
   python src/generate_figures.py
   ```
