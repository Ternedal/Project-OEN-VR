# ProjectOen.Audio

Unity audio-binding for Øen.

## Placement in the real Unity project

Mirror these files under:

`Assets/ProjectOen/Scripts/Audio/`

Audio source assets themselves belong under:

`Assets/ProjectOen/Audio/`

The repository stores this module because the full Unity project is maintained outside the repo, matching the existing `src/unity/App` convention.

## Architecture

- `AudioEventId`: stable typed runtime IDs. Never renumber existing values.
- `AudioEventDefinition`: ScriptableObject definition data: clips, mixer route, spatial settings and randomization.
- `AudioCatalog`: collection of event definitions.
- `AudioService`: scene-owned, pooled one-shot playback service. It is intentionally **not** a singleton.
- `AudioLoopEmitter`: scene component for persistent physical emitters such as campfire, rain-on-tarp and rope/tarp ambience.

Gameplay code depends on `IAudioService`, not concrete clip paths.

## Quest profile

Baseline:
- 48 kHz source WAV.
- Mono for local 3D one-shots and emitters.
- Stereo for non-spatial beds/music.
- Long ambience/music loops: Vorbis + Streaming.
- Short repeated SFX: ADPCM + Decompress On Load.
- Pool size begins at 24 one-shots and must be profiled on Quest 2 before increasing.
- No convolution reverb or expensive runtime DSP in the baseline profile.

## Status

This change adds architecture + production manifest only. It does **not** pretend that the final mastered recordings exist yet.
