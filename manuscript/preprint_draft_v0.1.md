# Ghost Sensitivity Peaks in Adaptive Phase-Coupled Systems: A Disguised Adler Bifurcation and a Calibration Rule for Coupling Floors

**Mihai Roșca**¹
¹ Independent researcher, Brăila, Romania · ORCID: [0009-0001-1422-6209](https://orcid.org/0009-0001-1422-6209)

**Draft v0.1 — 8 July 2026 — target: arXiv nlin.AO (cross-list cs.LG)**

---

## Abstract

We study a Kuramoto system of N internal oscillators coupled to an external reference ("human intent") through a noisy estimate and an adaptive coupling weight β governed by a coherence index (RSI). During calibration of a coupling floor β_min — introduced to prevent the adaptive loop from self-isolating at high internal coherence — the system's measured sensitivity to genuine reference changes exhibited an unexpected non-monotonic peak at β_min ≈ 0.15, reproduced across seven noise levels. Two intuitive explanations (forced harmonic resonance; critical damping of the feedback loop) were tested directly and rejected, one after identifying a fabricated data column in an externally proposed analysis. The true mechanism is a saddle-node-on-invariant-circle (SNIC) phase-locking bifurcation of Adler type in the mean-field reduction: near the locking threshold K_eff = Δω, critical slowing down makes fixed-window transient measurements register their deepest dips, producing a *ghost peak* that tracks the observation protocol rather than any resonance of the dynamics. The scaling law τ_relax = (K_eff² − Δω²)^(−1/2) is confirmed on the isolated Adler equation (measured exponent −0.4957 and −0.5009 in two independent implementations) and on the full 30-oscillator system (measured-to-predicted ratios 0.985–0.999). All quantitative claims were reproduced by an independent reimplementation with different seeds, RNG, and integration scheme. We derive a calibration rule for coupling floors, β_min ≥ m·Δω_max/K_ext with m(τ_target) = √(1 + (Δω_max·τ_target)^(−2)), and discuss a general methodological warning: benchmarks of adaptive alignment mechanisms that use fixed observation windows can manufacture spurious optima near bifurcations.

---

## 1. Introduction

Adaptive coupling schemes — systems that adjust how strongly they follow an external reference based on their own estimate of coherence — arise in AI alignment proposals [7], robot swarms, and power-grid control. A recurring design element is a *coupling floor*: a minimum weight below which the follow-the-reference term is never allowed to fall, guarding against a failure mode in which a self-confident system stops listening precisely because it is coherent.

This paper documents a case study in calibrating such a floor. The phenomenon that motivated it looked, at first, like a discovery: sensitivity to genuine reference changes peaked at an intermediate floor value instead of increasing monotonically, consistently across noise levels. We show that the peak is not a resonance, not a critical-damping effect, and not a property of the adaptive rule at all. It is the shadow of a textbook SNIC bifurcation [1, 4, 5] cast onto a fixed observation window by critical slowing down — a *ghost peak*.

Contributions:

1. **Mechanism identification.** The mean-field reduction of an adaptively coupled Kuramoto system with a coupling floor is an Adler equation; the empirical sensitivity peak is explained completely by critical slowing down near its locking threshold (Section 4).
2. **Quantitative verification at two levels.** The τ ~ (K_eff − Δω)^(−1/2) divergence is confirmed on the isolated Adler equation and on the full system, with ratios 0.985–0.999 (Fig. 3), including an independent reimplementation with different seeds and integrator.
3. **A calibration rule with a derived margin.** β_min ≥ m·Δω_max/K_ext, where the safety margin m follows from a recovery-time requirement: m(τ_target) = √(1 + (Δω_max τ_target)^(−2)) (Section 4.5).
4. **A methodological warning.** Fixed-window sensitivity benchmarks near bifurcations produce spurious optima. Two plausible-sounding alternative explanations failed direct testing; one arrived with an algebraically derived (not measured) data column, which the verification protocol caught (Section 4.2).

We are explicit about what this work is not: it is a nonlinear-dynamics case study on a small model (N = 30) motivated by AI-alignment questions, not evidence about production-scale alignment methods (Section 6).

## 2. Model

N internal phase oscillators θ_i with natural frequencies ω_i couple internally (Kuramoto) and to an estimate of an external reference phase θ_h:

dθ_i/dt = ω_i + α·(K_int/N)·Σ_j sin(θ_j − θ_i) + β·K_ext·sin(θ̂_h − θ_i)    (1)

The reference is observed only through noisy proxies z(t) = θ_h(t) + ξ(t), ξ ~ N(0, σ²), filtered by a constant-velocity Kalman filter to produce θ̂_h. Coherence is monitored by

Φ_int = |⟨e^{iθ_j}⟩|,  Φ_ext = (1 + cos(θ̄ − θ̂_h))/2,  Φ = α·Φ_int + β·Φ_ext    (2)

where θ̄ = arg⟨e^{iθ_j}⟩. (An earlier draft of the framework used Φ_ext = |e^{i(θ̄−θ̂_h)}|, which is identically 1; the degeneracy was found by running the simulation, not by inspection.) The Resonance Stability Index RSI is a 50-step moving average of Φ, and the adaptive weights are

β = max(1 − RSI, β_min),  α = 1 − β.    (3)

Equation (3) implements the design intent "open toward the reference when unstable"; β_min is the coupling floor whose calibration this paper concerns. Figure 1 shows the architecture.

**Mean-field reduction.** When the internal population is strongly synchronized (Φ_int ≈ 1), the group behaves as one effective oscillator, and the phase difference ψ = θ̄ − θ_h obeys the Adler equation [1]

dψ/dt = −Δω − K_eff·sin(ψ),  K_eff = β·K_ext,    (4)

with Δω the internal–reference frequency mismatch. For K_eff > |Δω| there is a stable lock ψ* = −arcsin(Δω/K_eff) with relaxation time

τ_relax = (K_eff² − Δω²)^(−1/2);    (5)

for K_eff < |Δω| the phase slips with period T_slip = 2π·(Δω² − K_eff²)^(−1/2). Both diverge at K_eff = Δω — a SNIC bifurcation with critical slowing down [4, 5] (Fig. 2).

## 3. Methods

**Simulation protocol (calibration experiment).** N = 30, ω_i ~ N(1.0, 0.05), dt = 0.02, T = 3000 steps, K_int = 1.2, K_ext = 1.5, Euler integration. The reference frequency ω_h switches 1.0 → 1.3 at t = 15 (Δω₁ = 0.3) and 1.3 → 0.9 at t = 35 (Δω₂ = 0.4). Kalman: Q = diag(10⁻⁴, 10⁻³), R = max(σ², 10⁻⁴). Grid: β_min ∈ {0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30} × σ ∈ {0.1, 0.25, 0.5, 1.0, 1.5, 2.0, 2.5}, seeds {1, 2, 3}.

**Sensitivity metric (formal definition).** With switch times t₁, t₂ and a fixed window T_w = 250 steps (5 s):

S(β_min, σ) = ½ · Σ_{k=1,2} [ 1 − min_{t ∈ [t_k, t_k+T_w]} Φ_ext(t) ].    (6)

S is a *transient* quantity by construction; steady-state Φ_ext returns to ≈ 0.99 in all locked regimes. **Jitter** is the standard deviation of dθ̄/dt over a pre-switch stationary segment (steps 100–700), quantifying noise transmission to the group phase.

**Scaling measurements.** τ_relax is measured (i) on Eq. (4) directly (RK4, dt = 10⁻³), from the asymptotic slope of ln|ψ − ψ*|, for K_eff/Δω − 1 ∈ [10⁻³, 10⁻¹]; and (ii) on the full system (RK4, dt = 5·10⁻³, fixed β, spread σ_ω = 0.01) by applying a 0.2 rad phase kick to the reference after settling and fitting the exponential return of ψ. Two measurement bugs found and fixed during this step are documented in Appendix A (phase-wrapping of ψ; sign convention of Δω) — before the fixes, the full-system check appeared to fail by a factor 4–14.

**Independent reproduction.** All headline numbers were re-derived by a second implementation written without access to the original code (vectorized mean-field formulation instead of pairwise sums, independently written Kalman filter, `numpy.random.default_rng` instead of legacy seeding, seeds {10, 11, 12}). Where the two implementations disagree is stated explicitly in Results.

## 4. Results

### 4.1 The phenomenon: a non-monotonic sensitivity peak

S(β_min) rises from ≈ 0.29 at β_min = 0 to a maximum of 0.57–0.68 at β_min = 0.15, then falls to ≈ 0.12–0.36 by β_min = 0.30, consistently across all seven noise levels and in both implementations (Fig. 4). Naively, more guaranteed coupling should mean more sensitivity; the peak demands a mechanism.

### 4.2 Two plausible explanations, tested and rejected

**Forced harmonic resonance.** Hypothesis: the RSI averaging window (50 steps) resonates with the switching cadence. Test: periodic forcing at four periods (10–80 steps). Result: response amplitude decreases monotonically with β_min at every period — no peak. Rejected.

**Critical damping of the RSI–β loop.** Hypothesis: the peak marks a critically damped regime of the feedback loop. The supporting table supplied with this hypothesis contained a "steady-state response" column that direct measurement exposed as algebraically derived from the transient column (≈ 1 − transient) rather than measured: actual steady-state Φ_ext is ≈ 0.99 for *all* β_min. Rejected; the episode is retained here as part of the verification record.

### 4.3 The mechanism: a disguised Adler bifurcation

The two switching events have thresholds β_thr,1 = Δω₁/K_ext = 0.20 and β_thr,2 = Δω₂/K_ext ≈ 0.267 (Eq. 4). Below both thresholds the system slips persistently; far above both it relocks so fast that a 5 s window barely registers a dip. Near threshold, critical slowing down (Eq. 5) makes transients longer than the window — which therefore records its deepest minima *near but not at* threshold. The measured peak (β_min ≈ 0.12–0.15, just below β_thr,1, with the RSI–β loop supplying transient coupling above the floor) is the fixed window's shadow of the bifurcation, not a property of the adaptive rule. The peak location is protocol-dependent by construction — hence *ghost peak*.

### 4.4 Quantitative verification

- **Locking threshold (full system):** persistent slipping below, definitive locking above; empirical transition at β_min ≈ 0.20–0.25 vs analytic 0.20, the offset explained by the RSI–β loop raising β above the floor when coherence drops.
- **Scaling exponent (isolated Adler):** −0.5009 (original) and −0.4957 (independent reimplementation) vs −0.5 analytic; T_slip measured/predicted = 1.0000 across K/Δω ∈ {0.5, 0.8, 0.95, 0.99}.
- **Transfer to the full system (N = 30):** measured/predicted τ ratios 0.9847–0.9965 (original, ω-spread larger) and 0.9968–0.9990 (reimplementation, σ_ω = 0.01) across β ∈ {0.35, 0.4, 0.5, 0.7, 1.0} (Fig. 3). The residual deviation shrinks with the internal frequency spread, consistent with the mean-field idealization.
- **Ghost peak reproduction:** the β_min = 0.15 peak reproduces at all seven noise levels under the independent reimplementation (peak S = 0.55–0.67 vs neighbors 0.25–0.43), with different seeds and RNG (Fig. 4).

### 4.5 Calibration rule with a derived margin

Requiring the locked system to recover within a target time, τ_relax ≤ τ_target, and writing K_eff = m·Δω_max, Eq. (5) gives

m(τ_target) = √(1 + (Δω_max·τ_target)^(−2)),  equivalently  τ_relax ≤ [Δω_max·√(m²−1)]^(−1).    (7)

The rule β_min ≥ m·Δω_max/K_ext with m = 1.5 therefore guarantees τ_relax ≤ 0.894/Δω_max — recovery within one characteristic mismatch time. Numerical check on Eq. (4): guaranteed vs measured τ agree to 0.996–0.999 for m ∈ {1.2, 1.5, 2, 3}. This replaces both the naive "β_min that scored best on the grid" (0.15 — inside the critical-slowing region, hence fragile) and any fixed universal constant: the floor must be set from the anticipated frequency mismatch and the required recovery time, quantities an implementer can estimate.

## 5. Discussion

**For benchmark design.** Any evaluation of an adaptive coupling/alignment mechanism that (i) measures transient responses (ii) in fixed windows (iii) while sweeping a parameter that moves the system across a locking threshold will manufacture an interior optimum. The optimum tracks the observation protocol — window length, event magnitudes Δω_k — not the mechanism. This is the transient counterpart of using critical slowing down as an early-warning signal [6]: the same divergence that provides warning signals also corrupts fixed-window benchmarks.

**For adaptive alignment schemes.** The episode illustrates a structural risk in coherence-gated coupling (Eq. 3): the regime in which the system most needs external correction (large Δω) is exactly where slow relaxation makes corrections hardest to observe. Recovery time after a large perturbation deserves treatment as a first-class metric, separate from steady-state alignment quality.

**On the verification record.** Two attractive explanations failed direct tests; one external contribution contained fabricated data; two bugs in our own verification code initially masqueraded as a 4–14× violation of the mean-field prediction. We retain these in Appendix A because the paper's reliability claim rests on the process, not on the elegance of the final formula.

## 6. Limitations

- Results characterize a small phase-oscillator model (N = 30) with synthetic reference signals. No claim is made about neural-network training dynamics or production alignment methods (RLHF/DPO); the connection is motivational, not demonstrated.
- The proxies-to-phase pipeline (Kalman with fixed R) is idealized; whether real human-interaction signals admit a useful phase representation is an open problem and the framework's main unvalidated assumption.
- The ghost-peak location depends on protocol parameters (T_w, Δω_k); we characterize the mechanism, not a universal constant.
- Euler integration with dt = 0.02 for the calibration experiment (RK4 for scaling measurements); the peak's robustness to integrator choice is confirmed only indirectly through the independent reimplementation.

## 7. Reproducibility and code availability

Two independent implementations produce all headline numbers: the original (pairwise-sum Kuramoto, legacy seeding, seeds 1–3) and a reimplementation written from the equations alone (vectorized mean field, independent Kalman, seeds 10–12). Scripts, exact parameters, and both raw outputs accompany this manuscript: code repository https://github.com/amidigiart/p6-adler-ghost-peak, archived at https://doi.org/10.5281/zenodo.21269201. The original calibration script reproduces its archived output bit-for-bit under Python 3.14 / NumPy 2.5.

## AI-assisted research disclosure

The research was conducted by the author in iterative sessions with multiple AI systems used as drafting, critique, and verification instruments, with executed code as the arbiter for every quantitative claim. Two AI-proposed explanations were rejected by direct testing, and one AI-supplied table was identified as containing fabricated values (Section 4.2). The independent reimplementation and cross-validation were performed by an AI system (Claude, Anthropic) in a separate session without access to the original code. All results were verified by execution on the author's hardware.

## References

[1] R. Adler, "A study of locking phenomena in oscillators," *Proc. IRE* **34**, 351–357 (1946).
[2] Y. Kuramoto, *Chemical Oscillations, Waves, and Turbulence* (Springer, 1984).
[3] S. H. Strogatz, "From Kuramoto to Crawford: exploring the onset of synchronization in populations of coupled oscillators," *Physica D* **143**, 1–20 (2000).
[4] S. H. Strogatz, *Nonlinear Dynamics and Chaos* (Addison-Wesley, 1994), Ch. 4.
[5] G. B. Ermentrout and N. Kopell, "Parabolic bursting in an excitable system coupled with a slow oscillation," *SIAM J. Appl. Math.* **46**, 233–253 (1986).
[6] M. Scheffer et al., "Early-warning signals for critical transitions," *Nature* **461**, 53–59 (2009).
[7] T. Miyato et al., "Artificial Kuramoto Oscillatory Neurons," *ICLR* (2025).
[8] A. Pikovsky, M. Rosenblum, and J. Kurths, *Synchronization: A Universal Concept in Nonlinear Sciences* (Cambridge Univ. Press, 2001).

## Figure captions

**Figure 1** (fig1_system): Architecture. N internal Kuramoto oscillators; an external reference observed through noisy proxies and a Kalman filter; adaptive weights α, β from the RSI loop with floor β_min.

**Figure 2** (fig2_bifurcation): Adler locking diagram. Stable lock ψ* = −arcsin(Δω/K_eff) (solid) and unstable branch (dashed) merge in a SNIC bifurcation at K_eff = Δω; no fixed point exists in the shaded slipping region.

**Figure 3** (fig3_scaling): Critical slowing down. Relaxation time vs distance from threshold, log-log: isolated Adler equation (circles), full N = 30 system (squares), analytic curve (line), −1/2 slope guide (dotted). Both systems collapse onto Eq. (5).

**Figure 4** (fig4_ghost_peak): The ghost peak. Transient sensitivity (Eq. 6) vs β_min at σ = 0.25: original implementation (seeds 1–3) and independent reimplementation (seeds 10–12, error bars = ±1 std over seeds). Dashed lines: Adler thresholds of the two switching events. The peak sits below threshold, in the critical-slowing region — its location tracks the measurement protocol, not a resonance.

## Appendix A: Verification record (bugs and rejected analyses)

**A.1 Degenerate coherence formula.** The original external-coherence definition |e^{i(θ̄−θ̂_h)}| ≡ 1 cannot detect misalignment; found by simulation (RSI pinned at 0.999 across intent changes), fixed to Eq. (2).

**A.2 Phase-wrapping bug.** ψ computed as (wrapped θ̄) − (unwrapped θ_h) inflated full-system τ ratios to 4.3–14.5×; fixed by wrapping the difference.

**A.3 Sign convention.** The implemented coupling direction yields dψ/dt = −Δω − K_eff sin ψ; the initially assumed +Δω made predictions incomparable.

**A.4 Fabricated data column.** An externally supplied "empirical" table for the critical-damping hypothesis contained a steady-state column derived algebraically from the transient column; direct measurement (steady-state Φ_ext ≈ 0.99 ∀ β_min) exposed it.

**A.5 Rejected calibrator.** An externally supplied β_min calibrator produced hardcoded recommendations that failed cross-validation against full simulations (e.g., predicted Φ_ext = 0.66 vs measured 0.998 at σ = 0.05).

---

*Draft v0.1. To do before submission: Zenodo/GitHub DOI for code; endorsement or direct journal submission (Chaos / Physica D); final pass on references [5] vs a dedicated SNIC review; English proofread.*
