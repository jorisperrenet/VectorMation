SHELL := /bin/bash
MAKEFLAGS += -j$(shell nproc 2>/dev/null || echo 4)
PYTHON ?= python
SPHINXBUILD ?= sphinx-build
SRCDIR = source
BUILDDIR = build
VIDEODIR = $(SRCDIR)/_static/videos
IMGDIR = $(SRCDIR)/_static/images
EXDIR = ../examples
MANIMDIR = $(EXDIR)/manim
DIAGDIR = generate_diagrams

# ── Video / screenshot assets ────────────────────────────────────────
# Each asset depends on its source script and the library.
LIB = $(wildcard ../vectormation/*.py)

VIDEOS = \
	$(VIDEODIR)/animation_showcase.mp4 \
	$(VIDEODIR)/arg_min.mp4 \
	$(VIDEODIR)/boolean_operations.mp4 \
	$(VIDEODIR)/following_graph_camera.mp4 \
	$(VIDEODIR)/graph_animated.mp4 \
	$(VIDEODIR)/heart.mp4 \
	$(VIDEODIR)/morphing_example.mp4 \
	$(VIDEODIR)/moving_angle.mp4 \
	$(VIDEODIR)/moving_around.mp4 \
	$(VIDEODIR)/moving_dots.mp4 \
	$(VIDEODIR)/moving_frame_box.mp4 \
	$(VIDEODIR)/moving_group.mp4 \
	$(VIDEODIR)/opening_manim.mp4 \
	$(VIDEODIR)/point_moving_on_shapes.mp4 \
	$(VIDEODIR)/point_with_trace.mp4 \
	$(VIDEODIR)/polygon_on_axes.mp4 \
	$(VIDEODIR)/rotating_morph.mp4 \
	$(VIDEODIR)/rotation_updater.mp4 \
	$(VIDEODIR)/sine_curve_unit_circle.mp4 \
	$(VIDEODIR)/speed_and_sections.mp4 \
	$(VIDEODIR)/spiral.mp4 \
	$(VIDEODIR)/three_d_camera.mp4 \
	$(VIDEODIR)/zoomed_inset.mp4 \
	$(VIDEODIR)/axes_zoom.mp4

SVGS = \
	$(VIDEODIR)/brace_annotation.svg \
	$(VIDEODIR)/gradient_image.svg \
	$(VIDEODIR)/graph_area_plot.svg \
	$(VIDEODIR)/heat_diagram.svg \
	$(VIDEODIR)/manim_community_logo.svg \
	$(VIDEODIR)/sierpinski_triangle.svg \
	$(VIDEODIR)/sin_cos_plot.svg \
	$(VIDEODIR)/three_d_axes.svg \
	$(VIDEODIR)/three_d_helix.svg \
	$(VIDEODIR)/three_d_sphere.svg \
	$(VIDEODIR)/three_d_surface_plot.svg \
	$(VIDEODIR)/vector_arrow.svg

ASSETS = $(VIDEOS) $(SVGS)

# ── Diagram assets ───────────────────────────────────────────────────
DIAGRAMS = $(wildcard $(IMGDIR)/*_params.svg)

# ── Top-level targets ────────────────────────────────────────────────

.PHONY: html assets diagrams videos svgs clean serve live deploy help

help:  ## Show this help
	@grep -E '^[a-z][a-z_-]+:.*##' $(MAKEFILE_LIST) | \
		awk -F ':.*## ' '{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

html: assets diagrams  ## Build HTML docs (regenerates changed assets first)
	$(SPHINXBUILD) -b html $(SRCDIR) $(BUILDDIR)
	@echo "Build finished. Open $(BUILDDIR)/index.html"

assets: videos svgs  ## Regenerate only changed video/screenshot assets

videos: $(VIDEOS)  ## Regenerate only changed videos

svgs: $(SVGS)  ## Regenerate only changed SVG frames

diagrams:  ## Regenerate SVG parameter diagrams
	$(PYTHON) $(DIAGDIR)/generate_all.py

serve: html  ## Build and serve locally on port 8000
	$(PYTHON) -m http.server -d $(BUILDDIR) 8000

live:  ## Live-reload (requires sphinx-autobuild)
	sphinx-autobuild $(SRCDIR) $(BUILDDIR)

deploy: html  ## Deploy docs to GitHub Pages (gh-pages branch)
	@if [ ! -d $(BUILDDIR) ]; then echo "No build directory. Run 'make html' first."; exit 1; fi
	cd $(ROOTDIR) && ghp-import -n -p -f docs/build

clean:  ## Remove build directory
	rm -rf $(BUILDDIR)

# ── Pattern rules ────────────────────────────────────────────────────

# All example scripts use paths relative to the repo root.
ROOTDIR = $(abspath ..)

# Manim examples → videos/svgs
$(VIDEODIR)/%.mp4: $(MANIMDIR)/%.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/manim/$*.py -v --no-display

$(VIDEODIR)/%.svg: $(MANIMDIR)/%.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/manim/$*.py -v --no-display

# Non-manim examples
$(VIDEODIR)/animation_showcase.mp4: $(EXDIR)/animation_showcase.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/animation_showcase.py -v --no-display

$(VIDEODIR)/morphing_example.mp4: $(EXDIR)/morphing_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/morphing_example.py -v --no-display

$(VIDEODIR)/rotating_morph.mp4: $(EXDIR)/rotating_morph.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/rotating_morph.py -v --no-display

$(VIDEODIR)/graph_animated.mp4: $(EXDIR)/graph_animated.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/graph_animated.py -v --no-display

$(VIDEODIR)/spiral.mp4: $(EXDIR)/spiral.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/spiral.py -v --no-display

$(VIDEODIR)/heart.mp4: $(EXDIR)/heart.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/heart.py -v --no-display

$(VIDEODIR)/sierpinski_triangle.svg: $(EXDIR)/sierpinski_triangle.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/sierpinski_triangle.py -v --no-display

$(VIDEODIR)/speed_and_sections.mp4: $(EXDIR)/speed_and_sections.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/speed_and_sections.py -v --no-display

$(VIDEODIR)/axes_zoom.mp4: $(EXDIR)/axes_zoom.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/axes_zoom.py -v --no-display

$(VIDEODIR):
	mkdir -p $@
