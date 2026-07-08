# Rezonanța Aparentă din Buclele de Feedback Adaptive: O Bifurcație Kuramoto Deghizată

**Autor:** Mihai Roșca
**Verificare independentă și redactare:** realizate prin sesiuni successive cu multiple instanțe de asistenți AI, cu cod rulat ca arbitru la fiecare pas
**Status:** Rezultat empiric confirmat pe sistem izolat și pe sistem complet; mecanism cauzal complet caracterizat
**Versiune:** 1.0 — extras de sine stătător din REAI v0.7.2, Secțiunile 25-26

---

## Rezumat

Într-un sistem de sincronizare Kuramoto cu cuplaj extern adaptiv (α/β dinamic, guvernat de un indice de coerență RSI), un parametru de planșeu minim al cuplajului extern (β_min) arată un vârf neașteptat de sensibilitate la dezaliniere, în jurul valorii β_min≈0.12–0.15, măsurat cu o fereastră scurtă de observare. Două explicații intuitive — rezonanță armonică forțată și "amortizare critică" a buclei de feedback — au fost propuse, testate direct și respinse, una dintre ele demascată ca bazată pe o coloană de date fabricată, nu măsurată. Mecanismul real e o **bifurcație de blocare de fază de tip Adler** (echivalentă cu tranziția SNIC din teoria oscilatorilor cuplați), cu **încetinire critică** lângă prag — fenomen standard în dinamica neliniară, nu specific acestui sistem. Forma exactă a divergenței timpului de relaxare (τ~(K_eff−Δω)^(−1/2)) e confirmată atât pe ecuația Adler izolată, cât și pe sistemul complet de 30 de oscilatori, cu acord de 98.5–99.6% între predicție și măsurătoare.

---

## 1. Fenomenul observat

Într-un grid de calibrare (β_min ∈ [0.05, 0.30], testat pe multiple seed-uri), sensibilitatea sistemului la o schimbare reală de intenție (măsurată ca adâncimea dip-ului de coerență externă într-o fereastră fixă de observare) **nu crește monoton** cu β_min:

| β_min | Sensibilitate (medie, 10 seed-uri) |
|---|---|
| 0.05 | 0.29 |
| 0.10 | 0.47 |
| 0.12 | 0.61 |
| 0.15 | 0.59 |
| 0.18 | 0.40 |
| 0.20 | 0.33 |

Vârful, confirmat de trei ori independent, cu metodologii ușor diferite, a cerut o explicație cauzală — nu doar o observație descriptivă.

## 2. Două explicații respinse

**Ipoteza 1 — rezonanță armonică forțată.** Propunerea: sistemul, modelat ca oscilator amortizat, ar intra în rezonanță când frecvența ferestrei RSI (T=50 pași) se aliniază cu frecvența schimbărilor de intenție. **Testată direct**, cu exact protocolul pe care îl cerea (forcing periodic, patru perioade diferite): amplitudinea de răspuns scade monoton cu β_min, în tot intervalul relevant. Niciun vârf, nicăieri. **Respinsă.**

**Ipoteza 2 — "amortizare critică" a buclei RSI-β.** A doua propunere venea cu un tabel de "verificare empirică" (răspuns tranzitoriu vs. staționar, pe șase valori de β_min). Verificare directă a arătat că valorile din coloana "răspuns staționar" erau construite algebric (aproximativ 1 − tranzitoriu), nu măsurate independent — confirmat prin măsurarea reală a coerenței externe în regim stabil, constant la ~0.99 pentru toate valorile de β_min, nu variind cum pretindea tabelul. **Respinsă, cu o coloană de date fabricate identificată explicit.**

## 3. Mecanismul real: bifurcație Adler

Reducerea mean-field a sistemului (N oscilatori interni puternic sincronizați ≈ un singur oscilator efectiv, cuplat cu θ_uman) dă ecuația Adler standard — aceeași familie matematică din teoria clasică a sincronizării (Kuramoto 1984; Strogatz 2000):

$$\frac{d\psi}{dt} = -\Delta\omega - K_{eff}\sin(\psi), \qquad \psi = \theta_{mean}-\theta_{uman}, \qquad K_{eff}=\beta \cdot K_{ext}$$

**Regim blocat** (K_eff > |Δω|): punct fix stabil ψ* = −arcsin(Δω/K_eff), timp de relaxare:
$$\tau_{relax} = \frac{1}{\sqrt{K_{eff}^2-\Delta\omega^2}}$$

**Regim alunecat** (K_eff < |Δω|): fără punct fix, alunecare continuă, cu perioadă:
$$T_{slip} = \frac{2\pi}{\sqrt{\Delta\omega^2-K_{eff}^2}}$$

Ambele formule **diverg la K_eff=Δω** — încetinire critică la bifurcație, fenomen bine documentat pentru tranziții de tip SNIC (saddle-node on invariant circle), nu un artefact al acestui sistem particular.

**Interpretarea vârfului:** lângă pragul de blocare, tranzitoriile devin arbitrar de lungi. O măsurătoare cu fereastră fixă (cum era protocolul original) vede dip-uri mai mari în vecinătatea pragului — nu la prag exact, ci într-o regiune din jurul lui — pentru că sistemul "ezită" mai mult între a se bloca și a aluneca. Vârful observat empiric e umbra acestei încetiniri critice, nu un fenomen distinct.

## 4. Verificare empirică, trei niveluri

**Nivel 1 — pragul de blocare, pe sistemul complet (30 oscilatori).** Sub K_eff critic: alunecare permanentă (sute de treceri prin decoerență completă). Peste prag: blocare definitivă (zero treceri). Pragul empiric (β_min≈0.25) apropiat de predicția analitică simplă (β_min=0.20), diferența explicată de bucla suplimentară RSI-β care ridică β peste planșeu când coerența scade.

**Nivel 2 — forma exactă, pe ecuația Adler izolată** (re-verificat acum, în sesiunea curentă):

$$\text{Exponent măsurat: } -0.5009 \quad (\text{predicție analitică: } -0.5)$$

**Nivel 3 — forma exactă, pe sistemul complet** (re-verificat acum, în sesiunea curentă):

| β_min | K_eff | τ prezis | τ măsurat | raport |
|---|---|---|---|---|
| 0.35 | 0.525 | 2.3210 | 2.2855 | 0.9847 |
| 0.40 | 0.600 | 1.9245 | 1.9050 | 0.9899 |
| 0.50 | 0.750 | 1.4548 | 1.4466 | 0.9944 |
| 0.70 | 1.050 | 0.9938 | 0.9903 | 0.9965 |
| 1.00 | 1.500 | 0.6804 | 0.6778 | 0.9962 |

Raport măsurat/prezis între 0.985 și 0.996 — practic exact, diferența mică atribuibilă faptului că N=30 oscilatori nu sunt perfect echivalenți cu un singur oscilator ideal (răspândire reziduală mică de frecvențe interne).

## 5. Doi bugi de verificare, găsiți și corectați în timpul testării

Prima încercare de verificare a Nivelului 3 a arătat o discrepanță majoră (raport între 4.3× și 14.5×, complet nefizică). În loc să fie raportată ca "limită reală a modelului mean-field", discrepanța a fost investigată:

**Bug 1 — înfășurare de fază incorectă.** ψ era calculat ca diferență între o valoare înfășurată (θ_mean, întotdeauna în (−π,π], din `np.angle()`) și una neînfășurată, crescândă nemărginit (θ_uman). Corectat prin înfășurarea explicită a diferenței.

**Bug 2 — semn greșit în convenția Δω.** Convenția din simulare dădea dψ/dt = −Δω − K_eff·sin(ψ), nu +Δω, din cauza direcției reale a cuplajului implementat, nu o alegere arbitrară de convenție.

Cu ambele corectate, acordul de 98.5–99.6% a apărut imediat. Distincția dintre "am găsit o limită reală a modelului" și "am găsit o eroare în verificarea proprie" a fost verificată explicit, nu presupusă — disciplina care a permis identificarea corectă.

## 6. Recomandare de calibrare, revizuită

Regula utilizabilă pentru orice implementare care folosește acest mecanism:

$$\beta_{min} \geq 1.5 \times \frac{\Delta\omega_{max}}{K_{ext}}$$

nu o constantă fixă (β_min=0.14, cum s-a propus inițial, empiric, fără acest mecanism). Lângă prag, încetinirea critică anulează practic beneficiul planșeului — o marjă de siguranță explicită față de bifurcație e necesară, nu doar o valoare care "a funcționat" pe un set limitat de teste.

## 7. Limitări, spuse direct

Acest rezultat e complet caracterizat **pe sistemul redus** (Kuramoto + cuplaj extern adaptiv). El **nu** demonstrează nimic despre:
- dacă proxy-urile folosite pentru a estima "intenția umană" (timp de răspuns, rata de corecție) au vreo legătură reală cu o intenție umană reală (Problema P1, temelia întregului framework REAI, rămasă complet netestată dincolo de acest model)
- dacă fenomenul se transferă la sisteme de aliniere AI reale (RLHF, DPO) — legătura rămâne analogie, nu demonstrație

Ce demonstrează, riguros: un mecanism cunoscut din teoria sincronizării (bifurcație Adler/SNIC, încetinire critică) explică complet un fenomen empiric care inițial părea specific și misterios, iar procesul de verificare — inclusiv respingerea a două explicații plauzibile și corectarea a două erori proprii de testare — e documentat integral, nu curățat retroactiv.

---

## Referințe

- Kuramoto, Y. (1984). *Chemical Oscillations, Waves, and Turbulence*. Springer.
- Strogatz, S. (2000). *From Kuramoto to Crawford: exploring the onset of synchronization in populations of coupled oscillators*. Physica D.
- Standard theory of SNIC bifurcations and critical slowing down — orice manual de dinamică neliniară (ex. Strogatz, *Nonlinear Dynamics and Chaos*).

---

*Document extras din REAI v0.7.2 (Secțiunile 25-26), ca lucrare de sine stătătoare, la propunerea explicită de a separa rezultatele publicabile de framework-ul mai larg, nevalidat.*
*Proprietate intelectuală: Mihai Roșca*
