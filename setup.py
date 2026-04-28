"""Build-time hook: regenerate pypi_assets/ before setuptools reads metadata.

Setuptools' pyproject.toml-driven build reads `readme = "pypi_assets/README.md"`
when this module is imported. Generating the file here ensures it is fresh on
every `python -m build`. When installing from an sdist (no source SVGs present),
the hook is a no-op and the pre-generated README ships as-is.
"""
import subprocess
import sys
from pathlib import Path

from setuptools import setup

_ROOT = Path(__file__).resolve().parent

if (_ROOT / "examples" / "svgs" / "logo.svg").exists():
    subprocess.check_call(
        [sys.executable, str(_ROOT / "scripts" / "build_pypi.py")],
        cwd=_ROOT,
    )

setup()
