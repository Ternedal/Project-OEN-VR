# Project OEN — Unity First-Playable Audio Assembly

## Purpose

The production audio remains split into independent authored/environmental lanes for provenance and QA. For Unity integration, CI also stages one combined first-playable pack under the exact folder tokens expected by `ProjectOenAudioImportPostprocessor`.

Current combined scope:

- 65 authored UI/status WAVs
- 66 authored gameplay-feedback/stinger WAVs
- 14 authored adaptive-music candidate WAVs
- 15 public-domain/CC0 environmental candidate WAVs
- **160 WAV files total**
- **45 populated canonical runtime events**

This does not fabricate the remaining production events. Missing Foley, reviewed tarp/Amazon material and other not-yet-produced events stay missing until real source material exists.

## CI artifact

Audio Validation builds:

`oen-unity-first-playable-audio-v1`

The ZIP is intended to be extracted at the Unity project root. It contains:

```text
Assets/
  ProjectOen/
    Audio/
      2D/
        OneShots/
        Compressed/
        Streaming/
      Spatial/
        OneShots/
        Streaming/
FIRST_PLAYABLE_MANIFEST.csv
README.txt
```

The path tokens are functional, not decorative:

- `2D` preserves source channel layout and uses non-spatial playback defaults.
- `Spatial` forces mono in the Project OEN import postprocessor.
- `OneShots` selects ADPCM + Decompress On Load.
- `Compressed` selects Vorbis + Compressed In Memory.
- `Streaming` selects Vorbis + Streaming.

All imported source audio is forced to 48 kHz by the importer.

## Unity import workflow

1. Download `oen-unity-first-playable-audio-v1` from the current green Audio Validation run.
2. Extract the ZIP at the Unity project root.
3. Allow Unity to finish importing `Assets/ProjectOen/Audio/**`.
4. Run:

   `Project Oen > Audio > Build First-Playable Definitions + Catalog`

The Editor builder then:

- scans canonical numbered clips (`AudioEventId_01.wav`, etc.);
- ignores non-canonical AudioClips rather than guessing;
- groups variations deterministically by canonical `AudioEventId`;
- creates missing `AudioEventDefinition` assets in `Assets/ProjectOen/Audio/Definitions`;
- updates clip membership on existing definitions;
- preserves existing designer playback tuning on already-created definitions;
- writes stable numeric enum values, including canonical Injury/ColdWet IDs rather than legacy alias names;
- routes new definitions to matching mixer groups when a matching Project OEN mixer exists;
- creates/updates `Assets/ProjectOen/Audio/Definitions/AudioCatalog.asset`;
- sorts catalog entries by stable numeric runtime ID.

Run:

`Project Oen > Audio > Audit First-Playable Clip Coverage`

for a per-event imported-variation report.

## Current coverage

The v1 pack should stage exactly 160 WAV files across 45 unique runtime events. The staging script fails closed if either count drifts unexpectedly.

The remaining 70 runtime events are not errors by themselves. They represent production work that has not yet produced approved source clips.

## Quality state

The combined Unity pack is an integration artifact, not a mastering claim.

- authored UI/status: deterministic authored source
- authored gameplay/stingers: deterministic authored source
- adaptive music: `candidate-headset-listen`
- environmental material: candidate assets pending listening/loop/mix approval

Physical Unity import/compile, in-scene listening and Quest 2 headset/performance validation remain release gates.
