# Multiplayer- og netværksspecifikation

## 1. Mål

To spillere skal kunne oprette en privat session, forbinde med join code, gennemføre hele scenariet og håndtere kortvarige afbrydelser uden permanent state corruption.

## 2. Valgt topologi

**Photon Fusion 2 Shared Mode** er førstevalg, fordi:

- sessionen har kun to klienter,
- VR-pose kan ejes lokalt,
- ingen dedikeret server ønskes,
- Fusion har officiel VR Shared-sample,
- Shared Mode undgår samme prediction/resimulation-kompleksitet som host/server til dette scope.

Risiko: Shared authority kræver disciplin ved ownership transfer og gameplay commands. Derfor ejer klienterne ikke frit kritisk scenariestate.

## 3. Roller

### Session Coordinator

Den første spiller, der opretter sessionen, vælges som logisk coordinator for:

- phase transitions,
- scenario seed,
- checkpoint trigger,
- event queue resolution.

Dette er en gameplayrolle oven på Shared Mode. **Foreslået beslutning (ADR-020, afventer ejeren):** der er ingen live overdragelse. Med to spillere findes ingen tredje klient at overdrage til — hvis coordinator forsvinder, er sessionen enten slut eller den anden klient er per definition ny coordinator. Ved coordinator-tab: pause, checkpoint-resume, ny session. Det er én kodesti i stedet for to og fjerner en klasse af desync-fejl. Checkpoint-stien skal bygges og testes alligevel.

### Player authority

Hver klient ejer:

- eget head/hand pose,
- lokal locomotion,
- input intents,
- lokale cosmetics.

### Interactable authority

- Små objekter: authority til den spiller, der griber først.
- Overdragelse sker kun ved release eller explicit handoff.
- Fælles/tunge objekter: separat `CoopObjectController` ejer state; begge sender hand targets.
- Missionkritiske objekter kan aldrig despawnes af klienten.

## 4. Session lifecycle

1. Create/Join.
2. Region selection eller best region.
3. Compatibility handshake.
4. Spawn player rigs.
5. Calibration complete.
6. Ready check.
7. Scenario load acknowledgement.
8. Start at synchronized timestamp.
9. Periodic state checksum.
10. Results and session close.

## 5. Compatibility handshake

Begge builds sender:

- semantic game version.
- network protocol version.
- scenario content hash.
- save schema version.
- platform profile.
- required feature flags.

Quest 2 og Quest 3 må spille sammen, hvis protocol/content/schema matcher. Grafikprofil må være forskellig.

## 6. Replikationskategorier

| Data | Frekvens/metode | Bemærkning |
|---|---|---|
| Head/hands pose | NetworkTransform-lignende, komprimeret | Interpolation, ikke save-state |
| Grab state | Reliable state/event | Object ID, hand, authority |
| Hand targets på coop object | Høj frekvens, komprimeret | Bruges af kinematic solver |
| Scenario phase | Reliable networked state | Coordinator-valideret |
| Resources/status | Networked properties + events | Lav frekvens |
| Weather seed/state | Seed + phase timestamps | Undgå at replikerer hver partikel |
| Audio cues | Event ID + timestamp | Lokal playback |
| Destruction/collapse | Sequence ID + seed/timestamp | Ikke rå rigidbody streams |

## 7. Commands

Klienten sender intents, ikke endelige resultater.

**Præciseret 2026-08-07.** `CompleteInteractionStepCommand` bar oprindeligt hele udfaldsinputtet — inklusive `Preparation` og `Penalty`. Det brød princippet i denne sektion: klienten fortalte reelt direktoren, hvor hårdt den skulle straffes, og en fejl i én klients måling ville forplante sig til det delte resultat.

Commanden bærer nu kun det, klienten alene kan måle: `PhysicalExecution` og `Cooperation`, begge fra coop-solverens quality samples. Direktoren udleder resten af autoritativ state:

- `Preparation` = indsatsmarkører placeret på handlingen ÷ dens kostpris (fra planen).
- `Penalty` = skader + træthed + scenariets egen modstand (vejr, hændelser).

Commands:

- RequestPlaceMarker.
- RequestGrab.
- RequestRelease.
- SubmitInteractionSample.
- RequestConfirmPlan.
- RequestUseItem.
- RequestPause.

Coordinator/gameplay authority validerer ressourcer, fase og tilladelser.

## 8. Two-player object handling

`CoopObjectController` state:

- Idle.
- HeldByOne.
- HeldByBoth.
- Stabilizing.
- LockedToTarget.
- Released/Failed.

Solveren kombinerer to hand targets og anvender:

- max velocity/rotation,
- damped midpoint,
- grip distance constraints,
- soft correction,
- local immediate hand feedback.

Network result er target pose og quality score, ikke ukontrolleret kraftsimulation.

## 9. Latency

Designmål:

- Spilbart ved 80-120 ms round trip.
- Lokale greb responderer samme frame.
- Remote avatar interpolation skjuler jitter.
- Samtidighedsvinduer på samarbejdshandlinger er mindst 300-500 ms, medmindre de er rytmiske og tydeligt telegrapherede.
- Ingen mekanik må kræve frame-perfect cross-client input.

## 10. Disconnect og reconnect

### Kort disconnect

- Scenario pauses diegetisk efter 2-3 sekunders manglende peer.
- Lokale farer fryses eller går i safe loop.
- Reconnect window: foreslået 90 sekunder. **Skal måles, ikke gættes (CR-009):** Quest går i standby få sekunder efter aftagning, så den hyppigste virkelige afbrydelse — "jeg tog headsettet af" — kan overskride vinduet og ramme den dyre sti. Mål faktisk standby → netværkstab på Q2/Q3 i M2 og sæt vinduet efter data.
- Returnerende klient får fuldt authoritative snapshot og scene acknowledgement.

### Lang disconnect

- Session går til checkpoint menu.
- Begge kan rejoin med samme code og resume.
- Hvis coordinator mangler, den anden må oprette resume-session fra gemt checkpoint.

### Standby/headset sleep

Behandles som disconnect. Testes specifikt, fordi Quest ofte går i standby.

## 11. State integrity

- Scenario state har monotonic revision.
- Periodisk checksum på kritiske værdier.
- Ved mismatch sender coordinator fuldt snapshot.
- Commands er idempotente via command ID.
- Completed interaction step kan ikke tælles to gange.

## 12. Voice

- Samlokal gaveversion kræver ikke in-game voice.
- Fjernspil kan i v1.1 bruge Photon Voice.
- Voice må ikke være nødvendig for netværksprotokollen.
- Der optages eller gemmes ingen tale.

## 13. Failure injection tests

- Drop 5 %, 10 % og burst packets.
- 150-250 ms latency.
- Authority transfer under grab.
- Coordinator disconnect under phase transition.
- Standby under loading.
- Duplicate confirm command.
- Mismatched scenario hash.
- Quest 2 reconnect til Quest 3-session.

## 14. Go/no-go-kriterium

Før contentproduktion:

- 10 gentagelser af fælles løft Q2↔Q3 uden permanent desync.
- 10 session create/join/leave/rejoin cycles.
- Coordinator disconnect giver enten vellykket handover eller kontrolleret checkpoint-resume; aldrig skjult divergens.
