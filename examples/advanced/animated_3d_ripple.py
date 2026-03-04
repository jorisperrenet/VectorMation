"""Animated 3D Ripple — demonstrates time-varying surface plots.

A ripple surface z = sin(r - t) * exp(-r^2) animates over time,
showing the wave propagating outward with ambient camera rotation.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import math
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/animated_3d_ripple')
canvas.set_background()

T = 12

# ── Title ────────────────────────────────────────────────────────────
title = TexObject(r'Animated 3D Ripple', x=960, y=55,
                  font_size=44, fill='#ffffff', stroke_width=0, anchor='center', creation=0)
title.fadein(0, 1)

eq = TexObject(r'$z = \sin\!\left(\sqrt{x^2 + y^2} - 3t\right) \cdot e^{-0.1(x^2+y^2)}$',
               x=960, y=125, font_size=72, fill='#aaaaaa',
               stroke_width=0, anchor='center', creation=0)
eq.fadein(0.3, 1.3)

# ── 3D Axes ──────────────────────────────────────────────────────────
axes = ThreeDAxes(
    x_range=(-4, 4), y_range=(-4, 4), z_range=(-1.5, 1.5),
    cx=960, cy=560, scale=110,
    phi=math.radians(65), theta=math.radians(-30),
    show_ticks=True, show_labels=True, show_grid=True,
    x_label='x', y_label='y', z_label='z',
    creation=0,
)
axes.set_light_direction(0.3, -0.5, 0.8)

# ── Time-varying ripple surface ──────────────────────────────────────
def ripple(x, y, time):
    r = math.sqrt(x * x + y * y)
    phase = r - 3 * time
    return math.sin(phase) * math.exp(-0.1 * r * r)

surface = axes.plot_surface(
    ripple,
    u_range=(-4, 4), v_range=(-4, 4),
    resolution=(51, 51),
    fill_color='#58C4DD',
    stroke_color='#225577',
    stroke_width=0.3,
    fill_opacity=0.85,
    creation=0,
)
surface.set_checkerboard('#58C4DD', '#83D9F0')

# ── Camera animation ─────────────────────────────────────────────────
axes.set_camera_orientation(0, 2, phi=math.radians(60), theta=math.radians(-20))
axes.begin_ambient_camera_rotation(start=2, end=T, rate=0.3)

# ── Assemble ─────────────────────────────────────────────────────────
canvas.add(axes)
canvas.add(title, eq)

if args.for_docs:
    canvas.export_video('docs/source/_static/videos/animated_3d_ripple.mp4', fps=30, end=T)
if not args.for_docs:
    canvas.browser_display(start=args.start or 0, end=args.end or T,
    fps=args.fps or 30, port=args.port)
