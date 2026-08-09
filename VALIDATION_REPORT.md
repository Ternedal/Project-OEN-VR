# Valideringsrapport - PROJECT ØEN handoff v2.0

**Dato:** 2026-08-05  
**Resultat:** PASS  
**Formål:** Kontrollere at handoff-pakken kan åbnes, læses, valideres og overdrages uden kendte strukturelle fejl.

## Automatiske kontroller

- 6 JSON Schemas er syntaktisk gyldige under Draft 2020-12.
- 5 JSON-eksempler validerer mod deres respektive schemas.
- Alle YAML-filer i `.github/` og `config/` kan parses.
- Alle relative Markdown-links peger på eksisterende filer.
- DOCX- og XLSX-containere består ZIP-integritetstest.
- Master-PDF kan læses og indeholder 85 sider.
- Alle Mermaid-filer har en genkendelig diagramtype.
- Der blev ikke fundet signing keys, APK/AAB-filer eller åbenlyse private personaliseringsassets.
- `MANIFEST.json` matcher filstørrelser og SHA-256 checksums for payloaden.
- Backlog-workbooken indeholder 9 ark, 108 backlog-items, 44 P0-items og 1.447 estimerede timer.
- Workbook-formlernes nøgleområder blev inspiceret; der blev ikke fundet `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?` eller `#N/A`.

## Visuel QA

### Master DOCX/PDF

- DOCX blev renderet til 85 PNG-sider via den containeriserede LibreOffice-renderer.
- Alle sider blev gennemset samlet som kontaktark.
- Repræsentative sider med titel, brødtekst, testcases og JSON/code formatting blev inspiceret i fuld størrelse.
- Der blev ikke observeret clipping, overlap, manglende glyphs eller ødelagte tabeller.
- Den afledte PDF blev desuden renderet separat til 85 billeder.

### Backlog-workbook

- Dashboardet blev renderet via `artifact_tool`.
- KPI-blok, milepælstabel og timegraf er læsbare og uden synlige overlap.
- Status- og prioriteringskolonner har datavalidering og betinget formatering.

## Reproducerbar kontrol

Fra repositoryroden:

```bash
python -m pip install -r tools/requirements-validation.txt
python tools/validate_handoff.py
```

GitHub Actions-workflowen `.github/workflows/validate-handoff.yml` kører den samme validering ved push og pull request.

## Bevidste ikke-validerede forhold

Følgende kan ikke bevises af dokumentpakken og er derfor eksplicitte M0/M1-spikes:

- at Quest 2 og Quest 3 kan cross-playe stabilt under den endelige package-lane,
- at Photon Fusion Shared Mode leverer acceptabel jitter og authority-adfærd for tohånds-/fællesobjekter,
- at Stormnatten kan holde 72 Hz og memory/thermal-budget på Quest 2,
- at scenarioet reelt varer 30-45 minutter og holder begge spillere aktive mindst 70 % af action-tiden.

Disse punkter må ikke omtales som verificerede, før de er målt på fysisk hardware.
