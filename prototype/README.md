# Prototype

## `m0a-openxr-smoke/`

M0a-pakken: alt Anders skal bruge for at besvare det ene spørgsmål, resten af projektet venter på — **starter og tracker Unitys OpenXR-provider på Quest 1?**

- `RUNBOOK.md` — trin for trin fra tomt Unity-projekt til aflæst resultat.
- `RESULTAT.md` — skema til svaret. Evidensen bag CR-002 og ADR-019.
- `files/` — drop-in kildefiler, manifest-patch, pakkeliste og installationsscript.

Kildefilerne i `files/` er **ikke kompileret**. Der findes ingen Unity Editor i det miljø, de blev skrevet i. Meld straks, hvis Editoren giver en compile-fejl.

## M0b — det rigtige Unity-projekt

Oprettes først, når M0a er besvaret, og editorversionen dermed er afgjort. M0b skal bevise:

1. samme gameplaykode og scenarioformat på Quest 1, Quest 2 og Quest 3,
2. controllertracking, grab og comfort locomotion,
3. privat Photon-session med compatibility handshake,
4. head/hand replication,
5. fælles kinematic tung-kasse-interaktion,
6. signeret APK og BuildInfo,
7. 72 Hz i minimal scene på alle enheder i lanen,
8. dokumenteret package/graphics API matrix.

Hvis én package lock ikke kan starte på alle enheder, må kun manifests/lockfiles og platformadapters divergere. Gameplay, protocol, content og save schema skal fortsat være fælles. Kræver Quest 1 et andet XR-backend, er det ikke divergens — det er exit-kriteriet, jf. ADR-019.
