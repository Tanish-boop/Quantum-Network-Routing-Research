# Mathematical Model: Quantum State & EVSI Formulation

---

## 1. Physical Quantum Channel & Fidelity Model
We model link noise as depolarizing channels. For a state $\rho$ with depolarizing parameter $p \in (0, 1]$:

$$\mathcal{E}(\rho) = p \rho + (1 - p) \frac{I}{2}$$

For elementary link fidelity $F = \frac{1+p}{2}$. End-to-end Werner state swapping fidelity across path $P$ with latency $\Delta t$ and memory lifetime $T_2$:

$$F_{\text{e2e}}(P, \Delta t) = 0.25 + 0.75 \cdot \left(\prod_{e \in P} p_e\right) \cdot \exp\left(-\frac{\Delta t}{\min_{e \in P} T_{2,e}}\right)$$

## 2. Dynamic Bounce Measurement Model
Physical benchmarking conducts $m$ link bounces with $n_{\text{shots}}$ trials. The observed visibility signal $b_m$ follows:

$$b_m = A \cdot p^{2m} + \mathcal{N}\left(0, \frac{\sigma_{bm}}{\sqrt{n_{\text{shots}}}}\right)$$

Benchmarking cost is parameterized as:

$$C(a) = c_{\text{fixed}} + c_{\text{bounce}} \cdot m \cdot n_{\text{shots}}$$

## 3. EVSI and Net Decision Value
Expected Value of Sample Information:

$$\text{EVSI}(a) = \mathbb{E}_{Y \sim P(Y \mid B, a)} \left[ \max_P \mathbb{E}_{X \mid B, Y, a} [ U(P, X) ] \right] - \max_P \mathbb{E}_{X \mid B} [ U(P, X) ]$$

Information acquisition criterion:

$$\text{Net\_EVSI}(a) = \text{EVSI}(a) - C(a) > 0$$
