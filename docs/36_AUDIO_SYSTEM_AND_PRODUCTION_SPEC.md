# Audio system og produktionsspecifikation

Status: implementeringsgrundlag v1  
Målplatform: Quest 2 baseline, kompatibel med Quest 1-test og Quest 3  
Runtime: Unity 6000.4.10f1

## 1. Formål

Audio skal gøre Øen læsbar uden at overdøve VR-rummet. Repoets eksisterende retning er styrende:
zonebaseret 3D-ambience, vindlag, tarp/reb som gameplay-feedback, lejrbål som status og dyr,
der ofte høres før de ses.

Lydsystemet må derfor ikke være en samling tilfældige `AudioSource`-referencer. Gameplay bruger
typed event IDs; fysiske loop-kilder ejer deres egen emitter; definitioner ligger i ScriptableObjects;
runtime-state ligger i en scene-owned service.

## 2. Leveranceomfang

Manifestet `content/audio/audio_asset_manifest.csv` indeholder:

- **115 audio events**
- **788 planlagte source-variationer**
- ambience, vejr, fauna, materialer, footsteps, player movement, crafting, UI, status, musik og stingers
- præcis filename-pattern, spatialitet, mixer-route, distance, randomisering og Unity-importstrategi

Det er med vilje mere komplet end MVP-behovet. Produktionsstatus starter som `production-needed`, så
man kan udfylde biblioteket gradvist uden at ændre runtime API'et.

## 3. Navngivning

Repoets prefix-konvention `SFX_` anvendes.

Eksempel:

`SFX_ENV_Fire_Pop_01.wav`  
`SFX_ENV_Fire_Pop_02.wav`  
...  
`SFX_ENV_Fire_Pop_14.wav`

Musik bruger `MUS_`, stingers `STG_`.

Eksisterende enum-værdier må aldrig renummereres efter at definitions-assets er serialiseret i Unity.

## 4. Mixer-busser

```text
Master
├── Ambience
├── Weather
├── Nature
├── Environment
├── Player
├── Interaction
├── Crafting
├── UI
├── Music
└── Stinger
```

Anbefalet headroom i content pass: normal peaks omkring -6 dBFS; Master limiter er safety-net,
ikke loudness-værktøj.

## 5. Spatial audio

### 3D mono
Bruges til:
- bål
- tarp og reb
- footsteps
- dyr og lokale natur-events
- pickup/drop/materialeinteraktion
- crafting/building i verden

### 2D/stereo
Bruges til:
- brede ambience beds
- global storm/rain bed
- UI
- status cues
- musik og stingers

Der må ikke bages reverb ind i korte 3D one-shots, hvis refleksionen skal følge rummet.

## 6. Dynamisk ambience

Ambience skal sammensættes i lag i stedet for ét stort masterloop.

Eksempel dag/strand:

`OceanFar + OceanNear + CoastalWind + PalmCanopy + randomized ShoreWash/Birds`

Eksempel jungle/nat:

`NightBed + CanopyWind + randomized Cicadas/Frogs/Rustles`

Storm:

`StormWind + RoughOcean + Rain + local RainOnTarp + randomized WindGust/Thunder`

Vejr/game-state ændrer gain på lag; der skiftes ikke hårdt mellem komplette soundscapes.

## 7. Gameplay-signaler

Vigtige cues skal fortsat have visuel feedback.

Prioriterede auditive gameplay-cues:
1. reb/tarp under belastning
2. lejrbål lavt/aktivt/ændret
3. objective/discovery
4. fare/status
5. crafting success/fail
6. dyr i nærheden før visuel reveal

## 8. Unity-importprofil

| Type | Channels | Compression | Load |
|---|---|---|---|
| 3D one-shot | Mono | ADPCM | Decompress On Load |
| korte UI/status | Mono/stereo | ADPCM | Decompress On Load |
| lange ambience loops | Stereo | Vorbis | Streaming |
| vejr beds | Stereo | Vorbis | Streaming |
| musik | Stereo | Vorbis | Streaming |
| stingers | Stereo | Vorbis | Compressed In Memory |

48 kHz er master/source-format. Kvalitetsniveauet skal måles på Quest 2 før evt. nedjustering.

## 9. Runtime-arkitektur

`ProjectOen.Audio` følger repoets dependency-regler:

- Gameplay/scene wiring kalder `IAudioService`.
- `AudioService` er scene-owned og ikke singleton.
- Service bygger runtime lookup fra `AudioCatalog`.
- `AudioEventDefinition` er immutable definitionsdata under runtime.
- One-shots bruger et fast source-pool for at undgå GameObject churn.
- Persistente loops bruger `AudioLoopEmitter` med egen `AudioSource`.

V1 stjæler ikke voices, hvis poolen er fuld; den afviser nye one-shots. Det er bevidst simpelt og
profilerbart. Voice stealing kan tilføjes senere med en eksplicit prioritetspolitik.

## 10. Quest-budget og QA

Før M1/M2 content vokser:
- profilér 24 samtidige one-shot sources på Quest 2
- kontrollér streaming spikes ved storm + musik
- test at footsteps ikke maskerer dialog/radio
- test mono 3D-kilder med hovedrotation og afstand
- test to samtidige spilleres relevante lokale/world cues
- undgå at netværkssynkronisere kosmetiske audio variationer; synkronisér gameplay-eventet, vælg lokal variant

## 11. Produktionsrækkefølge

**P0 vertical slice**
- beach ocean near/far
- coastal wind
- jungle day/night
- fire idle/low/pop/add wood
- tarp flap/tension
- rope tighten/creak
- 7 footsteps-materialer
- pickup/drop/build/craft success/fail
- objective/discovery/danger
- light/heavy rain + storm wind + thunder
- minimal camp/warning/storm/finale musik

**P1**
- fuld fauna-variation
- alle materialer
- shelter interior beds
- flere storm transitions
- polished UI/radio family

**P2**
- sjældne world one-shots
- ekstra stingers
- yderligere variationer efter repetitionstest

## 12. Acceptance criteria for audio foundation

- Module compiles in Unity 6000.4.10f1 after mirroring into `Assets/ProjectOen/Scripts/Audio/`.
- Ingen runtime singleton.
- Duplicate IDs giver tydelig editor/runtime error.
- Manglende event/clip fejler uden exception.
- One-shot playback allokerer ikke et nyt GameObject per event efter `Awake`.
- Loop emitter stopper ved disable.
- Manifest og enum har samme 115 events.
- Endelige optagelser/mastere er **ikke** markeret som færdige før de faktisk er produceret og lyttetestet.
