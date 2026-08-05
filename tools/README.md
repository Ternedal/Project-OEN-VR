# Valideringsværktøjer

Installer afhængigheder og kør validering:

```bash
python -m pip install -r tools/requirements-validation.txt
python tools/validate_handoff.py
```

Når Unity-projektet oprettes, udvides denne mappe med content-ID-, localization-, package-lock- og buildmetadata-validering.
