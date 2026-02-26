"""Manim equivalent: SineCurveUnitCircle -- sine wave traced from a unit circle."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
import math
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/manim/sine_curve_unit_circle')
canvas.set_background()

ax = Axes(x_range=(-3, 14), y_range=(-1.5, 1.5), equal_aspect=True)
c2p = ax.coords_to_point

RATE, DURATION = 0.5, 4
angle = lambda t: 2 * math.pi * RATE * t
cx, cy = c2p(-1, 0)
unit_px = c2p(1, 0)[0] - c2p(0, 0)[0]

# Sine curve growing from x=0
curve = ax.plot(math.sin, x_range=(0, 0), stroke='#FCE94F')
curve._domain_max.set_onward(0, angle)

# Unit circle at (-1, 0)
circle = Circle(r=unit_px, cx=cx, cy=cy, stroke='red', stroke_width=2, fill_opacity=0)

# Orbiting dot + sine-tracking dot
dot = Dot(fill='#FFFF00')
dot.c.set_onward(0, lambda t: c2p(-1 + math.cos(angle(t)), math.sin(angle(t))))

curve_dot = Dot(fill='#FFFF00', r=5)
curve_dot.c.set_onward(0, lambda t: c2p(angle(t), math.sin(angle(t))))

# Radius line and horizontal connector
radius_line = Line(x1=cx, y1=cy, stroke='#58C4DD', stroke_width=2)
radius_line.p2.set_onward(0, lambda t: dot.c.at_time(t))

h_line = Line(stroke='#FFFF00', stroke_width=2, opacity=0.6)
h_line.p1.set_onward(0, lambda t: dot.c.at_time(t))
h_line.p2.set_onward(0, lambda t: curve_dot.c.at_time(t))

canvas.add_objects(ax, circle, radius_line, h_line, dot, curve_dot)
if args.verbose:
    canvas.export_video('docs/source/_static/videos/sine_curve_unit_circle.mp4',
                         fps=30, end_time=DURATION)
if not args.no_display:
    canvas.browser_display(start_time=0, end_time=DURATION, fps=args.fps,
                           port=args.port, hot_reload=True)
