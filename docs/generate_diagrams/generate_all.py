#!/usr/bin/env python3
"""Generate all SVG parameter diagrams for the documentation.

Run from the repository root:
    python docs/generate_diagrams/generate_all.py
"""
import subprocess, sys, pathlib

DIR = pathlib.Path(__file__).parent
scripts = sorted(DIR.glob("diagram_*.py"))

for script in scripts:
    print(f"  Generating {script.stem} ...")
    subprocess.check_call([sys.executable, str(script)])

print(f"Done – generated {len(scripts)} diagrams.")
