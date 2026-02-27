"""Lorenz Attractor — recreation of 3b1b's lorenz.py demo.

Multiple trajectories with nearly identical initial conditions diverge chaotically,
rendered as 3D parametric curves on rotating axes.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
from scipy.integrate import solve_ivp
import numpy as np

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/lorenz')
canvas.set_background()

# ── Lorenz system ───────────────────────────────────────────────────
def lorenz(_t, state, sigma=10, rho=28, beta=8/3):
    x, y, z = state
    return [sigma * (y - x), x * (rho - z) - y, x * y - beta * z]

# ── Solve for multiple nearby initial conditions ────────────────────
n_curves = 8
eps = 1e-5
T = 25
colors = color_gradient(['#2244FF', '#58C4DD', '#83C167', '#FFFF00'], n_curves)

solutions = []
for i in range(n_curves):
    sol = solve_ivp(lorenz, (0, T), [10, 10, 10 + i * eps],
                    t_eval=np.arange(0, T, 0.005), max_step=0.005)
    solutions.append(sol.y.T)

# ── 3D axes ─────────────────────────────────────────────────────────
axes = ThreeDAxes(
    x_range=(-25, 25, 10), y_range=(-25, 25, 10), z_range=(0, 50, 10),
    scale=9, cx=960, cy=580,
    show_ticks=False, show_labels=False,
    axis_color='#555', creation=0,
)
axes.set_camera_orientation(0, 8, phi=70, theta=30)
axes.begin_ambient_camera_rotation(0, 8, rate=12)

# ── Add curves as ParametricCurve3D objects ─────────────────────────
for sol, col in zip(solutions, colors):
    def make_func(s=sol):
        def f(t):
            idx = int(t * (len(s) - 1))
            idx = max(0, min(idx, len(s) - 1))
            return tuple(s[idx])
        return f
    curve = ParametricCurve3D(
        make_func(), t_range=(0, 1), num_points=500,
        stroke=col, stroke_width=2, creation=0,
    )
    axes.add_3d(curve)

# ── Title ───────────────────────────────────────────────────────────
title = Text(
    text='Lorenz Attractor', x=960, y=60, font_size=42,
    fill='#fff', stroke_width=0, text_anchor='middle', creation=0,
)
title.fadein(0, 1)

# ── Equations ───────────────────────────────────────────────────────
eq1 = Text(text='dx/dt = \u03c3(y - x)', x=160, y=140, font_size=22,
           fill='#aaa', stroke_width=0, text_anchor='start', creation=0)
eq2 = Text(text='dy/dt = x(\u03c1 - z) - y', x=160, y=170, font_size=22,
           fill='#aaa', stroke_width=0, text_anchor='start', creation=0)
eq3 = Text(text='dz/dt = xy - \u03b2z', x=160, y=200, font_size=22,
           fill='#aaa', stroke_width=0, text_anchor='start', creation=0)
for eq in (eq1, eq2, eq3):
    eq.fadein(0.5, 1.5)

params = Text(text='\u03c3=10  \u03c1=28  \u03b2=8/3', x=160, y=240,
              font_size=18, fill='#666', stroke_width=0, text_anchor='start', creation=0)
params.fadein(1, 2)

canvas.add(axes, title, eq1, eq2, eq3, params)
if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or 8,
                           fps=args.fps, port=args.port)
