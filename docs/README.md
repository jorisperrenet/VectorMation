## Documentation

This directory contains the Sphinx documentation for VectorMation, using the [Furo](https://pradyunsg.me/furo/) theme.

### Prerequisites

```bash
pip install sphinx furo sphinx-design sphinx-copybutton sphinx-autobuild ghp-import
pip install vectormation[export]   # cairosvg, Pillow (ffmpeg must be on PATH)
```

### Quick build

From the `docs/` directory:

```bash
make html       # regenerate changed assets, then build HTML
make serve      # build + serve on http://localhost:8000
make live        # live-reload (auto-rebuilds on file changes)
```

### Regenerate assets

The Makefile tracks dependencies so only scripts that changed (or whose library code changed) are re-rendered:

```bash
make assets     # regenerate all changed videos and SVG frames
make videos     # regenerate only changed videos
make svgs       # regenerate only changed SVG frames
make diagrams   # regenerate SVG parameter diagrams
```

To force a full rebuild of all assets, touch the library files:

```bash
touch ../vectormation/*.py && make assets
```

### Regenerate SVG diagrams

The parameter diagrams in `source/_static/images/` are generated using VectorMation itself:

```bash
make diagrams
# or directly:
python generate_diagrams/generate_all.py
```

### Regenerate a single example

Run the example script with `-v --no-display` from the repository root:

```bash
python examples/manim/square_to_circle.py -v --no-display
```

### Deploy

```bash
make deploy     # builds HTML, then pushes to gh-pages branch
```

This uses [ghp-import](https://github.com/c-w/ghp-import) to push `docs/build/` to the `gh-pages` branch. Make sure GitHub Pages is configured to serve from the `gh-pages` branch.
