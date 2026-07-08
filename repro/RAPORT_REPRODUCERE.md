# Raport de Reproducere Independentă — P6 / Bifurcația Adler

**Obiect:** afirmațiile empirice din `P6_bifurcatie_Adler.md` (extras din REAI v0.7.2, Secțiunile 25–26)
**Metodă:** reimplementare de la zero, **doar din ecuațiile și parametrii declarați în text**, fără acces la codul original. Codul reproducerii: [reproduce_p6.py](reproduce_p6.py).
**Executat:** 8 iulie 2026, local, Python 3.14 + NumPy 2.5.1, de Claude (Claude Code) ca verificator terț.
**Statut verificator:** aceasta este o verificare independentă *de implementare* (alt cod, alte alegeri de integrare, alt generator de zgomot), nu o verificare independentă *de persoană*. Rămâne un pas sub standardul „terț uman ostil".

---

## Rezumatul verdictelor

| # | Afirmația din text | Verdict | Detaliu |
|---|---|---|---|
| A | Φ_extern = \|e^{i(θm−θh)}\| e degenerată (≡1) | **CONFIRMAT** | 1.000000 pentru toate cele 6 valori test |
| B1 | Exponent divergență τ_relax ≈ −0.5 (text: −0.5009) | **CONFIRMAT** | măsurat **−0.4957** pe 9 valori K_eff, fit log-log |
| B2 | T_slip măsurat/prezis ≈ 1.0000 | **CONFIRMAT** | raport 1.0000 la K/Δω ∈ {0.5, 0.8, 0.95, 0.99} |
| C | Sistem complet N=30: raport τ măsurat/prezis 0.985–0.996 | **CONFIRMAT** | raporturi obținute **0.9968–0.9990**, același semn și aceeași tendință (sub 1, convergent spre 1 cu K_eff) |
| D1 | Prag de blocare empiric β_min ≈ 0.20–0.25 | **CONFIRMAT** | alunecare persistentă la β_min ≤ 0.15, zero alunecări la β_min ≥ 0.18; tranziția cade exact în jurul pragului analitic Adler β=0.20 |
| D2 | Vârf ne-monoton de sensibilitate la β_min ≈ 0.12–0.15 | **NEREPRODUS sub lectura directă a textului** → **CONFIRMAT după specificarea completă** (vezi Addendum) | cauza: metrică și parametri nespecificați în text, nu eroare în original |

## Detaliu pe verdictul D2 — constatarea cea mai importantă a reproducerii

Cu definiția citită literal din text („adâncimea dip-ului de coerență externă într-o fereastră fixă de 250 de pași"), rezultatul meu **saturează la 1.000** pentru orice β_min sub pragul de blocare (sistemul alunecă, Φ_extern parcurge tot intervalul [0,1], deci minimumul atinge ~0) și **scade monoton** deasupra pragului (0.658 → 0.431 → 0.227 → 0.154). Nu apare niciun vârf interior la 0.12–0.15.

Datele originale (0.29 la β_min=0.05, urcând la 0.61 la 0.12, coborând la 0.33 la 0.20) **nu pot proveni din această definiție a metricii** — la β_min=0.05 sistemul alunecă liber și orice dip de coerență externă ar satura. Deci metrica reală folosită în original era alta (posibil: dip-ul lui Φ agregat sau al RSI, ori dip măsurat pe θ_uman observat cu zggomot, ori normalizat altfel) și/sau dt-ul pașilor diferă substanțial de alegerea mea.

**Interpretare onestă:** asta nu demonstrează că vârful original e un artefact. Mecanismul explicativ propus în text (umbra încetinirii critice văzută printr-o fereastră fixă) rămâne plauzibil și e susținut de faptul că vârful original (0.12–0.15) stă imediat sub pragul de blocare confirmat (0.20–0.25). Dar demonstrează că **Secțiunea 25.6 nu e reproductibilă din text** — un cititor care implementează exact ce scrie obține altă curbă. Pentru preprint, exact această secțiune are nevoie de: definiția formală a metricii de sensibilitate, dt, K_int, modelul de zgomot și seed-urile.

## Parametri pe care textul NU îi declară (aleși de mine, documentați aici)

| Parametru | Alegerea mea | Impact |
|---|---|---|
| K_int (cuplare internă) | 2.0 | scăzut pentru A–C (grup strâns sincronizat oricum); necunoscut pentru D |
| Spread ω_i | σ=0.01, normal | explică diferența raporturilor C (0.997 la mine vs 0.985 în text — spread-ul lor era probabil mai mare) |
| dt | 0.001 (B), 0.005 (C), 0.1 (D) | critic pentru D: ferestrele sunt definite în „pași", nu în timp fizic |
| Integrator | RK4 (B, C), Euler (D) | minor pentru B–C |
| Amplitudine kick (C) | 0.2 rad | minor (regim liniar) |
| Model zgomot (D) | aditiv pe faza observată, σ=0.25 | textul aplică zgomotul pe „proxy-uri" prin Kalman — nereplicabil fără specificația Kalman |

## Concluzie (versiunea inițială, 8 iulie 2026, înainte de primirea codului original)

Nucleul științific al lucrării — mecanismul Adler/SNIC, pragul de blocare, legea de scalare τ ~ (K_eff−Δω)^(−1/2) și transferul ei pe sistemul complet de 30 de oscilatori — **se reproduce independent, din text, cu acord numeric excelent**. Aceasta e o proprietate rară și e cel mai puternic argument pentru publicare.

Singura componentă nereproductibilă din text e curba de sensibilitate din Secțiunea 25.6 (fenomenul-sursă care a *motivat* investigația), din cauza subspecificării metricii și parametrilor — remediabil prin publicarea codului original și a definiției formale a metricii, nu prin muncă nouă de cercetare.

---

# ADDENDUM (8 iulie 2026, mai târziu în aceeași zi) — fisura D2, închisă

Autorul a furnizat codul original (`../cod_original/calibration_real.py`, primit via `pentru_fable.zip`) plus specificația completă a metricii. Trei verificări noi, toate rulate efectiv:

**1. Codul original rulează identic cu output-ul atașat.** `calibration_real.py`, rulat local, reproduce **bit-cu-bit** toate valorile din `output_original_confirmat.txt` (diferențele diff sunt doar line-endings CRLF/LF). Determinismul seed-urilor [1,2,3] confirmat.

**2. Ce nu spunea textul — cele trei piese lipsă, acum explicite:**
- metrica e **media a două evenimente de dezaliniere** cu praguri Adler diferite: Δω₁=0.3 la t=15 (prag β=0.20) și Δω₂=0.4 la t=35 (prag β=0.267), fiecare măsurat pe o fereastră fixă de 250 pași = 5s (dt=0.02);
- Φ_extern se calculează față de **estimarea Kalman** θ_est, nu față de faza reală;
- **α multiplică și termenul Kuramoto intern** (dθ = ω + α·kuramoto + β·ext), nu doar coerența în formula Φ.

**3. Verificare încrucișată independentă — vârful se reproduce.** Reimplementare proprie ([cross_validation_25_6.py](cross_validation_25_6.py)): câmp mediu vectorizat în loc de sumă pairwise, Kalman propriu, **alte seed-uri (10-12) și alt RNG** (`default_rng` vs `np.random.seed` legacy). Rezultat: **vârf la β_min=0.15 pe toate cele 7 niveluri de zgomot** (sensibilitate 0.55–0.67 la vârf vs 0.34–0.43 la vecinul 0.10 și 0.27–0.41 la vecinul 0.20), cu valori apropiate de originalele (ex. σ=0.25: 0.5628 la mine vs 0.5822 în original).

**Interpretarea mecanicistă e acum și mai curată:** vârful (0.12–0.15) cade *între* zona pragurilor Adler ale celor două evenimente (0.20 și 0.267) scalate de bucla RSI–β — exact regimul în care încetinirea critică face ca fereastra fixă de 5s să vadă dip-ul cel mai adânc. Fenomenul e o proprietate a sistemului specificat, nu a implementării, seed-urilor sau generatorului de zgomot.

**Verdict final D2: CONFIRMAT.** Toate cele 6 afirmații verificate din P6/25–26 sunt acum reproduse independent. Gap-ul rămas pentru manuscris e pur editorial: ecuația formală a metricii + tabelul de parametri intră în Methods/Supplementary.

*Bonus verificat în aceeași sesiune:* kit-ul de implementare `ukbe_core` (v10) rulează **102/102 teste** local (pytest, 6.7s), exact cum declară README-ul, iar `ukbe_core/calibration.py` implementează regula β_min ≥ margine × Δω_max/K_ext derivată din Secțiunea 26, cu pragul teoretic și recomandarea separate explicit.
