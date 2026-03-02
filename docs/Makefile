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
	$(VIDEODIR)/rotating_morph.mp4 \
	$(VIDEODIR)/rotation_updater.mp4 \
	$(VIDEODIR)/sine_curve_unit_circle.mp4 \
	$(VIDEODIR)/speed_and_sections.mp4 \
	$(VIDEODIR)/spiral.mp4 \
	$(VIDEODIR)/three_d_camera.mp4 \
	$(VIDEODIR)/zoomed_inset.mp4 \
	$(VIDEODIR)/axes_zoom.mp4 \
	$(VIDEODIR)/annotation_untype_example.mp4 \
	$(VIDEODIR)/array_viz_example.mp4 \
	$(VIDEODIR)/asymptote_coords_example.mp4 \
	$(VIDEODIR)/automaton_example.mp4 \
	$(VIDEODIR)/bar_chart_animate_example.mp4 \
	$(VIDEODIR)/bar_heartbeat_example.mp4 \
	$(VIDEODIR)/bohr_atom_example.mp4 \
	$(VIDEODIR)/boxplot_band_example.mp4 \
	$(VIDEODIR)/bubble_donut_example.mp4 \
	$(VIDEODIR)/callout_example.mp4 \
	$(VIDEODIR)/candlestick_gantt_example.mp4 \
	$(VIDEODIR)/cascade_shake_example.mp4 \
	$(VIDEODIR)/chart_enhance_example.mp4 \
	$(VIDEODIR)/chart_showcase_example.mp4 \
	$(VIDEODIR)/checklist_stepper_tagcloud_example.mp4 \
	$(VIDEODIR)/chess_example.mp4 \
	$(VIDEODIR)/clone_example.mp4 \
	$(VIDEODIR)/code_highlight.mp4 \
	$(VIDEODIR)/code_highlight_lines_example.mp4 \
	$(VIDEODIR)/complex_plane_example.mp4 \
	$(VIDEODIR)/contour_quiver_band_example.mp4 \
	$(VIDEODIR)/cursor_dim_example.mp4 \
	$(VIDEODIR)/curve_effects_example.mp4 \
	$(VIDEODIR)/dashed_title_example.mp4 \
	$(VIDEODIR)/data_structures_example.mp4 \
	$(VIDEODIR)/electrostatics_example.mp4 \
	$(VIDEODIR)/errorbar_histogram_boxplot_example.mp4 \
	$(VIDEODIR)/errorbars_radial_example.mp4 \
	$(VIDEODIR)/flowchart_example.mp4 \
	$(VIDEODIR)/focus_camera_example.mp4 \
	$(VIDEODIR)/funnel_gauge_example.mp4 \
	$(VIDEODIR)/gradient_example.mp4 \
	$(VIDEODIR)/gradient_styling_example.mp4 \
	$(VIDEODIR)/heatmap_waterfall_example.mp4 \
	$(VIDEODIR)/highlight_range_example.mp4 \
	$(VIDEODIR)/histogram_rotate_example.mp4 \
	$(VIDEODIR)/implicit_curve_example.mp4 \
	$(VIDEODIR)/implicit_dotplot_example.mp4 \
	$(VIDEODIR)/kpi_bullet_example.mp4 \
	$(VIDEODIR)/legend_flip_example.mp4 \
	$(VIDEODIR)/line_arc_utils_example.mp4 \
	$(VIDEODIR)/linked_list_example.mp4 \
	$(VIDEODIR)/network_graph_example.mp4 \
	$(VIDEODIR)/network_tree_example.mp4 \
	$(VIDEODIR)/neural_network_example.mp4 \
	$(VIDEODIR)/number_plane_transform_example.mp4 \
	$(VIDEODIR)/numberline_pointer_example.mp4 \
	$(VIDEODIR)/optics_example.mp4 \
	$(VIDEODIR)/orbit_example.mp4 \
	$(VIDEODIR)/parametric_curve_example.mp4 \
	$(VIDEODIR)/pendulum_example.mp4 \
	$(VIDEODIR)/physics_bouncing_balls.mp4 \
	$(VIDEODIR)/physics_cloth.mp4 \
	$(VIDEODIR)/physics_showcase_example.mp4 \
	$(VIDEODIR)/physics_spring.mp4 \
	$(VIDEODIR)/polar_plot_example.mp4 \
	$(VIDEODIR)/progress_bar_example.mp4 \
	$(VIDEODIR)/progress_scoreboard_example.mp4 \
	$(VIDEODIR)/radar_chart_example.mp4 \
	$(VIDEODIR)/ribbon_swarm_heatmap_example.mp4 \
	$(VIDEODIR)/sankey_lollipop_example.mp4 \
	$(VIDEODIR)/scatter_arc_example.mp4 \
	$(VIDEODIR)/scatter_colorwave_example.mp4 \
	$(VIDEODIR)/science_showcase_example.mp4 \
	$(VIDEODIR)/scramble_text_example.mp4 \
	$(VIDEODIR)/slope_wave_example.mp4 \
	$(VIDEODIR)/speech_badge_divider_example.mp4 \
	$(VIDEODIR)/spiral_secant_example.mp4 \
	$(VIDEODIR)/spring_grid_example.mp4 \
	$(VIDEODIR)/stack_viz_example.mp4 \
	$(VIDEODIR)/standing_wave_example.mp4 \
	$(VIDEODIR)/status_meter_breadcrumb_example.mp4 \
	$(VIDEODIR)/stem_grouped_example.mp4 \
	$(VIDEODIR)/step_squish_example.mp4 \
	$(VIDEODIR)/stream_lines_example.mp4 \
	$(VIDEODIR)/table_highlight_example.mp4 \
	$(VIDEODIR)/tangent_arealabel_example.mp4 \
	$(VIDEODIR)/tangent_line_example.mp4 \
	$(VIDEODIR)/text_highlight_example.mp4 \
	$(VIDEODIR)/textbox_bracket_icongrid_example.mp4 \
	$(VIDEODIR)/trace_area_example.mp4 \
	$(VIDEODIR)/trace_elastic_example.mp4 \
	$(VIDEODIR)/trail_reveal_example.mp4 \
	$(VIDEODIR)/transform_from_copy_example.mp4 \
	$(VIDEODIR)/tree_example.mp4 \
	$(VIDEODIR)/typewrite_example.mp4 \
	$(VIDEODIR)/ui_showcase_example.mp4 \
	$(VIDEODIR)/variable_example.mp4 \
	$(VIDEODIR)/vector_field_axes_example.mp4 \
	$(VIDEODIR)/vector_field_example.mp4 \
	$(VIDEODIR)/vector_sort_example.mp4 \
	$(VIDEODIR)/venn_org_example.mp4 \
	$(VIDEODIR)/waffle_mindmap_example.mp4 \
	$(VIDEODIR)/zeroline_warp_example.mp4

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
	$(VIDEODIR)/vector_arrow.svg \
	$(VIDEODIR)/code_explanation.svg \
	$(VIDEODIR)/graph_example.svg

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

$(VIDEODIR)/annotation_untype_example.mp4: $(EXDIR)/annotation_untype_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/annotation_untype_example.py -v --no-display

$(VIDEODIR)/array_viz_example.mp4: $(EXDIR)/array_viz_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/array_viz_example.py -v --no-display

$(VIDEODIR)/asymptote_coords_example.mp4: $(EXDIR)/asymptote_coords_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/asymptote_coords_example.py -v --no-display

$(VIDEODIR)/automaton_example.mp4: $(EXDIR)/automaton_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/automaton_example.py -v --no-display

$(VIDEODIR)/bar_chart_animate_example.mp4: $(EXDIR)/bar_chart_animate_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/bar_chart_animate_example.py -v --no-display

$(VIDEODIR)/bar_heartbeat_example.mp4: $(EXDIR)/bar_heartbeat_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/bar_heartbeat_example.py -v --no-display

$(VIDEODIR)/bohr_atom_example.mp4: $(EXDIR)/bohr_atom_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/bohr_atom_example.py -v --no-display

$(VIDEODIR)/boxplot_band_example.mp4: $(EXDIR)/boxplot_band_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/boxplot_band_example.py -v --no-display

$(VIDEODIR)/bubble_donut_example.mp4: $(EXDIR)/bubble_donut_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/bubble_donut_example.py -v --no-display

$(VIDEODIR)/callout_example.mp4: $(EXDIR)/callout_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/callout_example.py -v --no-display

$(VIDEODIR)/candlestick_gantt_example.mp4: $(EXDIR)/candlestick_gantt_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/candlestick_gantt_example.py -v --no-display

$(VIDEODIR)/cascade_shake_example.mp4: $(EXDIR)/cascade_shake_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/cascade_shake_example.py -v --no-display

$(VIDEODIR)/chart_enhance_example.mp4: $(EXDIR)/chart_enhance_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/chart_enhance_example.py -v --no-display

$(VIDEODIR)/chart_showcase_example.mp4: $(EXDIR)/chart_showcase_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/chart_showcase_example.py -v --no-display

$(VIDEODIR)/checklist_stepper_tagcloud_example.mp4: $(EXDIR)/checklist_stepper_tagcloud_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/checklist_stepper_tagcloud_example.py -v --no-display

$(VIDEODIR)/chess_example.mp4: $(EXDIR)/chess_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/chess_example.py -v --no-display

$(VIDEODIR)/clone_example.mp4: $(EXDIR)/clone_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/clone_example.py -v --no-display

$(VIDEODIR)/code_explanation.svg: $(EXDIR)/code_explanation.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/code_explanation.py -v --no-display

$(VIDEODIR)/code_highlight.mp4: $(EXDIR)/code_highlight.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/code_highlight.py -v --no-display

$(VIDEODIR)/code_highlight_lines_example.mp4: $(EXDIR)/code_highlight_lines_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/code_highlight_lines_example.py -v --no-display

$(VIDEODIR)/complex_plane_example.mp4: $(EXDIR)/complex_plane_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/complex_plane_example.py -v --no-display

$(VIDEODIR)/contour_quiver_band_example.mp4: $(EXDIR)/contour_quiver_band_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/contour_quiver_band_example.py -v --no-display

$(VIDEODIR)/cursor_dim_example.mp4: $(EXDIR)/cursor_dim_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/cursor_dim_example.py -v --no-display

$(VIDEODIR)/curve_effects_example.mp4: $(EXDIR)/curve_effects_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/curve_effects_example.py -v --no-display

$(VIDEODIR)/dashed_title_example.mp4: $(EXDIR)/dashed_title_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/dashed_title_example.py -v --no-display

$(VIDEODIR)/data_structures_example.mp4: $(EXDIR)/data_structures_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/data_structures_example.py -v --no-display

$(VIDEODIR)/electrostatics_example.mp4: $(EXDIR)/electrostatics_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/electrostatics_example.py -v --no-display

$(VIDEODIR)/errorbar_histogram_boxplot_example.mp4: $(EXDIR)/errorbar_histogram_boxplot_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/errorbar_histogram_boxplot_example.py -v --no-display

$(VIDEODIR)/errorbars_radial_example.mp4: $(EXDIR)/errorbars_radial_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/errorbars_radial_example.py -v --no-display

$(VIDEODIR)/flowchart_example.mp4: $(EXDIR)/flowchart_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/flowchart_example.py -v --no-display

$(VIDEODIR)/focus_camera_example.mp4: $(EXDIR)/focus_camera_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/focus_camera_example.py -v --no-display

$(VIDEODIR)/funnel_gauge_example.mp4: $(EXDIR)/funnel_gauge_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/funnel_gauge_example.py -v --no-display

$(VIDEODIR)/gradient_example.mp4: $(EXDIR)/gradient_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/gradient_example.py -v --no-display

$(VIDEODIR)/gradient_styling_example.mp4: $(EXDIR)/gradient_styling_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/gradient_styling_example.py -v --no-display

$(VIDEODIR)/graph_example.svg: $(EXDIR)/graph_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/graph_example.py -v --no-display

$(VIDEODIR)/heatmap_waterfall_example.mp4: $(EXDIR)/heatmap_waterfall_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/heatmap_waterfall_example.py -v --no-display

$(VIDEODIR)/highlight_range_example.mp4: $(EXDIR)/highlight_range_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/highlight_range_example.py -v --no-display

$(VIDEODIR)/histogram_rotate_example.mp4: $(EXDIR)/histogram_rotate_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/histogram_rotate_example.py -v --no-display

$(VIDEODIR)/implicit_curve_example.mp4: $(EXDIR)/implicit_curve_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/implicit_curve_example.py -v --no-display

$(VIDEODIR)/implicit_dotplot_example.mp4: $(EXDIR)/implicit_dotplot_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/implicit_dotplot_example.py -v --no-display

$(VIDEODIR)/kpi_bullet_example.mp4: $(EXDIR)/kpi_bullet_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/kpi_bullet_example.py -v --no-display

$(VIDEODIR)/legend_flip_example.mp4: $(EXDIR)/legend_flip_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/legend_flip_example.py -v --no-display

$(VIDEODIR)/line_arc_utils_example.mp4: $(EXDIR)/line_arc_utils_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/line_arc_utils_example.py -v --no-display

$(VIDEODIR)/linked_list_example.mp4: $(EXDIR)/linked_list_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/linked_list_example.py -v --no-display

$(VIDEODIR)/network_graph_example.mp4: $(EXDIR)/network_graph_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/network_graph_example.py -v --no-display

$(VIDEODIR)/network_tree_example.mp4: $(EXDIR)/network_tree_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/network_tree_example.py -v --no-display

$(VIDEODIR)/neural_network_example.mp4: $(EXDIR)/neural_network_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/neural_network_example.py -v --no-display

$(VIDEODIR)/number_plane_transform_example.mp4: $(EXDIR)/number_plane_transform_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/number_plane_transform_example.py -v --no-display

$(VIDEODIR)/numberline_pointer_example.mp4: $(EXDIR)/numberline_pointer_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/numberline_pointer_example.py -v --no-display

$(VIDEODIR)/optics_example.mp4: $(EXDIR)/optics_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/optics_example.py -v --no-display

$(VIDEODIR)/orbit_example.mp4: $(EXDIR)/orbit_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/orbit_example.py -v --no-display

$(VIDEODIR)/parametric_curve_example.mp4: $(EXDIR)/parametric_curve_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/parametric_curve_example.py -v --no-display

$(VIDEODIR)/pendulum_example.mp4: $(EXDIR)/pendulum_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/pendulum_example.py -v --no-display

$(VIDEODIR)/physics_bouncing_balls.mp4: $(EXDIR)/physics_bouncing_balls.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/physics_bouncing_balls.py -v --no-display

$(VIDEODIR)/physics_cloth.mp4: $(EXDIR)/physics_cloth.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/physics_cloth.py -v --no-display

$(VIDEODIR)/physics_showcase_example.mp4: $(EXDIR)/physics_showcase_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/physics_showcase_example.py -v --no-display

$(VIDEODIR)/physics_spring.mp4: $(EXDIR)/physics_spring.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/physics_spring.py -v --no-display

$(VIDEODIR)/polar_plot_example.mp4: $(EXDIR)/polar_plot_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/polar_plot_example.py -v --no-display

$(VIDEODIR)/progress_bar_example.mp4: $(EXDIR)/progress_bar_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/progress_bar_example.py -v --no-display

$(VIDEODIR)/progress_scoreboard_example.mp4: $(EXDIR)/progress_scoreboard_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/progress_scoreboard_example.py -v --no-display

$(VIDEODIR)/radar_chart_example.mp4: $(EXDIR)/radar_chart_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/radar_chart_example.py -v --no-display

$(VIDEODIR)/ribbon_swarm_heatmap_example.mp4: $(EXDIR)/ribbon_swarm_heatmap_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/ribbon_swarm_heatmap_example.py -v --no-display

$(VIDEODIR)/sankey_lollipop_example.mp4: $(EXDIR)/sankey_lollipop_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/sankey_lollipop_example.py -v --no-display

$(VIDEODIR)/scatter_arc_example.mp4: $(EXDIR)/scatter_arc_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/scatter_arc_example.py -v --no-display

$(VIDEODIR)/scatter_colorwave_example.mp4: $(EXDIR)/scatter_colorwave_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/scatter_colorwave_example.py -v --no-display

$(VIDEODIR)/science_showcase_example.mp4: $(EXDIR)/science_showcase_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/science_showcase_example.py -v --no-display

$(VIDEODIR)/scramble_text_example.mp4: $(EXDIR)/scramble_text_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/scramble_text_example.py -v --no-display

$(VIDEODIR)/slope_wave_example.mp4: $(EXDIR)/slope_wave_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/slope_wave_example.py -v --no-display

$(VIDEODIR)/speech_badge_divider_example.mp4: $(EXDIR)/speech_badge_divider_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/speech_badge_divider_example.py -v --no-display

$(VIDEODIR)/spiral_secant_example.mp4: $(EXDIR)/spiral_secant_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/spiral_secant_example.py -v --no-display

$(VIDEODIR)/spring_grid_example.mp4: $(EXDIR)/spring_grid_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/spring_grid_example.py -v --no-display

$(VIDEODIR)/stack_viz_example.mp4: $(EXDIR)/stack_viz_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/stack_viz_example.py -v --no-display

$(VIDEODIR)/standing_wave_example.mp4: $(EXDIR)/standing_wave_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/standing_wave_example.py -v --no-display

$(VIDEODIR)/status_meter_breadcrumb_example.mp4: $(EXDIR)/status_meter_breadcrumb_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/status_meter_breadcrumb_example.py -v --no-display

$(VIDEODIR)/stem_grouped_example.mp4: $(EXDIR)/stem_grouped_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/stem_grouped_example.py -v --no-display

$(VIDEODIR)/step_squish_example.mp4: $(EXDIR)/step_squish_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/step_squish_example.py -v --no-display

$(VIDEODIR)/stream_lines_example.mp4: $(EXDIR)/stream_lines_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/stream_lines_example.py -v --no-display

$(VIDEODIR)/table_highlight_example.mp4: $(EXDIR)/table_highlight_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/table_highlight_example.py -v --no-display

$(VIDEODIR)/tangent_arealabel_example.mp4: $(EXDIR)/tangent_arealabel_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/tangent_arealabel_example.py -v --no-display

$(VIDEODIR)/tangent_line_example.mp4: $(EXDIR)/tangent_line_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/tangent_line_example.py -v --no-display

$(VIDEODIR)/text_highlight_example.mp4: $(EXDIR)/text_highlight_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/text_highlight_example.py -v --no-display

$(VIDEODIR)/textbox_bracket_icongrid_example.mp4: $(EXDIR)/textbox_bracket_icongrid_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/textbox_bracket_icongrid_example.py -v --no-display

$(VIDEODIR)/trace_area_example.mp4: $(EXDIR)/trace_area_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/trace_area_example.py -v --no-display

$(VIDEODIR)/trace_elastic_example.mp4: $(EXDIR)/trace_elastic_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/trace_elastic_example.py -v --no-display

$(VIDEODIR)/trail_reveal_example.mp4: $(EXDIR)/trail_reveal_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/trail_reveal_example.py -v --no-display

$(VIDEODIR)/transform_from_copy_example.mp4: $(EXDIR)/transform_from_copy_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/transform_from_copy_example.py -v --no-display

$(VIDEODIR)/tree_example.mp4: $(EXDIR)/tree_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/tree_example.py -v --no-display

$(VIDEODIR)/typewrite_example.mp4: $(EXDIR)/typewrite_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/typewrite_example.py -v --no-display

$(VIDEODIR)/ui_showcase_example.mp4: $(EXDIR)/ui_showcase_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/ui_showcase_example.py -v --no-display

$(VIDEODIR)/variable_example.mp4: $(EXDIR)/variable_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/variable_example.py -v --no-display

$(VIDEODIR)/vector_field_axes_example.mp4: $(EXDIR)/vector_field_axes_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/vector_field_axes_example.py -v --no-display

$(VIDEODIR)/vector_field_example.mp4: $(EXDIR)/vector_field_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/vector_field_example.py -v --no-display

$(VIDEODIR)/vector_sort_example.mp4: $(EXDIR)/vector_sort_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/vector_sort_example.py -v --no-display

$(VIDEODIR)/venn_org_example.mp4: $(EXDIR)/venn_org_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/venn_org_example.py -v --no-display

$(VIDEODIR)/waffle_mindmap_example.mp4: $(EXDIR)/waffle_mindmap_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/waffle_mindmap_example.py -v --no-display

$(VIDEODIR)/zeroline_warp_example.mp4: $(EXDIR)/zeroline_warp_example.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/zeroline_warp_example.py -v --no-display

$(VIDEODIR)/animations_color.mp4: $(EXDIR)/animations_color.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/animations_color.py -v --no-display

$(VIDEODIR)/animations_counters.mp4: $(EXDIR)/animations_counters.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/animations_counters.py -v --no-display

$(VIDEODIR)/animations_creation.mp4: $(EXDIR)/animations_creation.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/animations_creation.py -v --no-display

$(VIDEODIR)/animations_effects.mp4: $(EXDIR)/animations_effects.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/animations_effects.py -v --no-display

$(VIDEODIR)/animations_movement.mp4: $(EXDIR)/animations_movement.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/animations_movement.py -v --no-display

$(VIDEODIR)/animations_text.mp4: $(EXDIR)/animations_text.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/animations_text.py -v --no-display

$(VIDEODIR)/animations_vcollection.mp4: $(EXDIR)/animations_vcollection.py $(LIB) | $(VIDEODIR)
	cd $(ROOTDIR) && $(PYTHON) examples/animations_vcollection.py -v --no-display

$(VIDEODIR):
	mkdir -p $@
