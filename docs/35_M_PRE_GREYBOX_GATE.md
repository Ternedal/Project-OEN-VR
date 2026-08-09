# M-Pre — greybox-gate for kernehypotesen

**ADR-022 · PO-110 · 10-20 timer · ingen VR, intet netværk, ingen art**

## 1. Hvad gaten skal afgøre

Hele produktet står på én antagelse:

> Når to spillere skal fordele fire indsatsmarkører på for få opgaver, opstår der **diskussion** — de
> forhandler, argumenterer og fortryder. De administrerer ikke bare en liste.

Er antagelsen forkert, er alt bygget ovenpå den spildt: VR-interaktion, netværk, storm, content. Den
bevises i dag først i M3, efter ~200 timers platform- og netværksarbejde. Denne gate flytter beviset frem
til noget, der kan gøres på et køkkenbord på en aften.

**Gaten måler ikke, om spillet er sjovt.** Den måler én ting: om fordelingsvalget er interessant nok til at
bære et helt spil.

## 2. Hvad der IKKE indgår

Fristelsen er at teste hele oplevelsen. Lad være — så måler du noget andet.

- Ingen VR, intet headset.
- Ingen netværkskode.
- Ingen art, lyd eller stemning.
- Ingen fortælling ud over den ene sætning, der sætter scenen.
- Ingen af Stormnattens faktiske tal. Brug dem herunder.

## 3. Testere

**To personer, samtidig, i samme rum.** De skal kunne tale sammen.

- **Ikke gavemodtageren.** Det er hele pointen med at teste på nogen andre — du bruger overraskelsen én
  gang, og en playtest er ikke det rigtige sted at bruge den.
- Brætspilsvante venner er gode nok. Du tester en mekanik, ikke en personlig oplevelse.
- Mindst **tre sessioner** med mindst **to forskellige par**. Ét par kan være tilfældigt enige eller
  tilfældigt skænderiske.

Hver session: 30-40 minutter inkl. snak bagefter.

## 4. Materialer

Alt kan skrives i hånden på et kvarter.

| Materiale | Antal | Indhold |
|---|---|---|
| Markørbrikker | 4 | Hvad som helst ens — mønter, klodser, papirlapper |
| Opgavekort | 6 | Én opgave pr. kort, se §5 |
| Statusark | 1 | Fire spor: **Mad**, **Ly**, **Helbred**, **Signal** — hver 0-5 |
| Dagsark | 3 | Ét pr. dag: hvad blev valgt, hvad blev udfaldet |
| Terning | 1 | d6 til udfald |

## 5. Opgavekortene

Seks opgaver, fire markører. **Knapheden er hele mekanikken** — det skal gøre ondt at vælge fra.

| # | Opgave | Kræver | Ved succes | Ved fiasko |
|---|---|---|---|---|
| 1 | Skaf mad | 1 markør | Mad +2 | Mad +0, Helbred −1 |
| 2 | Forstærk ly | 2 markører | Ly +3 | Ly +1 |
| 3 | Hold bål | 1 markør | Helbred +1, Signal +1 | Helbred −1 |
| 4 | Byg signalbål | 3 markører | Signal +4 | Signal +1 |
| 5 | Behandl skade | 1 markør | Helbred +2 | Helbred +0 |
| 6 | Udforsk kysten | 2 markører | Vælg selv +2 på ét spor | Helbred −2 |

**Udfald:** slå d6 pr. igangsat opgave. 1-2 = fiasko, 3-6 = succes. Er opgaven bemandet med **én markør
mere** end krævet, lykkes den på 2-6.

Den sidste regel er vigtig: den giver spillerne noget at forhandle om ud over "hvem gør hvad".

## 6. Spillets gang

1. **Dag 1-3.** Hver dag: fordel de fire markører på opgaver, slå udfald, opdatér statusarket.
2. **Efter dag 3 kommer stormen.** Læs højt: *"Stormen rammer i nat. Den tester jeres ly, jeres helbred og
   om nogen kan se jer."*
3. **Stormen afgøres** af de tre spor: Ly ≥ 6, Helbred ≥ 4 og Signal ≥ 5 → I bliver reddet. Ellers ikke.
4. Fortæl **ikke** stormens tærskler på forhånd. Sig kun, at alle tre spor betyder noget. Usikkerheden er
   det, der skaber uenighed om prioriteringen.

Start-status: alle spor på 2.

## 7. Hvad du måler

Sæt en telefon til at optage lyd, eller sæt streger på et papir. Du skal bruge tal, ikke fornemmelser.

| Mål | Sådan måles det | Grøn |
|---|---|---|
| **Forhandlingstid** | Sekunder brugt på at tale om fordelingen, pr. dag | Median ≥ **45 sek/dag** |
| **Uenighed** | Antal dage hvor de to foreslår forskellig fordeling | ≥ **1 pr. session** |
| **Skiftede mening** | Antal gange nogen forlader sit eget forslag efter et argument | ≥ **2 pr. session** |
| **Fortrydelse** | Nævner de efter stormen et valg, de ville have gjort anderledes? | Ja |
| **Administration** | Spørger de "hvad skal jeg gøre?" frem for "hvad skal *vi* prioritere?" | Nej |

Sidste række er den vigtigste. Hvis begge spillere hurtigt bliver enige og bare eksekverer, er hypotesen
faldet — uanset hvor hyggelige de synes, det var.

## 8. Gate-kriteriet

**Grønt:** mindst **to af tre sessioner** er grønne på forhandlingstid, uenighed og "ingen administration".

**Rødt:** alt andet.

### Ved rødt

Gå ikke videre til M1. Kerneloopet skal redesignes først. De mest sandsynlige knapper, i rækkefølge:

1. **Færre markører end opgaver kræver** — skru knapheden op, ikke ned.
2. **Skjult information** — hver spiller kender én ting, den anden ikke gør. Tvinger snak.
3. **Asymmetriske markører** — de fire er ikke ens; nogle duer kun til noget.
4. **Synligt tradeoff** — vis eksplicit hvad et spor koster, når det forsømmes.

Kør gaten igen efter ændringen. Den koster en aften.

### Ved grønt

- Luk OQ-006 og OQ-007 i `docs/19`.
- Nedskalér PO-039 til ren genverifikation i VR.
- Notér de faktiske tal i denne fil under §10, og gå videre til M1.

## 9. Hvorfor tærsklerne ser ud, som de gør

De er sat lavt med vilje. 45 sekunders forhandling om ét valg er ikke meget — men det er nok til at skelne
*diskussion* fra *afkrydsning*. En høj tærskel ville risikere at forkaste en mekanik, der virker fint, når
den får VR-kroppen og stormen med. Gaten skal fange den **katastrofale** fejl, ikke finjustere balancen.

Tallene i §5 og §6 er heller ikke Stormnattens rigtige tal. De er valgt, så tre dage kan spilles på 20
minutter, og så det er umuligt at få alle tre spor grønne. Bliver testen for nem, mister valget sin brod.

## 10. Resultat

Udfyldes når gaten er kørt.

| Session | Dato | Testere | Forhandlingstid (median) | Uenige dage | Skiftede mening | Fortrydelse | Administration | Grøn? |
|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | |
| 2 | | | | | | | | |
| 3 | | | | | | | | |

**Samlet resultat:** `GRØNT` / `RØDT` — _udfyldes_

**Noter og observationer:**

_Skriv især det, der overraskede. Det er som regel dér, designet gemmer sig._
