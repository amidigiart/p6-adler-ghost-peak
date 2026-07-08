# -*- coding: utf-8 -*-
"""
Reproducere independentă a rezultatelor din P6_bifurcatie_Adler.md
(REAI v0.7.2, Secțiunile 25-26), Mihai Roșca.

Reimplementare DOAR din ecuațiile și parametrii declarați în text,
fără acces la codul original. Autor al reproducerii: Claude (sesiune
Claude Code, iulie 2026), rulat local pe mașina autorului.

Afirmațiile verificate:
  A. Φ_extern = |e^{i(θ_mean-θ_uman)}| este degenerată (≡1)         [Secț. 25.1]
  B. Ecuația Adler izolată: exponent divergență τ_relax ≈ -0.5,
     T_slip măsurat/prezis ≈ 1.0                                    [Etapa 2, 26.3]
  C. Sistem complet (N=30): τ măsurat vs τ prezis = 1/sqrt(K_eff²-Δω²),
     raport așteptat 0.985-0.996 pentru β ∈ {0.35,0.4,0.5,0.7,1.0}  [Etapa 3, 26.3]
  D. Vârf ne-monoton de sensibilitate la β_min ≈ 0.12-0.15 cu
     fereastră fixă de măsurare + prag de blocare empiric ≈ 0.25    [Secț. 25.6, 26.3 Etapa 1]

Parametri declarați în text:      K_ext=1.5, Δω=0.3 (dedus din tabelul τ),
                                  fereastră RSI=50 pași, fereastră măsurare=250 pași,
                                  N=30, prag analitic β_min=0.20.
Parametri NEdeclarați în text (alegeri proprii, documentate ca gap):
                                  K_int=2.0, spread ω_i: σ=0.01, dt (B: 0.001, C: 0.005,
                                  D: 0.1), integrator RK4 (B,C) / Euler (D),
                                  amplitudine kick=0.2 rad, σ_zgomot=0.25 (D).
"""
import numpy as np

rng_global = np.random.default_rng(42)

# ---------------------------------------------------------------- utilitare
def wrap(x):
    return np.angle(np.exp(1j * x))

def rk4(f, y, dt):
    k1 = f(y)
    k2 = f(y + 0.5 * dt * k1)
    k3 = f(y + 0.5 * dt * k2)
    k4 = f(y + dt * k3)
    return y + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

print("=" * 72)
print("PARTEA A — degenerarea formulei Φ_extern = |e^{i(θm-θh)}|  [Secț. 25.1]")
print("=" * 72)
for d in [0.0, 0.5, 1.0, np.pi / 2, np.pi, 2.7]:
    print(f"  Δfază = {d:6.3f}  ->  |e^(iΔ)| = {abs(np.exp(1j*d)):.6f}")
print("  Verdict: modulul e 1 pentru orice diferență de fază -> formula nu")
print("  poate detecta dezalinierea. CONFIRMAT trivial, cum afirmă textul.\n")

# ---------------------------------------------------------------- PARTEA B
print("=" * 72)
print("PARTEA B — ecuația Adler izolată: dψ/dt = -Δω - K_eff·sin(ψ)")
print("=" * 72)
DW = 0.3

def adler_tau_measured(K, dt=1e-3):
    """Timp de relaxare asimptotic spre ψ* prin fit pe ln|ψ-ψ*|."""
    psi_star = -np.arcsin(DW / K)
    f = lambda p: -DW - K * np.sin(p)
    psi = psi_star + 0.1
    ts, ds = [], []
    t = 0.0
    for _ in range(int(5e6)):
        psi = rk4(f, psi, dt)
        t += dt
        d = abs(wrap(psi - psi_star))
        if d < 1e-5:
            break
        if 1e-4 < d < 0.05:
            ts.append(t); ds.append(d)
    ts, ds = np.array(ts), np.array(ds)
    slope = np.polyfit(ts, np.log(ds), 1)[0]
    return -1.0 / slope

# B1: exponentul divergenței tau ~ (K-Δω)^(-1/2)
eps = np.logspace(-3, -1, 9)
Ks = DW * (1 + eps)
taus = np.array([adler_tau_measured(K) for K in Ks])
exponent = np.polyfit(np.log(Ks - DW), np.log(taus), 1)[0]
print(f"  B1. Exponent măsurat al divergenței τ_relax: {exponent:+.4f}")
print(f"      Predicție analitică: -0.5  |  Textul raportează: -0.5009")

# B2: perioada de alunecare sub prag
print("  B2. T_slip măsurat vs prezis = 2π/sqrt(Δω²-K²):")
for frac in [0.5, 0.8, 0.95, 0.99]:
    K = DW * frac
    f = lambda p: -DW - K * np.sin(p)
    psi, t, dt = 0.0, 0.0, 1e-3
    crossings = []
    prev = np.sin(psi / 2)
    unwrapped = psi
    # măsurăm timpul pentru M alunecări complete de 2π
    target, M = unwrapped - 2 * np.pi * 8, 8
    while unwrapped > target:
        psi_new = rk4(f, psi, dt)
        unwrapped += (psi_new - psi) if abs(psi_new - psi) < np.pi else 0
        psi = psi_new
        t += dt
    T_meas = t / M
    T_pred = 2 * np.pi / np.sqrt(DW**2 - K**2)
    print(f"      K/Δω={frac:.2f}:  măsurat={T_meas:9.3f}  prezis={T_pred:9.3f}"
          f"  raport={T_meas/T_pred:.4f}")
print()

# ---------------------------------------------------------------- PARTEA C
print("=" * 72)
print("PARTEA C — sistem complet, N=30 oscilatori  [Etapa 3, Secț. 26.3]")
print("=" * 72)
N, K_INT, K_EXT = 30, 2.0, 1.5
OMEGA_MEAN, OMEGA_HUMAN = 0.3, 0.0          # Δω = 0.3, dedus din tabelul textului
omega_i = OMEGA_MEAN + 0.01 * rng_global.standard_normal(N)

def full_system_tau(beta, dt=5e-3):
    """Settle -> kick de fază pe θ_uman -> fit exponențial pe revenirea lui ψ."""
    K_eff = beta * K_EXT
    theta = rng_global.uniform(-np.pi, np.pi, N)
    th_h = 0.0

    def step(theta, th_h):
        # (K_int/N)·Σ_j sin(θj-θi) scris vectorizat prin câmpul mediu complex
        f = lambda th: (omega_i
                        + K_INT * np.imag(np.exp(-1j * th) * np.exp(1j * th).mean())
                        + beta * K_EXT * np.sin(th_h - th))
        theta = rk4(f, theta, dt)
        return theta, th_h + OMEGA_HUMAN * dt

    for _ in range(int(400 / dt)):  # settle: 400 unități de timp
        theta, th_h = step(theta, th_h)
    # ψ* empiric = media pe ultimele 2000 de pași
    psis = []
    for _ in range(2000):
        theta, th_h = step(theta, th_h)
        psis.append(wrap(np.angle(np.exp(1j * theta).mean()) - th_h))
    psi_star = np.mean(psis[-500:])
    # kick
    th_h += 0.2
    ts, ds, t = [], [], 0.0
    for _ in range(int(200 / dt)):
        theta, th_h = step(theta, th_h)
        t += dt
        d = abs(wrap(np.angle(np.exp(1j * theta).mean()) - th_h - psi_star))
        if 1e-3 < d < 0.05:
            ts.append(t); ds.append(d)
        if d < 5e-4 and t > 1.0:
            break
    slope = np.polyfit(ts, np.log(ds), 1)[0]
    return -1.0 / slope

print(f"  Parametri: K_int={K_INT} (ALES, nedeclarat în text), K_ext={K_EXT},")
print(f"  Δω={OMEGA_MEAN-OMEGA_HUMAN}, spread ω_i σ=0.01 (ALES), kick=0.2 rad\n")
print("  β_min    K_eff    τ prezis   τ măsurat   raport      (text: raport)")
text_ratios = {0.35: 0.9847, 0.40: 0.9899, 0.50: 0.9944, 0.70: 0.9965, 1.00: 0.9962}
for beta in [0.35, 0.40, 0.50, 0.70, 1.00]:
    K_eff = beta * K_EXT
    tau_pred = 1.0 / np.sqrt(K_eff**2 - DW**2)
    tau_meas = full_system_tau(beta)
    print(f"  {beta:4.2f}    {K_eff:5.3f}    {tau_pred:7.4f}    {tau_meas:7.4f}"
          f"    {tau_meas/tau_pred:6.4f}      ({text_ratios[beta]:.4f})")
print()

# ---------------------------------------------------------------- PARTEA D
print("=" * 72)
print("PARTEA D — bucla adaptivă RSI-β: prag de blocare + vârf de sensibilitate")
print("=" * 72)
# Scenariul din Secț. 25: ω_uman 1.0 -> 1.3 (Δω=0.3), zgomot pe observație σ=0.25,
# RSI = medie mobilă 50 pași, fereastră de măsurare 250 pași, dt ALES = 0.1.
def adaptive_run(beta_min, seed, sigma_noise=0.25, dt=0.1):
    rng = np.random.default_rng(seed)
    om = 1.0 + 0.01 * rng.standard_normal(N)
    theta = rng.uniform(-np.pi, np.pi, N)
    th_h, om_h = 0.0, 1.0
    RSI, beta = 0.5, max(0.5, beta_min)
    phi_ext_hist, rsi_buf = [], []
    n_settle, n_meas = 1000, 250
    slips = 0
    for k in range(n_settle + n_meas):
        if k == n_settle:
            om_h = 1.3                                   # schimbarea reală de intenție
        th_h_obs = th_h + sigma_noise * rng.standard_normal()
        z = np.exp(1j * theta)
        th_mean = np.angle(z.mean())
        phi_int = abs(z.mean())
        phi_ext = (1 + np.cos(th_mean - th_h_obs)) / 2    # formula corectată 25.1
        beta = max(1 - RSI, beta_min)
        alpha = 1 - beta
        phi = alpha * phi_int + beta * phi_ext
        rsi_buf.append(phi)
        if len(rsi_buf) > 50:
            rsi_buf.pop(0)
        RSI = np.mean(rsi_buf)
        theta += dt * (om + K_INT * np.imag(np.exp(-1j * theta) * z.mean())
                       + beta * K_EXT * np.sin(th_h_obs - theta))
        th_h += om_h * dt
        phi_true = (1 + np.cos(wrap(np.angle(np.exp(1j*theta).mean()) - th_h))) / 2
        if k >= n_settle:
            phi_ext_hist.append(phi_true)
            if phi_true < 0.1:
                slips += 1
    baseline = 1.0
    dip = baseline - min(phi_ext_hist)
    return dip, slips

print("  Sensibilitate = adâncimea dip-ului Φ_extern în fereastra de 250 pași")
print("  după schimbarea ω_uman 1.0->1.3, mediată pe 10 seed-uri.\n")
print("  β_min    dip mediu   (±std)     pași cu Φ<0.1 (medie)")
betas = [0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20, 0.25, 0.30]
results = {}
for bm in betas:
    dips, slps = zip(*[adaptive_run(bm, s) for s in range(10)])
    results[bm] = (np.mean(dips), np.std(dips), np.mean(slps))
    print(f"  {bm:4.2f}     {np.mean(dips):6.3f}    (±{np.std(dips):5.3f})"
          f"      {np.mean(slps):6.1f}")
peak = max(results, key=lambda b: results[b][0])
print(f"\n  Vârf de sensibilitate găsit la β_min = {peak}"
      f"  (textul raportează 0.12-0.15; pragul analitic Adler: β=0.20)")
print("  NOTĂ: dt, K_int, modelul de zgomot sunt alegeri proprii — textul nu le")
print("  specifică. Poziția exactă a vârfului poate depinde de ele (vezi raport).")
