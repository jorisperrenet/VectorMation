"""Parametric 3D surfaces and advanced 3D features demo."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import math
from vectormation.objects import (
    VectorMathAnim, Text, ORIGIN, parse_args,
    ThreeDAxes, Sphere3D, Torus3D,
)

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/parametric_3d')

# Title
title = Text(text='3D Parametric Surfaces', x=ORIGIN[0], y=50,
             font_size=40, fill='#58C4DD', text_anchor='middle')
title.write(0, 0.8)
canvas.add(title)

# ── Section 1: Saddle surface z = x^2 - y^2 ─────────────────────────
label1 = Text(text='z = x² − y² (Saddle)', x=480, y=100,
              font_size=22, fill='#aaa', text_anchor='middle', creation=0.5)
canvas.add(label1)

ax1 = ThreeDAxes(x_range=(-2, 2), y_range=(-2, 2), z_range=(-4, 4),
                 cx=480, cy=400, scale=80, creation=0.5)
ax1.fadein(0.5, 1.0)
canvas.add(ax1)

saddle = ax1.plot_surface(
    lambda x, y: x**2 - y**2,
    resolution=(20, 20),
    fill_color='#4488ff',
    checkerboard_colors=('#4488ff', '#2266cc'),
    fill_opacity=0.8, creation=1.0)

ax1.begin_ambient_camera_rotation(start=1.5, end=6, rate=0.3)

# ── Section 2: Torus ────────────────────────────────────────────────
label2 = Text(text='Torus', x=1440, y=100,
              font_size=22, fill='#aaa', text_anchor='middle', creation=0.5)
canvas.add(label2)

ax2 = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2),
                 cx=1440, cy=400, scale=80, creation=0.5)
ax2.fadein(0.5, 1.0)
canvas.add(ax2)

torus = Torus3D(major_radius=1.5, minor_radius=0.5,
                fill_color='#FF6B6B',
                checkerboard_colors=('#FF6B6B', '#CC4444'))
ax2.add_surface(torus)
ax2.begin_ambient_camera_rotation(start=1.5, end=6, rate=-0.25)

# ── Section 3: Ripple surface z = sin(r)/r ──────────────────────────
label3 = Text(text='z = sin(r)/r (Ripple)', x=480, y=590,
              font_size=22, fill='#aaa', text_anchor='middle', creation=6)
canvas.add(label3)

ax3 = ThreeDAxes(x_range=(-4, 4), y_range=(-4, 4), z_range=(-1, 1.5),
                 cx=480, cy=820, scale=60, creation=6)
ax3.fadein(6, 6.5)
canvas.add(ax3)

def ripple(x, y):
    r = math.hypot(x, y)
    return math.sin(r * 2) / (r + 0.5) if r > 0.01 else 1.0

ax3.plot_surface(ripple, resolution=(25, 25),
                 fill_color='#83C167',
                 checkerboard_colors=('#83C167', '#5A8A40'),
                 creation=6.5)
ax3.set_camera_preset('isometric', start=6.5, end=7)
ax3.begin_ambient_camera_rotation(start=7, end=12, rate=0.2)

# ── Section 4: Sphere with camera orbit ─────────────────────────────
label4 = Text(text='Sphere + Camera Zoom', x=1440, y=590,
              font_size=22, fill='#aaa', text_anchor='middle', creation=6)
canvas.add(label4)

ax4 = ThreeDAxes(x_range=(-2, 2), y_range=(-2, 2), z_range=(-2, 2),
                 cx=1440, cy=820, scale=80, creation=6)
ax4.fadein(6, 6.5)
canvas.add(ax4)

sphere = Sphere3D(radius=1.2, fill_color='#FFFF00',
                  checkerboard_colors=('#FFFF00', '#CCCC00'),
                  resolution=(16, 16))
ax4.add_surface(sphere)
ax4.begin_ambient_camera_rotation(start=6.5, end=12, rate=0.4)
ax4.set_camera_zoom(1.5, start=8, end=10)

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or 12,
                           fps=args.fps, port=args.port)
