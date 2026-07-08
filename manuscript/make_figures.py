# -*- coding: utf-8 -*-
"""
Figurile manuscrisului + verificarea numerică a derivării marjei de siguranță.

Fig. 1  Schema sistemului (N oscilatori + referință umană + bucla RSI-beta)
Fig. 2  Diagrama de bifurcație Adler (ramura stabilă/instabilă, regim alunecat)
Fig. 3  Log-log: tau_relax vs (K_eff - dw) — ecuația izolată + sistemul complet
Fig. 4  Vârful-fantomă de sensibilitate vs beta_min, cu pragurile Adler marcate

Derivarea marjei (intră în manuscris, Secțiunea Calibration rule):
    tau_relax = 1/sqrt(K_eff^2 - dw^2) <= tau_target
    K_eff >= sqrt(dw^2 + 1/tau_target^2)
    m(tau_target) = K_eff/dw = sqrt(1 + 1/(dw*tau_target)^2)
    Invers: marja m garanteaza tau_relax <= 1/(dw*sqrt(m^2-1)).
    Pentru m=1.5: tau_relax <= 0.894/dw  (recuperare sub un timp caracteristic 1/dw).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)

# Okabe-Ito (CVD-safe, validat cu scripts/validate_palette.js: ALL PASS)
BLUE, VERM, GREEN, GRAY = "#0072B2", "#D55E00", "#009E73", "#7f7f7f"
plt.rcParams.update({
    "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.5,
    "figure.dpi": 100, "savefig.dpi": 300, "savefig.bbox": "tight",
    "mathtext.fontset": "dejavusans",
})
DW = 0.3

def wrap(x): return np.angle(np.exp(1j * x))

def rk4(f, y, dt):
    k1=f(y); k2=f(y+0.5*dt*k1); k3=f(y+0.5*dt*k2); k4=f(y+dt*k3)
    return y + (dt/6)*(k1+2*k2+2*k3+k4)

# ------------------------------------------------------------------ derivare
print("=== Verificare numerică a regulii de marjă ===")
print("m(tau_target) = sqrt(1 + 1/(dw*tau)^2);  m=1.5 => tau <= 1/(dw*sqrt(1.25))")
def adler_tau(K, dt=1e-3):
    ps = -np.arcsin(DW/K); f = lambda p: -DW - K*np.sin(p)
    psi, t, ts, ds = ps+0.1, 0.0, [], []
    for _ in range(int(5e6)):
        psi = rk4(f, psi, dt); t += dt
        d = abs(wrap(psi-ps))
        if d < 1e-5: break
        if 1e-4 < d < 0.05: ts.append(t); ds.append(d)
    return -1/np.polyfit(ts, np.log(ds), 1)[0]

for m in [1.2, 1.5, 2.0, 3.0]:
    K = m*DW
    tau_pred = 1/(DW*np.sqrt(m**2-1))
    tau_meas = adler_tau(K)
    print(f"  m={m:.1f}:  tau garantat={tau_pred:7.4f}   tau măsurat={tau_meas:7.4f}"
          f"   raport={tau_meas/tau_pred:.4f}")
print(f"  Interpretare m=1.5: tau <= {1/np.sqrt(1.25):.3f}/dw — sub un timp caracteristic 1/dw\n")

# ------------------------------------------------------------------ FIG 1
fig, ax = plt.subplots(figsize=(5.2, 3.2))
ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
rng = np.random.default_rng(3)
# grup de oscilatori interni
cx, cy = 2.6, 3.6
for a, r in zip(np.linspace(0, 2*np.pi, 12, endpoint=False), 0.85+0.25*rng.random(12)):
    ax.plot(cx+r*np.cos(a), cy+r*np.sin(a), "o", ms=7, color=BLUE, mec="white", mew=0.8)
circ = plt.Circle((cx, cy), 1.45, fill=False, ls=":", lw=1, color=BLUE)
ax.add_patch(circ)
ax.text(cx, cy, r"$\theta_i,\ \omega_i$" + "\n" + r"$K_{int}$", ha="center", va="center", fontsize=9)
ax.text(cx, 5.45, "N internal oscillators", ha="center", fontsize=9, color=BLUE)
# omul
ax.plot(8.3, 3.6, "o", ms=16, color=VERM, mec="white")
ax.text(8.3, 5.45, "human reference", ha="center", fontsize=9, color=VERM)
ax.text(8.3, 4.35, r"$\theta_{human},\ \omega_{human}$", ha="center", fontsize=9)
# Kalman
ax.add_patch(plt.Rectangle((5.35, 3.15), 1.7, 0.95, fill=False, lw=1, ec="black"))
ax.text(6.2, 3.62, "Kalman\n" + r"$\hat{\theta}_{human}$", ha="center", va="center", fontsize=8)
# sageti: om -> proxy -> Kalman -> cuplaj
ax.annotate("", xy=(7.1, 3.62), xytext=(7.95, 3.62), arrowprops=dict(arrowstyle="->", lw=1.2))
ax.text(7.52, 2.95, "noisy\nproxies", ha="center", va="top", fontsize=7, color=GRAY)
ax.annotate("", xy=(4.1, 3.62), xytext=(5.3, 3.62),
            arrowprops=dict(arrowstyle="->", lw=1.6, color=VERM))
ax.text(4.7, 4.35, r"$\beta\,K_{ext}\sin(\hat{\theta}_{human}-\theta_i)$",
        ha="center", fontsize=8, color=VERM)
# bucla RSI-beta
ax.add_patch(plt.Rectangle((3.6, 0.7), 2.9, 0.95, fill=False, lw=1, ec=GREEN))
ax.text(5.05, 1.17, r"RSI $\to$ $\beta=\max(1-\mathrm{RSI},\,\beta_{min})$",
        ha="center", va="center", fontsize=8, color=GREEN)
ax.annotate("", xy=(4.6, 1.7), xytext=(3.0, 2.35),
            arrowprops=dict(arrowstyle="->", lw=1, color=GREEN,
                            connectionstyle="arc3,rad=-0.25"))
ax.text(3.0, 1.75, r"$\Phi_{int},\,\Phi_{ext}$", fontsize=8, color=GREEN, ha="center")
ax.annotate("", xy=(5.6, 3.1), xytext=(5.9, 1.7),
            arrowprops=dict(arrowstyle="->", lw=1, color=GREEN,
                            connectionstyle="arc3,rad=-0.2"))
ax.text(6.35, 2.3, r"$\beta$", fontsize=9, color=GREEN)
fig.savefig(OUT/"fig1_system.png"); fig.savefig(OUT/"fig1_system.pdf"); plt.close(fig)
print("fig1 salvată")

# ------------------------------------------------------------------ FIG 2
k = np.linspace(1.0001, 5, 400)
fig, ax = plt.subplots(figsize=(4.4, 3.0))
ax.axvspan(0.55, 1, color=GRAY, alpha=0.15, lw=0)
ax.text(0.775, -1.65, "phase slipping\n(no fixed point)", ha="center", va="center",
        fontsize=8, color="black", rotation=90)
ax.plot(k, -np.arcsin(1/k), color=BLUE, lw=2, label="stable  $\\psi^*$")
ax.plot(k, -np.pi+np.arcsin(1/k), color=VERM, lw=1.6, ls="--", label="unstable")
ax.plot([1], [-np.pi/2], "o", ms=7, color="black", zorder=5)
ax.annotate("SNIC bifurcation\n$K_{eff}=\\Delta\\omega$", xy=(1, -np.pi/2),
            xytext=(1.9, -2.45), fontsize=8,
            arrowprops=dict(arrowstyle="->", lw=0.8))
ax.set_xlim(0.55, 5); ax.set_ylim(-np.pi-0.25, 0.25)
ax.set_yticks([0, -np.pi/2, -np.pi], ["0", r"$-\pi/2$", r"$-\pi$"])
ax.set_xlabel(r"$K_{eff}/\Delta\omega$")
ax.set_ylabel(r"phase lag  $\psi^*$")
ax.legend(frameon=False, loc="upper right", fontsize=8)
fig.savefig(OUT/"fig2_bifurcation.png"); fig.savefig(OUT/"fig2_bifurcation.pdf"); plt.close(fig)
print("fig2 salvată")

# ------------------------------------------------------------------ FIG 3 date
print("Generez datele Fig. 3 (poate dura ~2 min)...")
K_iso = DW*(1+np.logspace(-3, 0.7, 10))
tau_iso = np.array([adler_tau(min(K, 2.0)) for K in K_iso])

N, K_EXT, K_INT = 30, 1.5, 2.0
rngg = np.random.default_rng(42)
omega_i = 0.3 + 0.01*rngg.standard_normal(N)
def full_tau(beta, dt=5e-3):
    th = rngg.uniform(-np.pi, np.pi, N); hh = 0.0
    def step(th, hh):
        f = lambda x: (omega_i + K_INT*np.imag(np.exp(-1j*x)*np.exp(1j*x).mean())
                       + beta*K_EXT*np.sin(hh-x))
        return rk4(f, th, dt), hh
    for _ in range(int(600/dt)): th, hh = step(th, hh)
    # psi* empiric
    vals=[]
    for _ in range(1000):
        th, hh = step(th, hh); vals.append(wrap(np.angle(np.exp(1j*th).mean())-hh))
    pss = np.mean(vals[-300:])
    hh += 0.2
    ts, ds, t = [], [], 0.0
    for _ in range(int(400/dt)):
        th, hh = step(th, hh); t += dt
        d = abs(wrap(np.angle(np.exp(1j*th).mean())-hh-pss))
        if 1e-3 < d < 0.05: ts.append(t); ds.append(d)
        if d < 5e-4 and t > 1: break
    return -1/np.polyfit(ts, np.log(ds), 1)[0]

betas_full = [0.25, 0.30, 0.35, 0.40, 0.50, 0.70, 1.00]
K_full = np.array([b*K_EXT for b in betas_full])
tau_full = np.array([full_tau(b) for b in betas_full])

fig, ax = plt.subplots(figsize=(4.6, 3.4))
x = np.logspace(np.log10(3e-4), np.log10(1.3), 200)
ax.plot(x, 1/np.sqrt((DW+x)**2-DW**2), color="black", lw=1,
        label=r"analytic  $\tau=(K_{eff}^2-\Delta\omega^2)^{-1/2}$")
ax.plot(K_iso-DW, tau_iso, "o", ms=6, color=BLUE, mec="white", mew=0.7,
        label="isolated Adler equation")
ax.plot(K_full-DW, tau_full, "s", ms=6, color=VERM, mec="white", mew=0.7,
        label="full system, $N=30$")
xg = np.array([4e-4, 8e-3])
ax.plot(xg, 0.55*(2*DW)**-0.5*xg**-0.5, ls=":", lw=1.2, color=GRAY)
ax.text(2.2e-3, 16, "slope $-1/2$", fontsize=8, color=GRAY, rotation=-18)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel(r"$K_{eff}-\Delta\omega$")
ax.set_ylabel(r"relaxation time  $\tau_{relax}$")
ax.legend(frameon=False, fontsize=7.5, loc="lower left")
fig.savefig(OUT/"fig3_scaling.png"); fig.savefig(OUT/"fig3_scaling.pdf"); plt.close(fig)
print("fig3 salvată")

# ------------------------------------------------------------------ FIG 4
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "repro"))
from cross_validation_25_6 import run as cv_run
beta_grid = [0.0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30]
orig = [0.2920, 0.2732, 0.2549, 0.2657, 0.3388, 0.5822, 0.3072, 0.1367]  # seeds 1-3
mine_mean, mine_std = [], []
for bm in beta_grid:
    v = [cv_run(bm, 0.25, sd)[0] for sd in [10, 11, 12]]
    mine_mean.append(np.mean(v)); mine_std.append(np.std(v))

fig, ax = plt.subplots(figsize=(4.6, 3.2))
for thr, lab in [(0.20, r"$\beta_{thr,1}=\Delta\omega_1/K_{ext}$"),
                 (0.267, r"$\beta_{thr,2}=\Delta\omega_2/K_{ext}$")]:
    ax.axvline(thr, ls="--", lw=1, color=GRAY)
    ax.text(thr+0.004, 0.70, lab, rotation=90, fontsize=7, color=GRAY, va="top")
ax.plot(beta_grid, orig, "o-", color=BLUE, lw=1.6, ms=6, mec="white", mew=0.7,
        label="original (seeds 1–3)")
ax.errorbar(beta_grid, mine_mean, yerr=mine_std, fmt="s-", color=VERM, lw=1.6,
            ms=5.5, mec="white", mew=0.7, capsize=2.5,
            label="independent reimpl. (seeds 10–12)")
ax.set_xlabel(r"coupling floor  $\beta_{min}$")
ax.set_ylabel("transient sensitivity (5 s window)")
ax.set_ylim(0, 0.75)
ax.legend(frameon=False, fontsize=7.5, loc="upper left")
fig.savefig(OUT/"fig4_ghost_peak.png"); fig.savefig(OUT/"fig4_ghost_peak.pdf"); plt.close(fig)
print("fig4 salvată")
print("\nToate figurile în:", OUT)
