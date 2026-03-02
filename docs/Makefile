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
	$(VIDEODIR)/animations_color.mp4 \
	$(VIDEODIR)/animations_counters.mp4 \
	$(VIDEODIR)/animations_creation.mp4 \
	$(VIDEODIR)/animations_effects.mp4 \
	$(VIDEODIR)/animations_movement.mp4 \
	$(VIDEODIR)/animations_text.mp4 \
	$(VIDEODIR)/animations_vcollection.mp4 \
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
	$(VIDEODIR)/rotation_updater.mp4 \
	$(VIDEODIR)/sine_curve_unit_circle.mp4 \
	$(VIDEODIR)/speed_and_sections.mp4 \
	$(VIDEODIR)/spiral.mp4 \
	$(VIDEODIR)/three_d_camera.mp4 \
	$(VIDEODIR)/zoomed_inset.mp4 \
	$(VIDEODIR)/axes_zoom.mp4 \
	$(VIDEODIR)/automaton_example.mp4 \
	$(VIDEODIR)/chess_example.mp4 \
	$(VIDEODIR)/code_highlight.mp4 \
	$(VIDEODIR)/focus_camera_example.mp4 \
	$(VIDEODIR)/graph_structures.mp4 \
	$(VIDEODIR)/neural_network_example.mp4 \
	$(VIDEODIR)/number_plane_transform_example.mp4 \
	$(VIDEODIR)/pendulum_example.mp4 \
	$(VIDEODIR)/physics_bouncing_balls.mp4 \
	$(VIDEODIR)/physics_cloth.mp4 \
	$(VIDEODIR)/physics_spring.mp4 \
	$(VIDEODIR)/table_highlight_example.mp4 \
	$(VIDEODIR)/transform_from_copy_example.mp4 \
	$(VIDEODIR)/numberline_features.mp4 \
	$(VIDEODIR)/chart_methods.mp4 \
	$(VIDEODIR)/data_structure_methods.mp4

SVGS = \
	$(VIDEODIR)/brace_annotation.svg \
	$(VIDEODIR)/gradient_image.svg \
	$(VIDEODIR)/graph_area_plot.svg \
	$(VIDEODIR)/heat_diagram.svg \
	$(VIDEODIR)/manim_community_logo.svg \
	$(VIDEODIR)/sin_cos_plot.svg \
	$(VIDEODIR)/three_d_axes.svg \
	$(VIDEODIR)/three_d_helix.svg \
	$(VIDEODIR)/three_d_sphere.svg \
	$(VIDEODIR)/three_d_surface_plot.svg \
	$(VIDEODIR)/vector_arrow.svg \
	$(VIDEODIR)/code_explanation.svg \
	$(VIDEODIR)/complex_plane_example.svg \
	$(VIDEODIR)/gradient_example.svg \
	$(VIDEODIR)/parametric_curve_example.svg \
	$(VIDEODIR)/polar_plot_example.svg \
	$(VIDEODIR)/vector_fields.svg \
	$(VIDEODIR)/chart_types.svg \
	$(VIDEODIR)/ui_widgets.svg \
	$(VIDEODIR)/circuit_components.svg \
	$(VIDEODIR)/diagram_types.svg \
	$(VIDEODIR)/axes_plot_types.svg \
	$(VIDEODIR)/axes_annotations.svg \
	$(VIDEODIR)/axes_overlays.svg \
	$(VIDEODIR)/axes_formatters.svg \
	$(VIDEODIR)/shapes.svg \
	$(VIDEODIR)/threed.svg

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
	cd $(ROOTDIR) && $(PYTHON) examples/manim/$*.py --for-docs

$(VIDEODIR)/%.svg: $(MANIMDIR)/%.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/manim/$*.py --for-docs

# Non-manim examples
$(VIDEODIR)/morphing_example.mp4: $(EXDIR)/morphing_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/morphing_example.py --for-docs

$(VIDEODIR)/graph_animated.mp4: $(EXDIR)/graph_animated.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/graph_animated.py --for-docs

$(VIDEODIR)/spiral.mp4: $(EXDIR)/spiral.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/spiral.py --for-docs

$(VIDEODIR)/heart.mp4: $(EXDIR)/heart.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/heart.py --for-docs

$(VIDEODIR)/speed_and_sections.mp4: $(EXDIR)/speed_and_sections.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/speed_and_sections.py --for-docs

$(VIDEODIR)/axes_zoom.mp4: $(EXDIR)/axes_zoom.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/axes_zoom.py --for-docs

$(VIDEODIR)/automaton_example.mp4: $(EXDIR)/automaton_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/automaton_example.py --for-docs

$(VIDEODIR)/chess_example.mp4: $(EXDIR)/chess_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/chess_example.py --for-docs

$(VIDEODIR)/code_explanation.svg: $(EXDIR)/code_explanation.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/code_explanation.py --for-docs

$(VIDEODIR)/code_highlight.mp4: $(EXDIR)/code_highlight.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/code_highlight.py --for-docs

$(VIDEODIR)/complex_plane_example.svg: $(EXDIR)/complex_plane_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/complex_plane_example.py --for-docs

$(VIDEODIR)/focus_camera_example.mp4: $(EXDIR)/focus_camera_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/focus_camera_example.py --for-docs

$(VIDEODIR)/gradient_example.svg: $(EXDIR)/gradient_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/gradient_example.py --for-docs

$(VIDEODIR)/graph_structures.mp4: $(EXDIR)/graph_structures.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/graph_structures.py --for-docs

$(VIDEODIR)/neural_network_example.mp4: $(EXDIR)/neural_network_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/neural_network_example.py --for-docs

$(VIDEODIR)/number_plane_transform_example.mp4: $(EXDIR)/number_plane_transform_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/number_plane_transform_example.py --for-docs

$(VIDEODIR)/parametric_curve_example.svg: $(EXDIR)/parametric_curve_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/parametric_curve_example.py --for-docs

$(VIDEODIR)/pendulum_example.mp4: $(EXDIR)/pendulum_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/pendulum_example.py --for-docs

$(VIDEODIR)/physics_bouncing_balls.mp4: $(EXDIR)/physics_bouncing_balls.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/physics_bouncing_balls.py --for-docs

$(VIDEODIR)/physics_cloth.mp4: $(EXDIR)/physics_cloth.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/physics_cloth.py --for-docs

$(VIDEODIR)/physics_spring.mp4: $(EXDIR)/physics_spring.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/physics_spring.py --for-docs

$(VIDEODIR)/polar_plot_example.svg: $(EXDIR)/polar_plot_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/polar_plot_example.py --for-docs

$(VIDEODIR)/table_highlight_example.mp4: $(EXDIR)/table_highlight_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/table_highlight_example.py --for-docs

$(VIDEODIR)/transform_from_copy_example.mp4: $(EXDIR)/transform_from_copy_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/transform_from_copy_example.py --for-docs

$(VIDEODIR)/vector_fields.svg: $(EXDIR)/vector_fields.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/vector_fields.py --for-docs

$(VIDEODIR)/animations_color.mp4: $(EXDIR)/animations_color.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/animations_color.py --for-docs

$(VIDEODIR)/animations_counters.mp4: $(EXDIR)/animations_counters.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/animations_counters.py --for-docs

$(VIDEODIR)/animations_creation.mp4: $(EXDIR)/animations_creation.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/animations_creation.py --for-docs

$(VIDEODIR)/animations_effects.mp4: $(EXDIR)/animations_effects.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/animations_effects.py --for-docs

$(VIDEODIR)/animations_movement.mp4: $(EXDIR)/animations_movement.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/animations_movement.py --for-docs

$(VIDEODIR)/animations_text.mp4: $(EXDIR)/animations_text.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/animations_text.py --for-docs

$(VIDEODIR)/animations_vcollection.mp4: $(EXDIR)/animations_vcollection.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/animations_vcollection.py --for-docs

$(VIDEODIR)/chart_types.svg: $(EXDIR)/chart_types.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/chart_types.py --for-docs

$(VIDEODIR)/ui_widgets.svg: $(EXDIR)/ui_widgets.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/ui_widgets.py --for-docs

$(VIDEODIR)/circuit_components.svg: $(EXDIR)/circuit_components.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/circuit_components.py --for-docs

$(VIDEODIR)/diagram_types.svg: $(EXDIR)/diagram_types.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/diagram_types.py --for-docs

$(VIDEODIR)/axes_plot_types.svg: $(EXDIR)/axes_plot_types.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/axes_plot_types.py --for-docs

$(VIDEODIR)/axes_annotations.svg: $(EXDIR)/axes_annotations.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/axes_annotations.py --for-docs

$(VIDEODIR)/axes_overlays.svg: $(EXDIR)/axes_overlays.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/axes_overlays.py --for-docs

$(VIDEODIR)/axes_formatters.svg: $(EXDIR)/axes_formatters.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/axes_formatters.py --for-docs

$(VIDEODIR)/shapes.svg: $(EXDIR)/shapes.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/shapes.py --for-docs

$(VIDEODIR)/threed.svg: $(EXDIR)/threed.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/threed.py --for-docs

$(VIDEODIR)/numberline_features.mp4: $(EXDIR)/numberline_features.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/numberline_features.py --for-docs

$(VIDEODIR)/chart_methods.mp4: $(EXDIR)/chart_methods.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/chart_methods.py --for-docs

$(VIDEODIR)/data_structure_methods.mp4: $(EXDIR)/data_structure_methods.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/data_structure_methods.py --for-docs

$(VIDEODIR):
	mkdir -p $@
