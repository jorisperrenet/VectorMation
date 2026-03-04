#!/usr/bin/env python3
"""Build all documentation assets (videos, SVGs, diagrams) with a single progress bar.

Usage:  python build_assets.py [--jobs N] [--force]

Only rebuilds assets whose source script or library files are newer than the
output.  Pass --force to rebuild everything unconditionally.
"""

import argparse
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

# ---------------------------------------------------------------------------
# Asset registry  (output_file, script_path)
# Paths are relative to the repo root.
# ---------------------------------------------------------------------------

VIDEODIR = 'docs/source/_static/videos'
IMGDIR = 'docs/source/_static/images'

def _v(name):
    return f'{VIDEODIR}/{name}'

def _i(name):
    return f'{IMGDIR}/{name}'

# (output, script)
ASSETS = [
    # ── Manim comparison examples ────────────────────────────────────
    (_v('arg_min.mp4'),                        'examples/manim/arg_min.py'),
    (_v('boolean_operations.mp4'),             'examples/manim/boolean_operations.py'),
    (_v('brace_annotation.svg'),               'examples/manim/brace_annotation.py'),
    (_v('following_graph_camera.mp4'),         'examples/manim/following_graph_camera.py'),
    (_v('gradient_image.svg'),                 'examples/manim/gradient_image.py'),
    (_v('graph_area_plot.svg'),                'examples/manim/graph_area_plot.py'),
    (_v('heat_diagram.svg'),                   'examples/manim/heat_diagram.py'),
    (_v('manim_community_logo.svg'),           'examples/manim/manim_community_logo.py'),
    (_v('moving_angle.mp4'),                   'examples/manim/moving_angle.py'),
    (_v('moving_around.mp4'),                  'examples/manim/moving_around.py'),
    (_v('moving_dots.mp4'),                    'examples/manim/moving_dots.py'),
    (_v('moving_frame_box.mp4'),               'examples/manim/moving_frame_box.py'),
    (_v('moving_group.mp4'),                   'examples/manim/moving_group.py'),
    (_v('opening_manim.mp4'),                  'examples/manim/opening_manim.py'),
    (_v('point_moving_on_shapes.mp4'),         'examples/manim/point_moving_on_shapes.py'),
    (_v('point_with_trace.mp4'),               'examples/manim/point_with_trace.py'),
    (_v('polygon_on_axes.mp4'),                'examples/manim/polygon_on_axes.py'),
    (_v('rotation_updater.mp4'),               'examples/manim/rotation_updater.py'),
    (_v('sin_cos_plot.svg'),                   'examples/manim/sin_cos_plot.py'),
    (_v('sine_curve_unit_circle.mp4'),         'examples/manim/sine_curve_unit_circle.py'),
    (_v('three_d_axes.svg'),                   'examples/manim/three_d_axes.py'),
    (_v('three_d_camera.mp4'),                 'examples/manim/three_d_camera.py'),
    (_v('three_d_helix.svg'),                  'examples/manim/three_d_helix.py'),
    (_v('three_d_sphere.svg'),                 'examples/manim/three_d_sphere.py'),
    (_v('three_d_surface_plot.svg'),           'examples/manim/three_d_surface_plot.py'),
    (_v('vector_arrow.svg'),                   'examples/manim/vector_arrow.py'),
    (_v('zoomed_inset_manim.mp4'),             'examples/manim/zoomed_inset_manim.py'),
    # ── Examples ─────────────────────────────────────────────────────
    (_v('animations_color.mp4'),               'examples/animations_color.py'),
    (_v('animations_counters.mp4'),            'examples/animations_counters.py'),
    (_v('animations_creation.mp4'),            'examples/animations_creation.py'),
    (_v('animations_effects.mp4'),             'examples/animations_effects.py'),
    (_v('animations_movement.mp4'),            'examples/animations_movement.py'),
    (_v('animations_text.mp4'),                'examples/animations_text.py'),
    (_v('animations_vcollection.mp4'),         'examples/animations_vcollection.py'),
    (_v('automaton_example.mp4'),              'examples/automaton_example.py'),
    (_v('axes_annotations.svg'),               'examples/axes_annotations.py'),
    (_v('axes_formatters.svg'),                'examples/axes_formatters.py'),
    (_v('axes_overlays.svg'),                  'examples/axes_overlays.py'),
    (_v('axes_plot_types.svg'),                'examples/axes_plot_types.py'),
    (_v('axes_zoom.mp4'),                      'examples/axes_zoom.py'),
    (_v('chart_methods.mp4'),                  'examples/chart_methods.py'),
    (_v('chart_types.svg'),                    'examples/chart_types.py'),
    (_v('chess_example.mp4'),                  'examples/chess_example.py'),
    (_v('circuit_components.svg'),             'examples/circuit_components.py'),
    (_v('code_explanation.svg'),               'examples/code_explanation.py'),
    (_v('code_highlight.mp4'),                 'examples/code_highlight.py'),
    (_v('complex_plane_example.svg'),          'examples/complex_plane_example.py'),
    (_v('data_structure_methods.mp4'),         'examples/data_structure_methods.py'),
    (_v('diagram_types.svg'),                  'examples/diagram_types.py'),
    (_v('focus_camera_example.mp4'),           'examples/focus_camera_example.py'),
    (_v('gradient_example.svg'),               'examples/gradient_example.py'),
    (_v('graph_animated.mp4'),                 'examples/graph_animated.py'),
    (_v('graph_structures.mp4'),               'examples/graph_structures.py'),
    (_v('heart.mp4'),                          'examples/heart.py'),
    (_v('morphing_example.mp4'),               'examples/morphing_example.py'),
    (_v('neural_network_example.mp4'),         'examples/neural_network_example.py'),
    (_v('number_plane_transform_example.mp4'), 'examples/number_plane_transform_example.py'),
    (_v('numberline_features.mp4'),            'examples/numberline_features.py'),
    (_v('parametric_curve_example.svg'),       'examples/parametric_curve_example.py'),
    (_v('pendulum_example.mp4'),               'examples/pendulum_example.py'),
    (_v('physics_bouncing_objects.mp4'),         'examples/physics_bouncing_objects.py'),
    (_v('physics_cloth.mp4'),                  'examples/physics_cloth.py'),
    (_v('physics_spring.mp4'),                 'examples/physics_spring.py'),
    (_v('polar_plot_example.svg'),             'examples/polar_plot_example.py'),
    (_v('shapes.svg'),                         'examples/shapes.py'),
    (_v('speed_and_sections.mp4'),             'examples/speed_and_sections.py'),
    (_v('spiral.mp4'),                         'examples/spiral.py'),
    (_v('table_highlight_example.mp4'),        'examples/table_highlight_example.py'),
    (_v('threed.svg'),                         'examples/threed.py'),
    (_v('transform_from_copy_example.mp4'),    'examples/transform_from_copy_example.py'),
    (_v('ui_widgets.svg'),                     'examples/ui_widgets.py'),
    (_v('vector_fields.svg'),                  'examples/vector_fields.py'),
    # ── Advanced examples ────────────────────────────────────────────
    (_v('animated_3d_ripple.mp4'),             'examples/advanced/animated_3d_ripple.py'),
    (_v('axes_graphing.mp4'),                  'examples/advanced/axes_graphing.py'),
    (_v('boolean_ops_demo.mp4'),               'examples/advanced/boolean_ops_demo.py'),
    (_v('cutout_convexhull.mp4'),              'examples/advanced/cutout_convexhull.py'),
    (_v('colliding_blocks.mp4'),               'examples/advanced/colliding_blocks.py'),
    (_v('color_theory.mp4'),                   'examples/advanced/color_theory.py'),
    (_v('convolutions.mp4'),                   'examples/advanced/convolutions.py'),
    (_v('double_pendulum.mp4'),                'examples/advanced/double_pendulum.py'),
    (_v('easing_showcase.mp4'),                'examples/advanced/easing_showcase.py'),
    (_v('fibonacci_spiral.mp4'),               'examples/advanced/fibonacci_spiral.py'),
    (_v('fourier_circles.mp4'),                'examples/advanced/fourier_circles.py'),
    (_v('galton_board.mp4'),                   'examples/advanced/galton_board.py'),
    (_v('geometry_showcase.mp4'),              'examples/advanced/geometry_showcase.py'),
    (_v('mandelbrot_zoom.mp4'),                'examples/advanced/mandelbrot_zoom.py'),
    (_v('maurer_rose.mp4'),                    'examples/advanced/maurer_rose.py'),
    (_v('spring_mass.mp4'),                    'examples/advanced/spring_mass.py'),
    (_v('threed_primitives.mp4'),              'examples/advanced/threed_primitives.py'),
    (_v('zoomed_inset.svg'),                   'examples/advanced/zoomed_inset.py'),
    # ── Reference examples (docs admonitions) ──────────────────────────
    # vobject
    (_v('shift.mp4'),                          'examples/reference/shift.py'),
    (_v('fadein.mp4'),                         'examples/reference/fadein.py'),
    (_v('indicate.mp4'),                       'examples/reference/indicate.py'),
    (_v('orbit.mp4'),                          'examples/reference/orbit.py'),
    (_v('along_path.mp4'),                     'examples/reference/along_path.py'),
    (_v('trace_path.mp4'),                     'examples/reference/trace_path.py'),
    (_v('save_restore.mp4'),                   'examples/reference/save_restore.py'),
    (_v('updater.mp4'),                        'examples/reference/updater.py'),
    (_v('ref_indicate.mp4'),                   'examples/reference/ref_indicate.py'),
    (_v('ref_flash.mp4'),                      'examples/reference/ref_flash.py'),
    (_v('ref_pulse.mp4'),                      'examples/reference/ref_pulse.py'),
    (_v('ref_pulsate.mp4'),                    'examples/reference/ref_pulsate.py'),
    (_v('ref_wiggle.mp4'),                     'examples/reference/ref_wiggle.py'),
    (_v('ref_circumscribe.mp4'),               'examples/reference/ref_circumscribe.py'),
    (_v('ref_bounce.mp4'),                     'examples/reference/ref_bounce.py'),
    (_v('ref_spiral_in.mp4'),                  'examples/reference/ref_spiral_in.py'),
    (_v('ref_spring.mp4'),                     'examples/reference/ref_spring.py'),
    (_v('ref_rubber_band.mp4'),                'examples/reference/ref_rubber_band.py'),
    # shapes
    (_v('circle.svg'),                         'examples/reference/circle.py'),
    (_v('polygon.svg'),                        'examples/reference/polygon.py'),
    (_v('star.svg'),                           'examples/reference/star.py'),
    (_v('arc.svg'),                            'examples/reference/arc.py'),
    (_v('ref_ellipse.svg'),                    'examples/reference/ref_ellipse.py'),
    (_v('ref_circle.svg'),                     'examples/reference/ref_circle.py'),
    (_v('ref_dot.svg'),                        'examples/reference/ref_dot.py'),
    (_v('ref_square.svg'),                     'examples/reference/ref_square.py'),
    (_v('ref_lines.svg'),                      'examples/reference/ref_lines.py'),
    (_v('ref_rectangle.svg'),                  'examples/reference/ref_rectangle.py'),
    (_v('ref_rounded_rect.svg'),               'examples/reference/ref_rounded_rect.py'),
    (_v('ref_line.svg'),                       'examples/reference/ref_line.py'),
    (_v('ref_dashed_line.svg'),                'examples/reference/ref_dashed_line.py'),
    (_v('ref_regular_polygon.svg'),            'examples/reference/ref_regular_polygon.py'),
    (_v('ref_star_shape.svg'),                 'examples/reference/ref_star_shape.py'),
    (_v('ref_arc_shape.svg'),                  'examples/reference/ref_arc_shape.py'),
    (_v('ref_wedge.svg'),                      'examples/reference/ref_wedge.py'),
    (_v('ref_annulus.svg'),                    'examples/reference/ref_annulus.py'),
    (_v('ref_cross.svg'),                      'examples/reference/ref_cross.py'),
    (_v('ref_angle.svg'),                      'examples/reference/ref_angle.py'),
    (_v('ref_text.svg'),                       'examples/reference/ref_text.py'),
    (_v('ref_polygon.svg'),                    'examples/reference/ref_polygon.py'),
    (_v('ref_path.svg'),                       'examples/reference/ref_path.py'),
    (_v('ref_function_graph.svg'),             'examples/reference/ref_function_graph.py'),
    # text
    (_v('typewrite.mp4'),                      'examples/reference/typewrite.py'),
    (_v('scramble.mp4'),                       'examples/reference/scramble.py'),
    (_v('tex.mp4'),                            'examples/reference/tex.py'),
    (_v('ref_count_anim.mp4'),                 'examples/reference/ref_count_anim.py'),
    (_v('ref_value_tracker.mp4'),              'examples/reference/ref_value_tracker.py'),
    (_v('ref_animated_integer.mp4'),           'examples/reference/ref_animated_integer.py'),
    (_v('ref_multiline_latex.svg'),            'examples/reference/ref_multiline_latex.py'),
    (_v('ref_tex_counter.mp4'),               'examples/reference/ref_tex_counter.py'),
    (_v('ref_paragraph.svg'),                  'examples/reference/ref_paragraph.py'),
    (_v('ref_bulleted_list.svg'),              'examples/reference/ref_bulleted_list.py'),
    (_v('ref_numbered_list.svg'),              'examples/reference/ref_numbered_list.py'),
    # collections
    (_v('arrange.mp4'),                        'examples/reference/arrange.py'),
    (_v('stagger.mp4'),                        'examples/reference/stagger.py'),
    (_v('array.mp4'),                          'examples/reference/array_example.py'),
    (_v('ref_spread.svg'),                     'examples/reference/ref_spread.py'),
    (_v('ref_morph.mp4'),                      'examples/reference/ref_morph.py'),
    (_v('ref_arrow.svg'),                      'examples/reference/ref_arrow.py'),
    (_v('ref_double_arrow.svg'),               'examples/reference/ref_double_arrow.py'),
    (_v('ref_curved_arrow.svg'),               'examples/reference/ref_curved_arrow.py'),
    (_v('ref_brace.svg'),                      'examples/reference/ref_brace.py'),
    (_v('ref_table.svg'),                      'examples/reference/ref_table.py'),
    (_v('ref_matrix.svg'),                     'examples/reference/ref_matrix.py'),
    (_v('ref_swap_children.mp4'),              'examples/reference/ref_swap_children.py'),
    (_v('ref_shuffle_animate.mp4'),            'examples/reference/ref_shuffle_animate.py'),
    # graphing
    (_v('graph_plot.svg'),                     'examples/reference/graph_plot.py'),
    (_v('tangent_line.mp4'),                   'examples/reference/tangent_line.py'),
    (_v('numberline.svg'),                     'examples/reference/numberline.py'),
    # charts
    (_v('piechart.svg'),                       'examples/reference/piechart.py'),
    (_v('barchart.mp4'),                       'examples/reference/barchart.py'),
    (_v('ref_donut_chart.svg'),                'examples/reference/ref_donut_chart.py'),
    (_v('ref_radar_chart.svg'),                'examples/reference/ref_radar_chart.py'),
    (_v('ref_waterfall.svg'),                  'examples/reference/ref_waterfall.py'),
    (_v('ref_gantt.svg'),                      'examples/reference/ref_gantt.py'),
    (_v('ref_gauge.svg'),                      'examples/reference/ref_gauge.py'),
    (_v('ref_box_plot.svg'),                   'examples/reference/ref_box_plot.py'),
    (_v('ref_progress_bar.svg'),               'examples/reference/ref_progress_bar.py'),
    (_v('ref_matrix_heatmap.svg'),             'examples/reference/ref_matrix_heatmap.py'),
    # diagrams
    (_v('tree.svg'),                           'examples/reference/tree.py'),
    (_v('flowchart.svg'),                      'examples/reference/flowchart.py'),
    (_v('ref_periodic_table.svg'),              'examples/reference/ref_periodic_table.py'),
    (_v('ref_bohr_carbon.svg'),               'examples/reference/ref_bohr_carbon.py'),
    (_v('ref_chessboard.svg'),                 'examples/reference/ref_chessboard.py'),
    (_v('ref_automaton.svg'),                  'examples/reference/ref_automaton.py'),
    (_v('ref_network_graph.svg'),              'examples/reference/ref_network_graph.py'),
    (_v('ref_venn.svg'),                       'examples/reference/ref_venn.py'),
    (_v('ref_org_chart.svg'),                  'examples/reference/ref_org_chart.py'),
    (_v('ref_mind_map.svg'),                   'examples/reference/ref_mind_map.py'),
    (_v('ref_timeline.svg'),                   'examples/reference/ref_timeline.py'),
    # science
    (_v('pendulum.mp4'),                       'examples/reference/pendulum.py'),
    (_v('neuralnet.mp4'),                      'examples/reference/neuralnet.py'),
    (_v('ref_molecule.svg'),                   'examples/reference/ref_molecule.py'),
    (_v('ref_standing_wave.svg'),              'examples/reference/ref_standing_wave.py'),
    (_v('ref_lens.svg'),                       'examples/reference/ref_lens.py'),
    (_v('ref_unit_interval.svg'),              'examples/reference/ref_unit_interval.py'),
    # threed
    (_v('3d_surface.mp4'),                     'examples/reference/3d_surface.py'),
    (_v('3d_primitives.svg'),                  'examples/reference/3d_primitives.py'),
    (_v('ref_3d_axes.svg'),                    'examples/reference/ref_3d_axes.py'),
    (_v('ref_3d_sphere.svg'),                  'examples/reference/ref_3d_sphere.py'),
    (_v('ref_3d_cube.svg'),                    'examples/reference/ref_3d_cube.py'),
    (_v('ref_3d_torus.svg'),                   'examples/reference/ref_3d_torus.py'),
    # svg_utils
    (_v('boolean_ops.svg'),                    'examples/reference/boolean_ops.py'),
    # physics
    (_v('physics_bounce.mp4'),                 'examples/reference/physics_bounce.py'),
    (_v('ref_physics_cloth.mp4'),              'examples/reference/ref_physics_cloth.py'),
    (_v('ref_physics_spring.mp4'),             'examples/reference/ref_physics_spring.py'),
    # utilities
    (_v('gradient.svg'),                       'examples/reference/gradient.py'),
    (_v('ref_counterclockwise_morph.mp4'),     'examples/reference/ref_counterclockwise_morph.py'),
    # graphing (additional)
    (_v('ref_axes_basic.svg'),                 'examples/reference/ref_axes_basic.py'),
    (_v('ref_number_plane.svg'),               'examples/reference/ref_number_plane.py'),
    (_v('ref_polar_axes.svg'),                 'examples/reference/ref_polar_axes.py'),
    # ui
    (_v('ref_title.svg'),                      'examples/reference/ref_title.py'),
    (_v('ref_variable.svg'),                   'examples/reference/ref_variable.py'),
    (_v('ref_underline.svg'),                  'examples/reference/ref_underline.py'),
    (_v('ref_code.svg'),                       'examples/reference/ref_code.py'),
    (_v('ref_label.svg'),                      'examples/reference/ref_label.py'),
    (_v('ref_labeled_line.svg'),               'examples/reference/ref_labeled_line.py'),
    (_v('ref_labeled_arrow.svg'),              'examples/reference/ref_labeled_arrow.py'),
    (_v('ref_callout.svg'),                    'examples/reference/ref_callout.py'),
    (_v('ref_dimension_line.svg'),             'examples/reference/ref_dimension_line.py'),
    (_v('ref_tooltip.svg'),                    'examples/reference/ref_tooltip.py'),
    (_v('ref_textbox.svg'),                    'examples/reference/ref_textbox.py'),
    (_v('ref_bracket.svg'),                    'examples/reference/ref_bracket.py'),
    (_v('ref_icon_grid.svg'),                  'examples/reference/ref_icon_grid.py'),
    (_v('ref_speech_bubble.svg'),              'examples/reference/ref_speech_bubble.py'),
    (_v('ref_badge.svg'),                      'examples/reference/ref_badge.py'),
    (_v('ref_divider.svg'),                    'examples/reference/ref_divider.py'),
    (_v('ref_checklist.svg'),                  'examples/reference/ref_checklist.py'),
    (_v('ref_stepper.svg'),                    'examples/reference/ref_stepper.py'),
    (_v('ref_tag_cloud.svg'),                  'examples/reference/ref_tag_cloud.py'),
    (_v('ref_status_indicator.svg'),           'examples/reference/ref_status_indicator.py'),
    (_v('ref_meter.svg'),                      'examples/reference/ref_meter.py'),
    (_v('ref_breadcrumb.svg'),                 'examples/reference/ref_breadcrumb.py'),
    (_v('ref_countdown.svg'),                  'examples/reference/ref_countdown.py'),
    (_v('ref_filmstrip.svg'),                  'examples/reference/ref_filmstrip.py'),
    # canvas
    (_v('ref_canvas_basic.svg'),               'examples/reference/ref_canvas_basic.py'),
    (_v('ref_camera_zoom.mp4'),                'examples/reference/ref_camera_zoom.py'),
    (_v('ref_camera_follow.mp4'),              'examples/reference/ref_camera_follow.py'),
    # attributes
    (_v('attr_move_to.mp4'),                   'examples/reference/attr_move_to.py'),
    (_v('attr_easing.mp4'),                    'examples/reference/attr_easing.py'),
    (_v('attr_composition.mp4'),               'examples/reference/attr_composition.py'),
    (_v('attr_color.mp4'),                     'examples/reference/attr_color.py'),
    # animation
    (_v('anim_sections.mp4'),                  'examples/reference/anim_sections.py'),
    (_v('anim_speed.mp4'),                     'examples/reference/anim_speed.py'),
    (_v('anim_export.svg'),                    'examples/reference/anim_export.py'),
    # graphing (additional)
    (_v('graph_basic.svg'),                    'examples/reference/graphing_basic.py'),
    (_v('graph_zoom.mp4'),                     'examples/reference/graphing_zoom.py'),
    (_v('graph_animated_ref.mp4'),             'examples/reference/graphing_animated.py'),
    (_v('graph_functiongraph.mp4'),            'examples/reference/graphing_functiongraph.py'),
    (_v('graph_scatter.svg'),                  'examples/reference/graph_scatter.py'),
    (_v('graph_calculus.svg'),                 'examples/reference/graph_calculus.py'),
    (_v('graph_vector_field.svg'),             'examples/reference/graph_vector_field.py'),
    (_v('graph_histogram.svg'),                'examples/reference/graph_histogram.py'),
    (_v('graph_donut_radar.svg'),              'examples/reference/graph_donut_radar.py'),
    # tutorial
    (_v('tutorial_spiral.mp4'),                'examples/reference/tutorial_spiral.py'),
    (_v('tutorial_shapes.mp4'),                'examples/reference/tutorial_shapes.py'),
    (_v('tutorial_timing.mp4'),                'examples/reference/tutorial_timing.py'),
    # ── Parameter diagrams ─────────────────────────────────────────────
    (_i('coordinate_system.svg'),              'examples/reference/coordinate_system.py'),
    (_i('circle_params.svg'),                  'examples/reference/circle_params.py'),
    (_i('ellipse_params.svg'),                 'examples/reference/ellipse_params.py'),
    (_i('rectangle_params.svg'),               'examples/reference/rectangle_params.py'),
    (_i('line_params.svg'),                    'examples/reference/line_params.py'),
    (_i('regular_polygon_params.svg'),         'examples/reference/regular_polygon_params.py'),
    (_i('star_params.svg'),                    'examples/reference/star_params.py'),
    (_i('arc_params.svg'),                     'examples/reference/arc_params.py'),
    (_i('wedge_params.svg'),                   'examples/reference/wedge_params.py'),
    (_i('annulus_params.svg'),                 'examples/reference/annulus_params.py'),
    (_i('arrow_params.svg'),                   'examples/reference/arrow_params.py'),
    (_i('curved_arrow_params.svg'),            'examples/reference/curved_arrow_params.py'),
    (_i('brace_params.svg'),                   'examples/reference/brace_params.py'),
    (_i('edges.svg'),                          'examples/reference/edges.py'),
    (_i('next_to.svg'),                        'examples/reference/next_to.py'),
    (_i('arrange.svg'),                        'examples/reference/arrange_layout.py'),
    (_i('axes_anatomy.svg'),                   'examples/reference/axes_anatomy.py'),
    (_i('numberline_params.svg'),              'examples/reference/numberline_params.py'),
    (_i('easing_curves.svg'),                  'examples/reference/easing_curves.py'),
    (_i('angle_params.svg'),                   'examples/reference/angle_params.py'),
    # ── Additional reference examples (batch 2) ─────────────────────────
    # vobject effects
    (_v('ref_wave.mp4'),                       'examples/reference/ref_wave.py'),
    (_v('ref_show_passing_flash.mp4'),         'examples/reference/ref_show_passing_flash.py'),
    (_v('ref_ripple.mp4'),                     'examples/reference/ref_ripple.py'),
    (_v('ref_shake.mp4'),                      'examples/reference/ref_shake.py'),
    (_v('ref_float_anim.mp4'),                 'examples/reference/ref_float_anim.py'),
    (_v('ref_trail.mp4'),                      'examples/reference/ref_trail.py'),
    (_v('ref_cross_out.mp4'),                  'examples/reference/ref_cross_out.py'),
    (_v('ref_shimmer.mp4'),                    'examples/reference/ref_shimmer.py'),
    (_v('ref_swing.mp4'),                      'examples/reference/ref_swing.py'),
    (_v('ref_undulate.mp4'),                   'examples/reference/ref_undulate.py'),
    (_v('ref_glitch.mp4'),                     'examples/reference/ref_glitch.py'),
    (_v('ref_highlight_border.mp4'),           'examples/reference/ref_highlight_border.py'),
    (_v('ref_flash_color.mp4'),                'examples/reference/ref_flash_color.py'),
    (_v('ref_pulse_color.mp4'),                'examples/reference/ref_pulse_color.py'),
    (_v('ref_pulse_outline.mp4'),              'examples/reference/ref_pulse_outline.py'),
    (_v('ref_emphasize.mp4'),                  'examples/reference/ref_emphasize.py'),
    (_v('ref_breathe.mp4'),                    'examples/reference/ref_breathe.py'),
    (_v('ref_heartbeat.mp4'),                  'examples/reference/ref_heartbeat.py'),
    (_v('ref_blink.mp4'),                      'examples/reference/ref_blink.py'),
    # vobject advanced effects
    (_v('ref_apply_wave.mp4'),                 'examples/reference/ref_apply_wave.py'),
    (_v('ref_telegraph.mp4'),                  'examples/reference/ref_telegraph.py'),
    (_v('ref_skate.mp4'),                      'examples/reference/ref_skate.py'),
    (_v('ref_slingshot.mp4'),                  'examples/reference/ref_slingshot.py'),
    (_v('ref_elastic_bounce.mp4'),             'examples/reference/ref_elastic_bounce.py'),
    (_v('ref_morph_scale.mp4'),                'examples/reference/ref_morph_scale.py'),
    (_v('ref_unfold.mp4'),                     'examples/reference/ref_unfold.py'),
    (_v('ref_stamp_trail.mp4'),                'examples/reference/ref_stamp_trail.py'),
    (_v('ref_flicker.mp4'),                    'examples/reference/ref_flicker.py'),
    (_v('ref_strobe.mp4'),                     'examples/reference/ref_strobe.py'),
    (_v('ref_wobble.mp4'),                     'examples/reference/ref_wobble.py'),
    (_v('ref_focus_zoom.mp4'),                 'examples/reference/ref_focus_zoom.py'),
    # collections additional
    (_v('ref_stagger.mp4'),                    'examples/reference/ref_stagger.py'),
    (_v('ref_wave_anim.mp4'),                  'examples/reference/ref_wave_anim.py'),
    (_v('ref_stagger_fadein.mp4'),             'examples/reference/ref_stagger_fadein.py'),
    (_v('ref_write_collection.mp4'),           'examples/reference/ref_write_collection.py'),
    (_v('ref_reveal.mp4'),                     'examples/reference/ref_reveal.py'),
    (_v('ref_distribute_radial.svg'),          'examples/reference/ref_distribute_radial.py'),
    (_v('ref_vector_on_axes.svg'),             'examples/reference/ref_vector_on_axes.py'),
    (_v('ref_morph2.mp4'),                     'examples/reference/ref_morph2.py'),
    # graphing additional
    (_v('ref_sine_curve.svg'),                 'examples/reference/ref_sine_curve.py'),
    (_v('ref_quadratic_annotations.svg'),      'examples/reference/ref_quadratic_annotations.py'),
    (_v('ref_line_graph_data.svg'),            'examples/reference/ref_line_graph_data.py'),
    (_v('ref_dot_on_curve.mp4'),               'examples/reference/ref_dot_on_curve.py'),
    (_v('ref_shaded_area_sine.svg'),           'examples/reference/ref_shaded_area_sine.py'),
    (_v('ref_area_between_curves.svg'),        'examples/reference/ref_area_between_curves.py'),
    (_v('ref_riemann_sum.svg'),                'examples/reference/ref_riemann_sum.py'),
    (_v('ref_legend_curves.svg'),              'examples/reference/ref_legend_curves.py'),
    (_v('ref_animated_axis_range.mp4'),        'examples/reference/ref_animated_axis_range.py'),
    (_v('ref_incremental_plot.mp4'),           'examples/reference/ref_incremental_plot.py'),
    (_v('ref_damped_sine.svg'),                'examples/reference/ref_damped_sine.py'),
    (_v('ref_parametric_spiral.svg'),          'examples/reference/ref_parametric_spiral.py'),
    (_v('ref_complex_transform.svg'),          'examples/reference/ref_complex_transform.py'),
    (_v('ref_labelled_complex.svg'),           'examples/reference/ref_labelled_complex.py'),
    (_v('ref_animated_pie.mp4'),               'examples/reference/ref_animated_pie.py'),
    (_v('ref_bar_sort.mp4'),                   'examples/reference/ref_bar_sort.py'),
    (_v('ref_pi_ticks.svg'),                   'examples/reference/ref_pi_ticks.py'),
    # charts additional
    (_v('ref_sankey.svg'),                     'examples/reference/ref_sankey.py'),
    (_v('ref_funnel.svg'),                     'examples/reference/ref_funnel.py'),
    (_v('ref_treemap.svg'),                    'examples/reference/ref_treemap.py'),
    (_v('ref_sample_space.svg'),               'examples/reference/ref_sample_space.py'),
    (_v('ref_sparkline.svg'),                  'examples/reference/ref_sparkline.py'),
    (_v('ref_kpi_card.svg'),                   'examples/reference/ref_kpi_card.py'),
    (_v('ref_bullet_chart.svg'),               'examples/reference/ref_bullet_chart.py'),
    (_v('ref_calendar_heatmap.svg'),           'examples/reference/ref_calendar_heatmap.py'),
    (_v('ref_waffle.svg'),                     'examples/reference/ref_waffle.py'),
    (_v('ref_circular_progress.svg'),          'examples/reference/ref_circular_progress.py'),
    (_v('ref_scoreboard.svg'),                 'examples/reference/ref_scoreboard.py'),
    # 3D additional
    (_v('ref_3d_ambient_rotation.mp4'),        'examples/reference/ref_3d_ambient_rotation.py'),
    (_v('ref_3d_arrow.svg'),                   'examples/reference/ref_3d_arrow.py'),
    (_v('ref_3d_camera_rotation.mp4'),         'examples/reference/ref_3d_camera_rotation.py'),
    (_v('ref_3d_checkerboard.svg'),            'examples/reference/ref_3d_checkerboard.py'),
    (_v('ref_3d_cone.svg'),                    'examples/reference/ref_3d_cone.py'),
    (_v('ref_3d_cylinder.svg'),                'examples/reference/ref_3d_cylinder.py'),
    (_v('ref_3d_dodecahedron.svg'),            'examples/reference/ref_3d_dodecahedron.py'),
    (_v('ref_3d_dot.svg'),                     'examples/reference/ref_3d_dot.py'),
    (_v('ref_3d_function_curve.svg'),          'examples/reference/ref_3d_function_curve.py'),
    (_v('ref_3d_gaussian.svg'),                'examples/reference/ref_3d_gaussian.py'),
    (_v('ref_3d_heightmap.svg'),               'examples/reference/ref_3d_heightmap.py'),
    (_v('ref_3d_helix.svg'),                   'examples/reference/ref_3d_helix.py'),
    (_v('ref_3d_icosahedron.svg'),             'examples/reference/ref_3d_icosahedron.py'),
    (_v('ref_3d_light_direction.svg'),         'examples/reference/ref_3d_light_direction.py'),
    (_v('ref_3d_line.svg'),                    'examples/reference/ref_3d_line.py'),
    (_v('ref_3d_mobius.svg'),                   'examples/reference/ref_3d_mobius.py'),
    (_v('ref_3d_octahedron.svg'),              'examples/reference/ref_3d_octahedron.py'),
    (_v('ref_3d_primitives.svg'),              'examples/reference/ref_3d_primitives.py'),
    (_v('ref_3d_prism.svg'),                   'examples/reference/ref_3d_prism.py'),
    (_v('ref_3d_sphere_surface.svg'),          'examples/reference/ref_3d_sphere_surface.py'),
    (_v('ref_3d_tetrahedron.svg'),             'examples/reference/ref_3d_tetrahedron.py'),
    (_v('ref_3d_text.svg'),                    'examples/reference/ref_3d_text.py'),
    (_v('ref_3d_wireframe.svg'),               'examples/reference/ref_3d_wireframe.py'),
    (_v('ref_3d_zoom.mp4'),                    'examples/reference/ref_3d_zoom.py'),
    # svg_utils additional
    (_v('ref_angle_label.svg'),                'examples/reference/ref_angle_label.py'),
    (_v('ref_brace_between.svg'),              'examples/reference/ref_brace_between.py'),
    (_v('ref_clip_path.svg'),                  'examples/reference/ref_clip_path.py'),
    (_v('ref_color_cycle_border.mp4'),         'examples/reference/ref_color_cycle_border.py'),
    (_v('ref_convex_hull.svg'),                'examples/reference/ref_convex_hull.py'),
    (_v('ref_cross_mark.svg'),                 'examples/reference/ref_cross_mark.py'),
    (_v('ref_cutout_overlay.svg'),             'examples/reference/ref_cutout_overlay.py'),
    (_v('ref_drop_shadow.svg'),                'examples/reference/ref_drop_shadow.py'),
    (_v('ref_gaussian_blur.svg'),              'examples/reference/ref_gaussian_blur.py'),
    (_v('ref_right_angle.svg'),                'examples/reference/ref_right_angle.py'),
    (_v('ref_spotlight.mp4'),                  'examples/reference/ref_spotlight.py'),
    (_v('ref_stream_lines.svg'),               'examples/reference/ref_stream_lines.py'),
    (_v('ref_vector_field.svg'),               'examples/reference/ref_vector_field.py'),
    (_v('ref_zoomed_inset_animated.mp4'),       'examples/reference/ref_zoomed_inset_animated.py'),
    # physics additional
    (_v('ref_physics_bounce.mp4'),             'examples/reference/ref_physics_bounce.py'),
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

LIB_DIR = 'vectormation'

def _lib_mtime():
    """Return the newest mtime among library source files."""
    newest = 0
    for f in os.listdir(LIB_DIR):
        if f.endswith('.py'):
            newest = max(newest, os.path.getmtime(os.path.join(LIB_DIR, f)))
    return newest


def _needs_rebuild(output, script, lib_mtime):
    if not os.path.exists(output):
        return True
    out_mtime = os.path.getmtime(output)
    if os.path.exists(script) and os.path.getmtime(script) > out_mtime:
        return True
    return lib_mtime > out_mtime


def _run_one(script):
    """Run a single script with --for-docs.  Returns (script, ok, stderr)."""
    try:
        r = subprocess.run(
            [sys.executable, script, '--for-docs'],
            capture_output=True, text=True,
        )
        return (script, r.returncode == 0, r.stderr)
    except Exception as exc:
        return (script, False, str(exc))

# ---------------------------------------------------------------------------
# Progress display
# ---------------------------------------------------------------------------

BAR_WIDTH = 30
_CLEAR_LINE = '\033[2K'
_PREV_LINES = 0  # how many lines the last _draw wrote


def _draw(done, total, building, t0, failed):
    """Redraw the progress display.

    *building* is a set of asset names currently in-flight.
    """
    global _PREV_LINES

    # Move cursor up to overwrite previous output.
    if _PREV_LINES:
        sys.stderr.write(f'\033[{_PREV_LINES}A')

    lines = []

    # ── Bar line ──────────────────────────────────────────────────────
    frac = done / max(total, 1)
    filled = int(BAR_WIDTH * frac)
    bar = '\u2588' * filled + '\u2591' * (BAR_WIDTH - filled)
    elapsed = time.monotonic() - t0
    if 0 < frac < 1:
        eta = elapsed / frac * (1 - frac)
        time_str = f'{elapsed:.0f}s  eta {eta:.0f}s'
    else:
        time_str = f'{elapsed:.0f}s'
    fail_str = f'  \033[31m{failed} failed\033[0m' if failed else ''
    lines.append(
        f'{_CLEAR_LINE}\033[36mBuilding assets\033[0m  '
        f'|{bar}| {done}/{total}  {time_str}{fail_str}'
    )

    # ── Building line(s) ──────────────────────────────────────────────
    if building and len(building) <= 6:
        names = ', '.join(sorted(building))
        lines.append(f'{_CLEAR_LINE}  \033[33mbuilding\033[0m  {names}')

    sys.stderr.write('\n'.join(lines) + '\n')
    sys.stderr.flush()
    _PREV_LINES = len(lines)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='Build documentation assets')
    parser.add_argument('-j', '--jobs', type=int,
                        default=os.cpu_count() or 4,
                        help='Number of parallel jobs (default: nproc)')
    parser.add_argument('--force', action='store_true',
                        help='Rebuild all assets regardless of timestamps')
    args = parser.parse_args()

    # We must run from the repo root.
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)

    os.makedirs(VIDEODIR, exist_ok=True)
    os.makedirs(IMGDIR, exist_ok=True)

    lib_mt = _lib_mtime()

    if args.force:
        todo = list(ASSETS)
    else:
        todo = [(o, s) for o, s in ASSETS
                if os.path.exists(s) and _needs_rebuild(o, s, lib_mt)]

    if not todo:
        sys.stderr.write('All assets up to date.\n')
        return 0

    total = len(todo)
    done = 0
    failed = 0
    failures = []
    building: set[str] = set()
    t0 = time.monotonic()

    _draw(0, total, set(), t0, 0)

    with ProcessPoolExecutor(max_workers=args.jobs) as pool:
        futures = {}
        for output, script in todo:
            name = os.path.basename(output)
            fut = pool.submit(_run_one, script)
            futures[fut] = (name, output)
            building.add(name)

        _draw(done, total, building, t0, failed)

        for future in as_completed(futures):
            name, _ = futures[future]
            _, ok, stderr = future.result()
            building.discard(name)
            done += 1
            if not ok:
                failed += 1
                failures.append((name, stderr))
            _draw(done, total, building, t0, failed)

    # Clear the "building" line once everything is done.
    elapsed = time.monotonic() - t0

    if failures:
        sys.stderr.write(f'\n\033[31m{failed} asset(s) failed:\033[0m\n')
        for name, stderr in failures:
            sys.stderr.write(f'  \033[31m\u2718\033[0m {name}\n')
            # Show last few lines of stderr for context.
            for line in stderr.strip().splitlines()[-3:]:
                sys.stderr.write(f'    {line}\n')
        sys.stderr.write('\n')

    ok_count = total - failed
    sys.stderr.write(
        f'\033[32m\u2714 {ok_count} built\033[0m'
        + (f', \033[31m{failed} failed\033[0m' if failed else '')
        + f' in {elapsed:.1f}s\n'
    )

    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
