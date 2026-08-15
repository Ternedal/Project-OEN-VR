#!/usr/bin/env python3
"""Keep generated ProductionArt GUIDs stable when its Unity root moves."""
from __future__ import annotations

from pathlib import Path


RUNTIME_PREFIX = "Assets/ProductionArt/"
# Assemble the historical identity without retaining it as a usable root reference.
HISTORICAL_ID_PREFIX = "Assets/" + "ProjectOEN/ProductionArt/"


def stable_production_art_guid_path(path: Path, root: Path) -> str:
    """Return the immutable GUID identity for a path under ProductionArt."""
    relative = path.relative_to(root).as_posix() if path.is_absolute() else path.as_posix()
    if relative.startswith(RUNTIME_PREFIX):
        return HISTORICAL_ID_PREFIX + relative[len(RUNTIME_PREFIX):]
    return relative
