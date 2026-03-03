"""3D Surface Plot — demonstrates ThreeDAxes, plot_surface, and camera animation.

Shows two mathematical surfaces (a ripple function and a saddle surface)
with animated camera rotation and Lambertian shading.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import math
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/surface_plot_3d')
canvas.set_background()

T = 12

# ── Title ────────────────────────────────────────────────────────────
title = Text(text='3D Surface Plots', x=960, y=55,
             font_size=44, fill='#ffffff', stroke_width=0,
             text_anchor='middle', creation=0)
title.fadein(0, 1)

subtitle = Text(text='Ripple Function & Saddle Surface',
                x=960, y=95, font_size=22, fill='#888888',
                stroke_width=0, text_anchor='middle', creation=0)
subtitle.fadein(0.3, 1.3)

# ── Equation labels ──────────────────────────────────────────────────
eq1 = Text(text='z = sin(\u221a(x\u00b2 + y\u00b2))', x=170, y=180,
           font_size=22, fill='#58C4DD', stroke_width=0,
           text_anchor='start', creation=0)
eq1.fadein(1.0, 2.0)

eq2 = Text(text='z = x\u00b2/4 \u2212 y\u00b2/4', x=170, y=216,
           font_size=22, fill='#FC6255', stroke_width=0,
           text_anchor='start', creation=0)
eq2.set_opacity(0, 0)
eq2.set_opacity(7.5, 8.5, 1.0)

# ── 3D Axes ──────────────────────────────────────────────────────────
axes = ThreeDAxes(
    x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2),
    cx=960, cy=560, scale=120,
    phi=math.radians(70), theta=math.radians(-45),
    show_ticks=True, show_labels=True, show_grid=True,
    x_label='x', y_label='y', z_label='z',
    creation=0,
)
axes.set_light_direction(0.4, -0.6, 0.7)

# ── Surface 1: Ripple function z = sin(sqrt(x^2 + y^2)) ─────────────
def ripple(x, y):
    r = math.sqrt(x * x + y * y)
    return math.sin(r * 1.8) * math.exp(-0.15 * r * r) if r > 0.01 else 0

surface1 = axes.plot_surface(
    ripple,
    u_range=(-3, 3), v_range=(-3, 3),
    resolution=(30, 30),
    fill_color='#58C4DD',
    stroke_color='#225577',
    stroke_width=0.3,
    fill_opacity=0.85,
    creation=0,
)
surface1.set_checkerboard('#58C4DD', '#83D9F0')

# ── Camera animation ─────────────────────────────────────────────────
# 0-1s: initial settling from slightly higher angle
axes.set_camera_orientation(0, 1.5, phi=math.radians(65), theta=math.radians(-30))

# 1.5-7s: slow ambient rotation to show the ripple surface from all sides
axes.begin_ambient_camera_rotation(start=1.5, end=7.0, rate=0.4)

# 7-8s: tilt camera for second surface
axes.set_camera_orientation(7.0, 8.5,
                            phi=math.radians(60),
                            theta=math.radians(45))

# ── Surface 2: Saddle z = x^2/4 - y^2/4 (appears at t=7.5) ─────────
def saddle(x, y):
    return x * x / 4 - y * y / 4

surface2 = Surface(
    saddle,
    u_range=(-3, 3), v_range=(-3, 3),
    resolution=(25, 25),
    fill_color='#FC6255',
    stroke_color='#882222',
    stroke_width=0.3,
    fill_opacity=0.0,
    creation=0,
)
surface2.set_checkerboard('#FC6255', '#FF8877')
axes.add_surface(surface2)

# Hide surface1 and reveal surface2 at t=7.5
surface1.show.set(7.3, 7.8, lambda t: 1 if t < 7.5 else 0)
surface2._fill_opacity_attr = None  # we'll control opacity via show
surface2.show.set(0, 7.5, False)
surface2.show.set_onward(7.5, True)
# Crossfade: ramp surface2 opacity from 0 to 0.85
_orig_to_patches_2 = surface2.to_patches
def _fading_patches_2(axes, time):
    if time < 7.5:
        return []
    frac = min((time - 7.5) / 1.0, 1.0)
    surface2._fill_opacity = 0.85 * frac
    return _orig_to_patches_2(axes, time)
surface2.to_patches = _fading_patches_2

# Fade out surface1 opacity
_orig_to_patches_1 = surface1.to_patches
def _fading_patches_1(axes, time):
    if 7.3 <= time <= 8.0:
        frac = max(0, 1.0 - (time - 7.3) / 0.7)
        surface1._fill_opacity = 0.85 * frac
    elif time > 8.0:
        return []
    return _orig_to_patches_1(axes, time)
surface1.to_patches = _fading_patches_1

# 8.5-12s: ambient rotation on the saddle surface
axes.begin_ambient_camera_rotation(start=8.5, end=T, rate=0.35)

# ── 3D curve on the saddle: highlight the x-axis cross-section ───────
saddle_curve_x = axes.get_graph_3d(
    lambda x: x * x / 4,
    x_range=(-3, 3),
    plane='xz',
    num_points=80,
    stroke='#FFFF00',
    stroke_width=3,
    creation=0,
)
saddle_curve_x.show.set(0, 9.0, False)
saddle_curve_x.show.set_onward(9.0, True)

# ── Label for the cross-section ──────────────────────────────────────
curve_label = Text(text='y = 0 cross-section', x=1650, y=180,
                   font_size=20, fill='#FFFF00', stroke_width=0,
                   text_anchor='start', creation=0)
curve_label.set_opacity(0, 0)
curve_label.set_opacity(9.0, 9.8, 1.0)

# ── Phase indicator dots ─────────────────────────────────────────────
phase1_dot = Circle(r=6, cx=145, cy=183, fill='#58C4DD',
                    stroke_width=0, creation=0)
phase1_dot.fadein(1.0, 2.0)
phase1_dot.fadeout(7.0, 7.8)

phase2_dot = Circle(r=6, cx=145, cy=219, fill='#FC6255',
                    stroke_width=0, creation=0)
phase2_dot.set_opacity(0, 0)
phase2_dot.set_opacity(7.5, 8.5, 1.0)

# ── Assemble ─────────────────────────────────────────────────────────
canvas.add(axes)
canvas.add(title, subtitle, eq1, eq2)
canvas.add(phase1_dot, phase2_dot, curve_label)

canvas.browser_display(start=args.start or 0, end=args.end or T,
                           fps=args.fps, port=args.port)
