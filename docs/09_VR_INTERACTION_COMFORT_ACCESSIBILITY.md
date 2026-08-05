# VR-interaktion, komfort og tilgængelighed

## Input

- Touch controllers er obligatorisk baseline.
- Ingen håndtracking i gaveversionen.
- Standard action maps: Gameplay, UI, Debug.
- Dominant hånd kan vælges; kritiske handlinger må udføres med begge hænder.

## Locomotion

Default:

- Teleportation.
- Snap turn 30°.
- Vignette ved valgfri smooth locomotion.
- Ingen forced camera movement.
- Korte transitions mellem action-zoner kan bruge fade.

Valgfrit:

- Continuous move.
- Smooth turn.
- Snap turn 15/30/45°.

## Fysisk rum

- Designet til stationary/roomscale uden krav om stor plads.
- Alle nødvendige objekter kan tilgås i ca. 0,6-1,6 meters højde efter kalibrering.
- Ingen påkrævet knælen.
- Gulvobjekter kan “summones” eller hæves til komfortabel højde.
- Boundary/guardian respekteres; spillet beder ikke brugeren gå fysisk langt.

## Reach og snap

- Interaktionscolliders er større end modeller.
- Hover feedback før grip/release.
- Snap zones bruger magnetisk preview.
- Tohåndsobjekter tillader forskellig armlængde og siddende spillere.
- Timeout/hint efter 8-10 sekunder uden fremdrift.

## Haptics

- Kort pulse ved hover-confirm.
- Stærkere, men kort feedback ved fastgørelse, brud og værktøjsslag.
- Ingen vedvarende kraftig haptik.
- Haptik har intensitetsindstilling og kan deaktiveres.

## UI

Primært diegetisk:

- Armbånd til personstatus.
- Lejrbål/objektstatus i verden.
- Fysisk planlægningskort.
- Radio og vejrtegn.

Ikke-diegetisk UI bruges til:

- lobby,
- komfort,
- pause,
- reconnect,
- undertekster,
- fejlmeddelelser.

## Undertekster

- Al vigtig voice har tekst.
- Speaker label og retningsindikator.
- Størrelse: normal/stor/ekstra stor.
- Baggrundsopacitet justerbar.
- Ingen vigtig information udelukkende via lyd.

## Farve og signaler

- Farve kombineres med form/ikon/position.
- Rød/grøn må ikke være eneste success/fail-signal.
- Stormeffekter må ikke reducere kontrast så meget, at snap-zoner forsvinder.

## Komforttest

Spillere rapporterer efter 15/30/45 min:

- kvalme,
- øjentræthed,
- arm/skuldertræthed,
- forvirring,
- frustration over reach.

En sekvens fejler komfortgate, hvis flere testere rapporterer moderat ubehag, selv om framerate er korrekt.

## Onboardingsekvens

1. Se og peg på partner.
2. Teleportér få meter.
3. Grib en let genstand.
4. Løft tung kasse sammen.
5. Tænd ild med to roller.
6. Læg første indsatsmarkør.

Ingen separat “tutorial room”. Læring foregår i scenariet.

## Pause og safety

- Hver spiller kan bede om pause.
- En kort diegetisk countdown stopper action sikkert.
- Ved headset removal/standby går session i reconnect-safe state.
- “Reset position” og “Return object” er altid tilgængelige.
