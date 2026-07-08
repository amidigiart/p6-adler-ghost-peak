"""
Calibrare REALA pentru beta_min, derivata din date de simulare, nu presupusa.

Scenariu: N oscilatori interni + om cu schimbare reala de intentie (omega 1.0->1.3
la t=15, ->0.9 la t=35), proxy cu zgomot variabil sigma. Masor:
  - Phi_extern_sensitivity: cat de bine detecteaza sistemul dezalinierea reala
    (Phi_extern minim in fereastra de 5s dupa fiecare schimbare)
  - jitter: std al ratei de schimbare a fazei medii de grup, in perioade STABILE
    (zgomot fara schimbare reala de intentie - vulnerabilitatea la P1)
"""
import numpy as np

def run_sim(beta_min, proxy_noise_std, seed):
    np.random.seed(seed)
    N=30; dt=0.02; T_steps=3000; K_int=1.2; K_ext=1.5
    omega_i = np.random.normal(1.0,0.05,N)

    def true_human_omega(t):
        if t < 15: return 1.0
        elif t < 35: return 1.3
        else: return 0.9

    theta_human_true=0.0
    x_hat=np.array([0.0,1.0]); P=np.eye(2)*1.0
    F=np.array([[1,dt],[0,1]]); Q=np.diag([1e-4,1e-3])
    H=np.array([[1.0,0.0]]); R=np.array([[max(proxy_noise_std**2, 1e-4)]])  # R calibrat corect de data asta

    theta_i=np.random.uniform(0,2*np.pi,N)
    RSI=0.1; RSI_history=[]; theta_mean_hist=[]; Phi_e_hist=[]
    t=0.0
    for step in range(T_steps):
        t+=dt
        om_h = true_human_omega(t)
        theta_human_true += om_h*dt
        z = theta_human_true + np.random.normal(0,proxy_noise_std)
        x_pred=F@x_hat; P_pred=F@P@F.T+Q
        y_resid=z-(H@x_pred)[0]; S=H@P_pred@H.T+R
        K_gain=P_pred@H.T/S
        x_hat=x_pred+(K_gain.flatten()*y_resid)
        P=(np.eye(2)-K_gain@H)@P_pred
        theta_human_est=x_hat[0]
        beta = max(1-RSI, beta_min); alpha = 1-beta
        phase_diff = theta_i[None,:]-theta_i[:,None]
        kuramoto_term=(K_int/N)*np.sin(phase_diff).sum(axis=1)
        ext_term=K_ext*np.sin(theta_human_est-theta_i)
        dtheta=omega_i+alpha*kuramoto_term+beta*ext_term
        theta_i=theta_i+dt*dtheta
        theta_mean=np.angle(np.mean(np.exp(1j*theta_i)))
        theta_mean_hist.append(theta_mean)
        Phi_intern=np.abs(np.mean(np.exp(1j*theta_i)))
        Phi_extern=(1+np.cos(theta_mean-theta_human_est))/2.0
        Phi_e_hist.append(Phi_extern)
        Phi_t=alpha*Phi_intern+beta*Phi_extern
        RSI_history.append(Phi_t); RSI=np.mean(RSI_history[-50:])

    Phi_e = np.array(Phi_e_hist)
    tm_unwrapped = np.unwrap(np.array(theta_mean_hist))
    rate = np.diff(tm_unwrapped)/dt

    switch1, switch2 = int(15/dt), int(35/dt)
    # sensibilitate: cat de mult scade Phi_extern real dupa cele 2 schimbari
    sens1 = 1 - Phi_e[switch1:switch1+250].min()
    sens2 = 1 - Phi_e[switch2:switch2+250].min()
    sensitivity = (sens1 + sens2) / 2   # mai mare = mai sensibil la dezaliniere reala (bun)

    # jitter: std al ratei in perioada stabila INAINTE de prima schimbare (doar zgomot, fara semnal real)
    stable_period = rate[100:700]  # t=2 pana la t=14, stabil
    jitter = stable_period.std()

    return sensitivity, jitter

# --- GRID DE CALIBRARE ---
noise_grid = [0.1, 0.25, 0.5, 1.0, 1.5, 2.0, 2.5]
beta_min_grid = [0.0, 0.02, 0.05, 0.08, 0.1, 0.15, 0.2, 0.3]
seeds = [1, 2, 3]

print(f"{'sigma':>6} {'beta_min':>9} {'sensitivity':>12} {'jitter':>9}")
results = {}
for sigma in noise_grid:
    for bmin in beta_min_grid:
        sens_list, jit_list = [], []
        for s in seeds:
            sens, jit = run_sim(bmin, sigma, s)
            sens_list.append(sens); jit_list.append(jit)
        sens_mean = np.mean(sens_list); jit_mean = np.mean(jit_list)
        results[(sigma, bmin)] = (sens_mean, jit_mean)

# --- CALIBRARE: pentru fiecare sigma, gaseste cel mai mic beta_min care da sensitivity >= 0.5
# (adica Phi_extern scade sub 0.5 la o dezaliniere reala - "sistemul observa")
# SI jitter <= 0.05 (prag arbitrar declarat, dar consistent)
print("\n=== CALIBRARE DERIVATA DIN DATE (target: sensitivity>=0.5, jitter<=0.05) ===")
calib_table = []
for sigma in noise_grid:
    best = None
    for bmin in beta_min_grid:
        sens, jit = results[(sigma, bmin)]
        if sens >= 0.5 and jit <= 0.05:
            best = (bmin, sens, jit)
            break
    if best is None:
        # niciun beta_min din grid satisface ambele - ia cel cu sensitivity maxima si jitter minim posibil
        candidates = [(bmin, *results[(sigma,bmin)]) for bmin in beta_min_grid]
        # alege cel cu sensitivity>=0.5 cel mai mic jitter, daca exista
        valid = [c for c in candidates if c[1] >= 0.5]
        if valid:
            best = min(valid, key=lambda c: c[2])
        else:
            best = max(candidates, key=lambda c: c[1])
    calib_table.append((sigma, *best))
    print(f"sigma={sigma:.2f}: beta_min={best[0]:.2f}  sensitivity={best[1]:.4f}  jitter={best[2]:.4f}")

print("\n=== TABEL COMPLET (toate combinatiile, pt referinta) ===")
print(f"{'sigma':>6} {'beta_min':>9} {'sensitivity':>12} {'jitter':>9}")
for sigma in noise_grid:
    for bmin in beta_min_grid:
        sens, jit = results[(sigma, bmin)]
        print(f"{sigma:6.2f} {bmin:9.2f} {sens:12.4f} {jit:9.4f}")
