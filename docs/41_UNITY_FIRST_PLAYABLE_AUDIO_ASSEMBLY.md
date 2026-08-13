# Project OEN — Unity First-Playable Audio Assembly

## Purpose

The production audio remains split into independent authored/environmental lanes for provenance and QA. For Unity integration, CI stages one combined first-playable pack under the exact folder tokens expected by `ProjectOenAudioImportPostprocessor`.

Current combined scope:

- 65 authored UI/status WAVs
- 66 authored gameplay-feedback/stinger WAVs
- 14 authored adaptive-music candidate WAVs
- 28 Public Domain/CC0 environmental candidate WAVs
- **173 WAV files total**
- **47 populated canonical runtime events**

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

`FIRST_PLAYABLE_MANIFEST.csv` is not informational decoration. It is the authoritative staged-payload contract used by the Unity Editor tooling. Each row pins event ID, variation, source pack, Unity destination path, SHA-256 and byte count.

The path tokens are functional:

- `2D` preserves source channel layout and uses non-spatial playback defaults.
- `Spatial` forces mono in the Project OEN import postprocessor.
- `OneShots` selects ADPCM + Decompress On Load.
- `Compressed` selects Vorbis + Compressed In Memory.
- `Streaming` selects Vorbis + Streaming.

All imported source audio is forced to 48 kHz by the importer.

## Staging integrity

`tools/stage_unity_first_playable_audio.py` fails closed if:

- total staged WAV count differs from the expected current build;
- populated event count differs from the expected current build;
- two input packs attempt to produce the same canonical event/variation;
- two inputs attempt to write the same Unity destination;
- a filename is not a numbered canonical WAV shape.

The current CI expectation is exactly **173 WAV / 47 events**. The Unity Editor keeps a deliberately lower stable compatibility floor of **160 WAV / 45 events**, but it does not trust counts alone.

## Unity import workflow

1. Download `oen-unity-first-playable-audio-v1` from the current green Audio Validation run.
2. Extract the ZIP at the Unity project root. Keep `FIRST_PLAYABLE_MANIFEST.csv` at that root.
3. Allow Unity to finish importing `Assets/ProjectOen/Audio/**`.
4. Run:

   `Project Oen > Audio > Build First-Playable Definitions + Catalog`

Before the definition/catalog builder mutates generated assets, `ProjectOenAudioFirstPlayableManifestAudit` verifies:

- every manifested WAV exists;
- byte count matches the manifest;
- SHA-256 matches the manifest;
- each file has imported as an `AudioClip` with matching event/variation identity;
- event/variation and destination paths are unique;
- legacy Hunger/Thirst aliases cannot enter the current payload;
- there are no extra canonical WAVs under `Assets/ProjectOen/Audio` that are absent from the current manifest.

That last check prevents an old extraction from silently increasing runtime coverage with stale files.

The Editor builder then:

- consumes only manifest-verified clip rows rather than broadly trusting every imported clip;
- groups variations deterministically by canonical `AudioEventId`;
- creates missing `AudioEventDefinition` assets in `Assets/ProjectOen/Audio/Definitions`;
- updates clip membership on active definitions;
- clears clip membership from old definitions absent from the current staged manifest;
- rejects duplicate `AudioEventDefinition` IDs rather than choosing one arbitrarily;
- preserves existing designer playback tuning on active definitions;
- writes stable numeric enum values, including canonical Injury/ColdWet IDs rather than legacy alias names;
- routes new definitions to matching mixer groups when a matching Project OEN mixer exists;
- creates/updates `Assets/ProjectOen/Audio/Definitions/AudioCatalog.asset` from only the current manifested event set;
- sorts catalog entries by stable numeric runtime ID.

Run:

`Project Oen > Audio > Audit First-Playable Clip Coverage`

for a per-event imported-variation report backed by the same manifest/hash audit.

## Rerun safety

Old definition assets may remain on disk so playback tuning/history is not destructively erased. However, definitions absent from the current manifest have their `_clips` array cleared and are excluded from the runtime catalog and generated first-playable profiles.

Generated ambience/weather/music profile **membership** is synchronized on each one-click rebuild so newly available loop events appear and removed events disappear. Existing gain tuning is preserved for layers that are still valid. The generated runtime prefab itself remains preserved unless explicitly regenerated.

This distinction fixes the previous stale-state risk where an older generated profile could remain empty after new first-playable audio became available.

## Current coverage

The current v1 pack stages exactly **173 WAV files across 47 unique runtime events**. The remaining **68 runtime events** are not integration errors: readiness reporting assigns each to an explicit Foley, reviewed-field or field-source production lane, with zero unassigned missing events.

## Quality state

The combined Unity pack is an integration artifact, not a mastering claim.

- authored UI/status: deterministic authored source
- authored gameplay/stingers: deterministic authored source
- adaptive music: `candidate-headset-listen`
- environmental material: candidate assets pending listening/loop/mix approval

A green CI build proves staged bytes, provenance and software contracts. Physical Unity 6000.4.10f1 import/compile, in-scene listening and Quest 2 headset/performance validation remain production gates before this audio PR should be merged.
