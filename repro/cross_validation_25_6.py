# -*- coding: utf-8 -*-
"""
Verificare încrucișată a Secțiunii 25.6 — DUPĂ primirea specificației complete
(pentru_fable.zip: calibration_real.py + RASPUNS_METRICA_25_6.md, 8 iulie 2026).

Reimplementare independentă a protocolului acum-specificat, în stil propriu:
  - câmp mediu complex vectorizat (echivalent matematic cu suma pairwise O(N²))
  - filtru Kalman propriu (aceeași structură F/H/Q/R, cod diferit)
  - ALTE seed-uri (10, 11, 12 vs originalele 1, 2, 3) și alt RNG
    (np.random.default_rng vs np.random.seed legacy)

Dacă vârful de sensibilitate la β_min=0.15 apare și aici, fenomenul e o
proprietate a sistemului specificat, nu a implementării sau a seed-urilor.

Protocol (din specificația primită):
  N=30, dt=0.02, T=3000 pași, K_int=1.2, K_ext=1.5, ω_i~N(1.0, 0.05)
  ω_uman: 1.0 -> 1.3 (t=15) -> 0.9 (t=35);  Δω₁=0.3, Δω₂=0.4
  dθ = ω + α·(K_int/N)Σsin(θj-θi) + β·K_ext·sin(θ_est-θ);  β=max(1-RSI,β_min)
  Φ_ext=(1+cos(θ_mean-θ_est))/2;  RSI = medie mobilă 50 pași a Φ=αΦ_int+βΦ_ext
  sensibilitate = medie( 1-min(Φ_ext) pe 250 pași după fiecare comutare )
  jitter = std( dθ_mean/dt ) pe pașii 100-700 (regim stabil, doar zgomot)
"""
import numpy as np

N, DT, T_STEPS, K_INT, K_EXT = 30, 0.02, 3000, 1.2, 1.5

def run(beta_min, sigma, seed):
    rng = np.random.default_rng(seed)
    omega = rng.normal(1.0, 0.05, N)
    theta = rng.uniform(0, 2 * np.pi, N)
    th_h = 0.0

    # Kalman: stare [faza, viteza], observație = faza adevărată + zgomot
    x = np.array([0.0, 1.0])
    P = np.eye(2)
    F = np.array([[1.0, DT], [0.0, 1.0]])
    Q = np.diag([1e-4, 1e-3])
    R = max(sigma**2, 1e-4)

    RSI = 0.1
    phi_buf, phi_ext_hist, thm_hist = [], [], []
    for k in range(T_STEPS):
        t = (k + 1) * DT
        om_h = 1.0 if t < 15 else (1.3 if t < 35 else 0.9)
        th_h += om_h * DT
        z = th_h + rng.normal(0, sigma)

        # Kalman predict + update (implementare proprie, scalară pe inovație)
        x = F @ x
        P = F @ P @ F.T + Q
        innov = z - x[0]
        S = P[0, 0] + R
        Kg = P[:, 0] / S
        x = x + Kg * innov
        P = P - np.outer(Kg, P[0, :])
        th_est = x[0]

        beta = max(1.0 - RSI, beta_min)
        alpha = 1.0 - beta

        zc = np.exp(1j * theta)
        mf = zc.mean()
        kuramoto = K_INT * np.imag(np.exp(-1j * theta) * mf)   # (K/N)Σsin(θj-θi)
        theta = theta + DT * (omega + alpha * kuramoto
                              + beta * K_EXT * np.sin(th_est - theta))

        th_mean = np.angle(np.exp(1j * theta).mean())
        phi_int = abs(np.exp(1j * theta).mean())
        phi_ext = (1 + np.cos(th_mean - th_est)) / 2
        phi_buf.append(alpha * phi_int + beta * phi_ext)
        if len(phi_buf) > 50:
            phi_buf.pop(0)
        RSI = np.mean(phi_buf)
        phi_ext_hist.append(phi_ext)
        thm_hist.append(th_mean)

    phi_e = np.array(phi_ext_hist)
    s1, s2 = int(15 / DT), int(35 / DT)
    sens = ((1 - phi_e[s1:s1 + 250].min()) + (1 - phi_e[s2:s2 + 250].min())) / 2
    rate = np.diff(np.unwrap(np.array(thm_hist))) / DT
    jitter = rate[100:700].std()
    return sens, jitter

if __name__ == "__main__":
    noise_grid = [0.1, 0.25, 0.5, 1.0, 1.5, 2.0, 2.5]
    beta_grid = [0.0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30]
    seeds = [10, 11, 12]   # DIFERITE de originalele [1,2,3]

    print(f"{'sigma':>6} " + " ".join(f"b={b:<5}" for b in beta_grid))
    peaks = []
    for sigma in noise_grid:
        row = []
        for bm in beta_grid:
            s = np.mean([run(bm, sigma, sd)[0] for sd in seeds])
            row.append(s)
        peak_b = beta_grid[int(np.argmax(row))]
        peaks.append(peak_b)
        print(f"{sigma:6.2f} " + " ".join(f"{v:7.4f}" for v in row)
              + f"   vârf: β_min={peak_b}")
    print(f"\nVârf pe toate nivelurile de zgomot: {peaks}")
    print("Original (seed 1-3, implementare pairwise): vârf la 0.15 peste tot.")
