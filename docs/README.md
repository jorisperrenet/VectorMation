## Documentation

This directory contains the Sphinx documentation for VectorMation, using the [Furo](https://pradyunsg.me/furo/) theme.

### Prerequisites

```bash
pip install -r docs/requirements.txt
```

This installs Sphinx, the Furo theme, and the asset-building dependencies (cairosvg, Pillow, etc.). You also need `ffmpeg` on your PATH for video export, and `ghp-import` if you want to deploy.

### Quick build

From the `docs/` directory:

```bash
make html       # regenerate changed assets, then build HTML
make serve      # build + serve on http://localhost:8000
make live       # live-reload (auto-rebuilds on file changes)
```

### Regenerate assets

The Makefile tracks dependencies so only scripts that changed (or whose library code changed) are re-rendered:

```bash
make assets         # regenerate all changed videos and SVG frames
make assets-force   # rebuild all assets unconditionally
make diagrams       # regenerate SVG parameter diagrams only
```

### Regenerate a single example

Run the example script with `-o` from the repository root:

```bash
PYTHONPATH=. python examples/reference/circle.py -o docs/source/_static/videos/circle.mp4
```

### Deploy

```bash
make deploy     # builds HTML, then pushes to gh-pages branch
```

This uses [ghp-import](https://github.com/c-w/ghp-import) to push `docs/build/` to the `gh-pages` branch. Make sure GitHub Pages is configured to serve from the `gh-pages` branch.
