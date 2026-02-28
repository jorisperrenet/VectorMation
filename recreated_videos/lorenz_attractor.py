"""Lorenz Attractor — chaotic system with butterfly effect.

Two trajectories with nearly identical initial conditions diverge
chaotically, illustrating sensitive dependence on initial conditions.
Uses RK4 integration and oblique 3D-to-2D projection.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/lorenz_attractor')
canvas.set_background()

# ── Lorenz parameters ────────────────────────────────────────────────
sigma = 10
rho = 28
beta = 8 / 3

def lorenz(state):
    x, y, z = state
    return [
        sigma * (y - x),
        x * (rho - z) - y,
        x * y - beta * z,
    ]

# ── RK4 integration ─────────────────────────────────────────────────
def rk4_integrate(state0, dt, n_steps):
    """Integrate the Lorenz system using 4th-order Runge-Kutta."""
    trajectory = [tuple(state0)]
    state = list(state0)
    for _ in range(n_steps):
        k1 = lorenz(state)
        s2 = [s + dt / 2 * k for s, k in zip(state, k1)]
        k2 = lorenz(s2)
        s3 = [s + dt / 2 * k for s, k in zip(state, k2)]
        k3 = lorenz(s3)
        s4 = [s + dt * k for s, k in zip(state, k3)]
        k4 = lorenz(s4)
        state = [s + dt / 6 * (a + 2 * b + 2 * c + d)
                 for s, a, b, c, d in zip(state, k1, k2, k3, k4)]
        trajectory.append(tuple(state))
    return trajectory

# ── Simulate two trajectories ────────────────────────────────────────
T = 12
sim_dt = 0.002
sim_time = 40.0  # simulate enough Lorenz time for a full attractor
n_steps = int(sim_time / sim_dt)

traj_a = rk4_integrate([1.0, 1.0, 1.0], sim_dt, n_steps)
traj_b = rk4_integrate([1.0, 1.0, 1.001], sim_dt, n_steps)  # tiny perturbation

# ── 3D to 2D projection ─────────────────────────────────────────────
center_x = 960
center_y = 520
scale = 10
z_offset = 25  # center the attractor vertically (z ranges ~5-45, mean ~25)

def project(x, y, z):
    """Oblique projection of Lorenz 3D coords to SVG 2D coords."""
    sx = center_x + scale * (x + z * 0.3)
    sy = center_y - scale * (z - z_offset + y * 0.2)
    return sx, sy

# ── Precompute projected points ──────────────────────────────────────
pts_a = [project(*p) for p in traj_a]
pts_b = [project(*p) for p in traj_b]

# ── Build path d-string from projected points up to a given fraction ──
def _make_trace_fn(pts):
    """Return a function t -> SVG path d-string that grows over [0, T]."""
    total = len(pts)
    def _trace_d(t):
        # Map video time [0, T] to trajectory index
        frac = min(t / T, 1.0)
        n = int(frac * (total - 1))
        if n < 1:
            return ''
        # Subsample for performance (max ~800 points in the path)
        step = max(1, n // 800)
        d = f'M{pts[0][0]:.1f},{pts[0][1]:.1f}'
        for i in range(step, n + 1, step):
            d += f'L{pts[i][0]:.1f},{pts[i][1]:.1f}'
        return d
    return _trace_d

# ── Trajectory paths ────────────────────────────────────────────────
color_a = '#58C4DD'  # cyan-blue
color_b = '#FC6255'  # red-orange

path_a = Path('', stroke=color_a, stroke_width=1.5, stroke_opacity=0.85,
              fill_opacity=0, creation=0)
path_a.d.set_onward(0, _make_trace_fn(pts_a))

path_b = Path('', stroke=color_b, stroke_width=1.5, stroke_opacity=0.85,
              fill_opacity=0, creation=0)
path_b.d.set_onward(0, _make_trace_fn(pts_b))

# ── Moving dots at the head of each trajectory ──────────────────────
def _make_head_fn(pts):
    total = len(pts)
    def _head(t):
        frac = min(t / T, 1.0)
        idx = min(int(frac * (total - 1)), total - 1)
        return pts[idx]
    return _head

dot_a = Dot(r=5, fill=color_a, stroke_width=0, creation=0)
dot_a.c.set_onward(0, _make_head_fn(pts_a))

dot_b = Dot(r=5, fill=color_b, stroke_width=0, creation=0)
dot_b.c.set_onward(0, _make_head_fn(pts_b))

# ── Title ────────────────────────────────────────────────────────────
title = Text(text='Lorenz Attractor', x=960, y=55,
             font_size=42, fill='#fff', stroke_width=0,
             text_anchor='middle', creation=0)
title.fadein(0, 1)

subtitle = Text(text='Sensitivity to Initial Conditions',
                x=960, y=95, font_size=22, fill='#888',
                stroke_width=0, text_anchor='middle', creation=0)
subtitle.fadein(0.3, 1.3)

# ── Equation labels ──────────────────────────────────────────────────
eq1 = Text(text='dx/dt = \u03c3(y \u2212 x)', x=130, y=180, font_size=22,
           fill='#aaa', stroke_width=0, text_anchor='start', creation=0)
eq2 = Text(text='dy/dt = x(\u03c1 \u2212 z) \u2212 y', x=130, y=212, font_size=22,
           fill='#aaa', stroke_width=0, text_anchor='start', creation=0)
eq3 = Text(text='dz/dt = xy \u2212 \u03b2z', x=130, y=244, font_size=22,
           fill='#aaa', stroke_width=0, text_anchor='start', creation=0)
for eq in (eq1, eq2, eq3):
    eq.fadein(0.5, 1.5)

# ── Parameter labels ────────────────────────────────────────────────
params = Text(text='\u03c3 = 10    \u03c1 = 28    \u03b2 = 8/3', x=130, y=284,
              font_size=18, fill='#666', stroke_width=0,
              text_anchor='start', creation=0)
params.fadein(1, 2)

# ── Legend ────────────────────────────────────────────────────────────
legend_a_dot = Circle(r=6, cx=1650, cy=180, fill=color_a, stroke_width=0, creation=0)
legend_a_txt = Text(text='z\u2080 = 1.000', x=1665, y=186, font_size=18,
                    fill=color_a, stroke_width=0, text_anchor='start', creation=0)
legend_b_dot = Circle(r=6, cx=1650, cy=210, fill=color_b, stroke_width=0, creation=0)
legend_b_txt = Text(text='z\u2080 = 1.001', x=1665, y=216, font_size=18,
                    fill=color_b, stroke_width=0, text_anchor='start', creation=0)
for obj in (legend_a_dot, legend_a_txt, legend_b_dot, legend_b_txt):
    obj.fadein(1.5, 2.5)

# ── Reference axes hint (faint lines showing projected x/y/z) ───────
origin = project(0, 0, 0)
tip_x = project(15, 0, 0)
tip_y = project(0, 15, 0)
tip_z = project(0, 0, 15)

axis_x = Line(x1=origin[0], y1=origin[1], x2=tip_x[0], y2=tip_x[1],
              stroke='#444', stroke_width=1, stroke_dasharray='4 4', creation=0)
axis_y = Line(x1=origin[0], y1=origin[1], x2=tip_y[0], y2=tip_y[1],
              stroke='#444', stroke_width=1, stroke_dasharray='4 4', creation=0)
axis_z = Line(x1=origin[0], y1=origin[1], x2=tip_z[0], y2=tip_z[1],
              stroke='#444', stroke_width=1, stroke_dasharray='4 4', creation=0)

lbl_x = Text(text='x', x=tip_x[0] + 10, y=tip_x[1] + 5, font_size=16,
             fill='#555', stroke_width=0, creation=0)
lbl_y = Text(text='y', x=tip_y[0] + 10, y=tip_y[1] + 5, font_size=16,
             fill='#555', stroke_width=0, creation=0)
lbl_z = Text(text='z', x=tip_z[0] + 10, y=tip_z[1] - 5, font_size=16,
             fill='#555', stroke_width=0, creation=0)

for obj in (axis_x, axis_y, axis_z, lbl_x, lbl_y, lbl_z):
    obj.fadein(0.5, 1.5)

# ── Assemble ─────────────────────────────────────────────────────────
canvas.add(axis_x, axis_y, axis_z, lbl_x, lbl_y, lbl_z)
canvas.add(path_a, path_b, dot_a, dot_b)
canvas.add(title, subtitle, eq1, eq2, eq3, params)
canvas.add(legend_a_dot, legend_a_txt, legend_b_dot, legend_b_txt)

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or T,
                           fps=args.fps, port=args.port)
