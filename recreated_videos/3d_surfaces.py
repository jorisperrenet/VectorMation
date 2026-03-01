"""3D Surface Visualizations."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/3d_surfaces')
canvas.set_background()

T = 12

# ── Title ────────────────────────────────────────────────────────────
title = Text(text='Exploring 3D Surfaces', x=960, y=50,
             font_size=46, fill='#ffffff', stroke_width=0,
             text_anchor='middle', creation=0)
title.fadein(0, 1.0)
title.fadeout(10.5, 11.5)

subtitle = Text(text='Waves, Paraboloids & Camera Motion',
                x=960, y=90, font_size=22, fill='#888888',
                stroke_width=0, text_anchor='middle', creation=0)
subtitle.fadein(0.3, 1.3)
subtitle.fadeout(10.5, 11.5)

# ── Equation labels ──────────────────────────────────────────────────
eq1_label = Text(text='z = sin(x) \u00b7 cos(y)', x=140, y=170,
                 font_size=24, fill='#58C4DD', stroke_width=0,
                 text_anchor='start', creation=0)
eq1_label.fadein(1.5, 2.5)
eq1_label.fadeout(6.5, 7.5)

eq2_label = Text(text='z = (x\u00b2 + y\u00b2) / 4', x=140, y=170,
                 font_size=24, fill='#FC6255', stroke_width=0,
                 text_anchor='start', creation=0)
eq2_label.set_opacity(0, 0)
eq2_label.set_opacity(7.5, 8.5, 1.0)
eq2_label.fadeout(10.5, 11.5)

# ── Phase dots ───────────────────────────────────────────────────────
dot1 = Circle(r=6, cx=115, cy=173, fill='#58C4DD',
              stroke_width=0, creation=0)
dot1.fadein(1.5, 2.5)
dot1.fadeout(6.5, 7.5)

dot2 = Circle(r=6, cx=115, cy=173, fill='#FC6255',
              stroke_width=0, creation=0)
dot2.set_opacity(0, 0)
dot2.set_opacity(7.5, 8.5, 1.0)
dot2.fadeout(10.5, 11.5)

# ── 3D Axes ──────────────────────────────────────────────────────────
axes = ThreeDAxes(
    x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2),
    cx=960, cy=560, scale=120,
    phi=math.radians(72), theta=math.radians(-50),
    show_ticks=True, show_labels=True, show_grid=True,
    x_label='x', y_label='y', z_label='z',
    creation=0,
)
axes.set_light_direction(0.3, -0.5, 0.8)

# ── Surface 1: z = sin(x) * cos(y) ──────────────────────────────────
def wave_surface(x, y):
    return math.sin(x) * math.cos(y)

surface1 = axes.plot_surface(
    wave_surface,
    u_range=(-3, 3), v_range=(-3, 3),
    resolution=(32, 32),
    fill_color='#58C4DD',
    stroke_color='#1a5577',
    stroke_width=0.3,
    fill_opacity=0.85,
    creation=0,
)
surface1.set_checkerboard('#58C4DD', '#83D9F0')

# ── Camera animation ─────────────────────────────────────────────────
# 0-1.5s: axes settle in from initial angle
axes.set_camera_orientation(0, 1.5,
                            phi=math.radians(65),
                            theta=math.radians(-30))

# 1.5-6.5s: slow ambient rotation showing the wave surface from all sides
axes.begin_ambient_camera_rotation(start=1.5, end=6.5, rate=0.4)

# 6.5-8s: tilt camera for transition to second surface
axes.set_camera_orientation(6.5, 8.0,
                            phi=math.radians(60),
                            theta=math.radians(50))

# ── Surface 2: z = (x^2 + y^2) / 4  (paraboloid) ────────────────────
def paraboloid(x, y):
    return (x * x + y * y) / 4

surface2 = Surface(
    paraboloid,
    u_range=(-3, 3), v_range=(-3, 3),
    resolution=(28, 28),
    fill_color='#FC6255',
    stroke_color='#772222',
    stroke_width=0.3,
    fill_opacity=0.0,
    creation=0,
)
surface2.set_checkerboard('#FC6255', '#FF8877')
axes.add_surface(surface2)

# Hide surface2 initially, reveal with cross-fade at t=7
surface2.show.set(0, 7.0, False)
surface2.show.set_onward(7.0, True)

# Cross-fade surface2 opacity from 0 to 0.85
_orig_s2_patches = surface2.to_patches
def _fading_s2_patches(axes_ref, time):
    if time < 7.0:
        return []
    frac = min((time - 7.0) / 1.0, 1.0)
    surface2._fill_opacity = 0.85 * frac
    return _orig_s2_patches(axes_ref, time)
surface2.to_patches = _fading_s2_patches

# Fade out surface1 during cross-fade
_orig_s1_patches = surface1.to_patches
def _fading_s1_patches(axes_ref, time):
    if 6.5 <= time <= 7.5:
        frac = max(0, 1.0 - (time - 6.5) / 1.0)
        surface1._fill_opacity = 0.85 * frac
    elif time > 7.5:
        return []
    return _orig_s1_patches(axes_ref, time)
surface1.to_patches = _fading_s1_patches

# 8-12s: continued ambient rotation on the paraboloid
axes.begin_ambient_camera_rotation(start=8.0, end=T, rate=0.35)

# ── 3D curve: highlight the x-axis cross-section of the paraboloid ──
parab_curve = axes.get_graph_3d(
    lambda x: x * x / 4,
    x_range=(-3, 3),
    plane='xz',
    num_points=80,
    stroke='#FFFF00',
    stroke_width=3,
    creation=0,
)
parab_curve.show.set(0, 9.0, False)
parab_curve.show.set_onward(9.0, True)

# Cross-section label
section_label = Text(text='y = 0 slice: z = x\u00b2/4', x=1600, y=170,
                     font_size=20, fill='#FFFF00', stroke_width=0,
                     text_anchor='start', creation=0)
section_label.set_opacity(0, 0)
section_label.set_opacity(9.0, 9.8, 1.0)
section_label.fadeout(10.5, 11.5)

# ── Assemble ─────────────────────────────────────────────────────────
canvas.add(axes)
canvas.add(title, subtitle)
canvas.add(eq1_label, eq2_label)
canvas.add(dot1, dot2)
canvas.add(section_label)

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or T,
                           fps=args.fps, port=args.port)
