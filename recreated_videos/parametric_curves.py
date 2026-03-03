"""Parametric Curves — classic parametric equations visualized.

Shows Lissajous figures, hypotrochoid, epicycloid, and butterfly curve,
each animating their trace on separate axes.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/parametric_curves')
canvas.set_background()

# ── Title ────────────────────────────────────────────────────────────────
title = Text(text='Parametric Curves', x=960, y=55,
             font_size=44, fill='#fff', stroke_width=0,
             text_anchor='middle', creation=0)
title.fadein(0, 0.5)
canvas.add(title)

colors = ['#58C4DD', '#FF6B6B', '#83C167', '#FFB86C']

# ── Curve definitions ───────────────────────────────────────────────────
# Lissajous: x = sin(3t), y = sin(2t)
def lissajous(t):
    return (math.sin(3 * t), math.sin(2 * t))

# Hypotrochoid: R=5, r=3, d=3 -> deltoid variant
def hypotrochoid(t):
    R, r, d = 5, 3, 3
    return ((R - r) * math.cos(t) + d * math.cos((R - r) / r * t),
            (R - r) * math.sin(t) - d * math.sin((R - r) / r * t))

# Epicycloid: R=3, r=1 -> 3-cusped
def epicycloid(t):
    R, r = 3, 1
    return ((R + r) * math.cos(t) - r * math.cos((R + r) / r * t),
            (R + r) * math.sin(t) - r * math.sin((R + r) / r * t))

# Butterfly curve
def butterfly(t):
    e = math.exp(math.cos(t)) - 2 * math.cos(4 * t) - math.sin(t / 12) ** 5
    return (math.sin(t) * e, math.cos(t) * e)

curves_data = [
    ('Lissajous (3:2)', lissajous, (-1.5, 1.5), (-1.5, 1.5), (0, math.tau)),
    ('Hypotrochoid', hypotrochoid, (-6, 6), (-6, 6), (0, 2 * math.pi * 3)),
    ('Epicycloid (3-cusp)', epicycloid, (-6, 6), (-6, 6), (0, math.tau)),
    ('Butterfly Curve', butterfly, (-4, 4), (-4, 4), (0, 12 * math.pi)),
]

# 2x2 grid layout
plot_w, plot_h = 700, 400
positions = [
    (100, 100),    # top-left
    (1020, 100),   # top-right
    (100, 570),    # bottom-left
    (1020, 570),   # bottom-right
]

t = 0.3
for i, ((label, func, xr, yr, tr), (px, py)) in enumerate(zip(curves_data, positions)):
    ax = Axes(x_range=xr, y_range=yr,
              plot_width=plot_w, plot_height=plot_h,
              x=px, y=py, creation=t)
    ax.add_grid()
    ax.fadein(t, t + 0.3)
    canvas.add(ax)

    curve = ax.plot_parametric(func, t_range=tr, num_points=500,
                               color=colors[i], stroke_width=2)
    curve.create(t + 0.3, t + 1.5)

    lbl = Text(text=label, x=px + plot_w / 2, y=py - 15,
               font_size=24, fill=colors[i], stroke_width=0,
               text_anchor='middle', creation=t)
    lbl.fadein(t, t + 0.4)
    canvas.add(lbl)

    t += 0.8

canvas.browser_display(start=args.start or 0, end=args.end or 6,
                           fps=args.fps, port=args.port)
