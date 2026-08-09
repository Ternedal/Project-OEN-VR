# Build, release og drift

## Versionsformat

`MAJOR.MINOR.PATCH+BUILD`

Eksempel: `0.4.0+128`.

Separat:

- `NetworkProtocolVersion`.
- `SaveSchemaVersion`.
- `ContentVersion`.

Semver alene må ikke bruges til handshake.

## Branches

- `main`: altid kendt stabil.
- `develop`: integrationsbranch, hvis nødvendig; alternativt trunk-based med korte branches.
- `feature/<id>-<name>`.
- `fix/<id>-<name>`.
- `release/<version>`.
- `legacy/q1-<version>` kun hvis package manifest divergerer.

## Build artifacts

Hver build arkiverer:

- APK.
- symbols/mapping.
- package lock.
- git commit.
- build profile.
- content hash.
- release notes.
- test summary.

## Signing

- Keystore uden for repo.
- Backup i sikker password manager/storage.
- Samme signing identity for opdateringer på samme kanal/device.
- Development key må ikke blive release key ved et uheld.

## CI

Minimum:

- YAML/JSON/schema validation.
- Duplicate content IDs.
- EditMode tests.
- Static checks.
- Build metadata generation.

Senere:

- Android build via licensed/self-hosted runner.
- Automated smoke install hvis lab hardware findes.

## Releasekanaler

### Development

ADB/MQDH sideload på alle devices.

### Alpha

Quest 2/3 gift test. Invite-only. Brugere får app i Library/My Preview Apps.

### Quest 1 - udgået kanal

Quest 1 er ikke en releasekanal (`DROP_Q1_RUNTIME`, 2026-08-08). Genoptages en frossen sideload-demo,
kræver den sin egen build, sin egen guide og en ny ADR - den deler ikke compatibility hash med hovedbuildet.

## Release checklist

- Versioner incremented.
- Content/schema/protocol hash korrekt.
- Clean install + upgrade test.
- Save migration test.
- Q2/Q3 matrix gennemført.
- P0/P1 = 0.
- Known issues.
- Rollback APK tilgængelig.
- Private assets verificeret og ikke i repo/logs.

## Observability

Development logs:

- session ID (random/anonym).
- build/device/profile.
- phase transitions.
- command failures.
- authority changes.
- reconnect attempts.
- state checksum mismatch.
- performance samples.

Gift release kan gemme logs lokalt og eksportere manuelt. Ingen cloud analytics kræves.

## Incident playbook

### Kan ikke joine

1. Sammenlign protocol/content hash.
2. Check Photon status/region.
3. Opret ny code.
4. Export logs.

### Permanent object desync

1. Pause scenario.
2. Trigger authoritative snapshot/resync.
3. Hvis mismatch fortsætter: resume checkpoint.

### Crash efter update

1. Rollback build.
2. Bevar save backup.
3. Reproducer med development symbols.

## Sideload-guidekrav (kun hvis en frossen Q1-demo genoptages)

Ikke en aktiv leverance. PO-098 er droppet med `DROP_Q1_RUNTIME`.

- Skridt-for-skridt med MQDH eller adb.
- Developer mode forudsætninger.
- Hvordan update/uninstall virker.
- Kendte begrænsninger.
- Guide testet af ikke-udvikler.
