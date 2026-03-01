"""Polar Curves — beautiful mathematical curves in polar coordinates.

Shows several famous polar curves: circle, cardioid, rose curve,
lemniscate, and spiral, each animated sequentially.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/polar_curves')
canvas.set_background()

# ── Title ────────────────────────────────────────────────────────────────
title = Text(text='Polar Curves', x=960, y=55,
             font_size=44, fill='#fff', stroke_width=0,
             text_anchor='middle', creation=0)
title.fadein(0, 0.5)
canvas.add(title)

# ── Colors ───────────────────────────────────────────────────────────────
colors = ['#58C4DD', '#83C167', '#FF6B6B', '#FFB86C', '#BD93F9']

# ── Curves definition ───────────────────────────────────────────────────
curves = [
    ('Circle: r = 2',        lambda theta: 2),
    ('Cardioid: r = 1 + cos\u03b8', lambda theta: 1 + math.cos(theta)),
    ('Rose: r = 2 cos(3\u03b8)',    lambda theta: 2 * math.cos(3 * theta)),
    ('Lemniscate',            lambda theta: math.sqrt(max(0, 4 * math.cos(2 * theta)))),
    ('Spiral: r = 0.3\u03b8',      lambda theta: 0.3 * theta),
]

# ── Layout: 2 axes on top row, 3 on bottom ──────────────────────────────
plot_w, plot_h = 500, 400
positions = [
    (200, 100),   # top-left
    (1020, 100),  # top-right
    (60, 560),    # bottom-left
    (700, 560),   # bottom-center
    (1340, 560),  # bottom-right
]

t = 0.3
for i, ((label, func), (px, py)) in enumerate(zip(curves, positions)):
    r_max = 3 if i < 4 else 2.5
    ax = Axes(x_range=(-r_max, r_max), y_range=(-r_max, r_max),
              plot_width=plot_w, plot_height=plot_h,
              x=px, y=py, creation=t)
    ax.add_grid()
    ax.fadein(t, t + 0.3)
    canvas.add(ax)

    # Plot the curve
    theta_max = math.tau if i < 4 else 4 * math.pi
    curve = ax.plot_polar(func, theta_range=(0, theta_max),
                          num_points=300, color=colors[i], stroke_width=3)
    curve.create(t + 0.3, t + 1.2)

    # Label
    lbl = Text(text=label, x=px + plot_w / 2, y=py + plot_h + 30,
               font_size=22, fill=colors[i], stroke_width=0,
               text_anchor='middle', creation=t + 0.2)
    lbl.fadein(t + 0.2, t + 0.6)
    canvas.add(lbl)

    t += 0.8

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or 6,
                           fps=args.fps, port=args.port)
