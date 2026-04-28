"""Generate PyPI-flavored README and image assets in pypi_assets/.

PyPI's README renderer strips <img> tags pointing at .svg files and does not
resolve relative URLs, so the GitHub README cannot be reused as-is. This script
rasterizes the referenced SVGs to PNG, copies the GIF, and rewrites the image
URLs to absolute raw.githubusercontent.com paths.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "pypi_assets"
GITHUB_RAW_BASE = (
    "https://raw.githubusercontent.com/jorisperrenet/VectorMation/master/pypi_assets"
)

# (source path relative to ROOT, output filename in pypi_assets/, width-in-pixels-or-None)
SVG_RASTER = [
    ("examples/svgs/logo.svg", "logo.png", 800),
    ("examples/svgs/explanation.svg", "explanation.png", 1200),
]
COPY = [
    ("examples/svgs/convolutions.gif", "convolutions.gif"),
]


def newer(src: Path, dst: Path) -> bool:
    return not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime


def rasterize_svgs() -> dict[str, str]:
    """Rasterize SVGs to PNGs. Returns a map of source-rel-path -> output filename."""
    mapping: dict[str, str] = {}
    for svg_rel, out_name, width in SVG_RASTER:
        svg = ROOT / svg_rel
        out = ASSETS / out_name
        mapping[svg_rel] = out_name
        if not newer(svg, out):
            print(f"  {out_name}: up-to-date")
            continue
        if not shutil.which("rsvg-convert"):
            sys.exit(
                "ERROR: rsvg-convert is required to rasterize SVGs.\n"
                "  Install with: pacman -S librsvg  (Arch) or apt install librsvg2-bin"
            )
        print(f"  {out_name}: rendering from {svg_rel} at {width}px wide")
        subprocess.check_call(
            ["rsvg-convert", "-w", str(width), str(svg), "-o", str(out)]
        )
    return mapping


def copy_assets() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for src_rel, out_name in COPY:
        src = ROOT / src_rel
        out = ASSETS / out_name
        mapping[src_rel] = out_name
        if not newer(src, out):
            print(f"  {out_name}: up-to-date")
            continue
        print(f"  {out_name}: copying from {src_rel}")
        shutil.copy2(src, out)
    return mapping


def transform_readme(asset_map: dict[str, str]) -> None:
    src = ROOT / "README.md"
    dst = ASSETS / "README.md"
    text = src.read_text()

    pattern = re.compile(r'src="\./([^"]+)"')

    def replace(match: re.Match[str]) -> str:
        rel = match.group(1)
        if rel not in asset_map:
            sys.exit(
                f"ERROR: README references {rel!r} but no asset mapping is "
                f"defined in scripts/build_pypi.py."
            )
        return f'src="{GITHUB_RAW_BASE}/{asset_map[rel]}"'

    transformed = pattern.sub(replace, text)
    dst.write_text(transformed)
    print(f"  README.md: regenerated ({len(transformed)} bytes)")


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    print("Rasterizing SVGs:")
    raster_map = rasterize_svgs()
    print("Copying assets:")
    copy_map = copy_assets()
    print("Generating PyPI README:")
    transform_readme({**raster_map, **copy_map})


if __name__ == "__main__":
    main()
