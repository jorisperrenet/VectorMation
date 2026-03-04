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
    (_v('zoomed_inset.mp4'),                   'examples/manim/zoomed_inset.py'),
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
    (_v('physics_bouncing_balls.mp4'),         'examples/physics_bouncing_balls.py'),
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
    (_v('zoomed_inset.mp4'),                  'examples/advanced/zoomed_inset.py'),
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
    # shapes
    (_v('circle.svg'),                         'examples/reference/circle.py'),
    (_v('polygon.svg'),                        'examples/reference/polygon.py'),
    (_v('star.svg'),                           'examples/reference/star.py'),
    (_v('arc.svg'),                            'examples/reference/arc.py'),
    # text
    (_v('typewrite.mp4'),                      'examples/reference/typewrite.py'),
    (_v('scramble.mp4'),                       'examples/reference/scramble.py'),
    (_v('tex.mp4'),                            'examples/reference/tex.py'),
    # collections
    (_v('arrange.mp4'),                        'examples/reference/arrange.py'),
    (_v('stagger.mp4'),                        'examples/reference/stagger.py'),
    (_v('array.mp4'),                          'examples/reference/array_example.py'),
    # graphing
    (_v('graph_plot.svg'),                     'examples/reference/graph_plot.py'),
    (_v('tangent_line.mp4'),                   'examples/reference/tangent_line.py'),
    (_v('numberline.svg'),                     'examples/reference/numberline.py'),
    # charts
    (_v('piechart.svg'),                       'examples/reference/piechart.py'),
    (_v('barchart.mp4'),                       'examples/reference/barchart.py'),
    # diagrams
    (_v('tree.svg'),                           'examples/reference/tree.py'),
    (_v('flowchart.svg'),                      'examples/reference/flowchart.py'),
    # science
    (_v('pendulum.mp4'),                       'examples/reference/pendulum.py'),
    (_v('neuralnet.mp4'),                      'examples/reference/neuralnet.py'),
    # threed
    (_v('3d_surface.mp4'),                     'examples/reference/3d_surface.py'),
    (_v('3d_primitives.svg'),                  'examples/reference/3d_primitives.py'),
    # svg_utils
    (_v('boolean_ops.svg'),                    'examples/reference/boolean_ops.py'),
    # physics
    (_v('physics_bounce.mp4'),                 'examples/reference/physics_bounce.py'),
    # utilities
    (_v('gradient.svg'),                       'examples/reference/gradient.py'),
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
    if building:
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
