#!/usr/bin/env python3
"""Canonical entrypoint for the final Project ØEN tropical vegetation pass.

The additive V1 pass is intentionally superseded by the clean V2 rebuild after
visual review showed that the underlying twig-heavy silhouettes remained visible.
Keeping this stable entrypoint avoids workflow churn while V2 becomes authoritative.
"""
from refine_vegetation_fidelity_v2 import main

if __name__ == "__main__":
    raise SystemExit(main())
