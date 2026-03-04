"""Double Pendulum — chaotic motion from a simple system.

Two connected pendulums produce wildly different trajectories from
nearly identical initial conditions, illustrating sensitive dependence
(chaos). The simulation uses the exact Lagrangian equations of motion.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from vectormation.objects import *
import math

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/double_pendulum')
canvas.set_background()

# ── Parameters ────────────────────────────────────────────────────────
g = 9.81
L1, L2 = 1.0, 1.0        # arm lengths (meters)
m1, m2 = 1.0, 1.0         # masses
scale = 200                # pixels per meter

# Initial conditions: two pendulums with slightly different starting angles
configs = [
    {'theta1': 2.0,  'theta2': 2.0,  'color': '#58C4DD', 'label': 'A'},
    {'theta1': 2.01, 'theta2': 2.0,  'color': '#FF6B6B', 'label': 'B'},
]

dt = 1 / 240
T = 12.0
n_steps = int(T / dt)

# ── Simulate ──────────────────────────────────────────────────────────
def simulate_double_pendulum(th1, th2, w1=0, w2=0):
    """Runge-Kutta 4 integration of the double pendulum equations."""
    def derivs(state):
        t1, t2, o1, o2 = state
        delta = t1 - t2
        cos_d, sin_d = math.cos(delta), math.sin(delta)
        denom1 = (m1 + m2) * L1 - m2 * L1 * cos_d ** 2
        denom2 = (L2 / L1) * denom1
        a1 = (-m2 * L1 * o1 ** 2 * sin_d * cos_d +
              m2 * g * math.sin(t2) * cos_d -
              m2 * L2 * o2 ** 2 * sin_d -
              (m1 + m2) * g * math.sin(t1)) / denom1
        a2 = (m2 * L2 * o2 ** 2 * sin_d * cos_d +
              (m1 + m2) * g * math.sin(t1) * cos_d +
              (m1 + m2) * L1 * o1 ** 2 * sin_d -
              (m1 + m2) * g * math.sin(t2)) / denom2
        return [o1, o2, a1, a2]

    state = [th1, th2, w1, w2]
    trajectory = []  # list of (x1, y1, x2, y2) in SVG coords
    pivot_x, pivot_y = 960, 380

    for _ in range(n_steps + 1):
        t1, t2 = state[0], state[1]
        x1 = pivot_x + L1 * scale * math.sin(t1)
        y1 = pivot_y + L1 * scale * math.cos(t1)
        x2 = x1 + L2 * scale * math.sin(t2)
        y2 = y1 + L2 * scale * math.cos(t2)
        trajectory.append((x1, y1, x2, y2))

        # RK4 step
        k1 = derivs(state)
        s2 = [s + dt / 2 * k for s, k in zip(state, k1)]
        k2 = derivs(s2)
        s3 = [s + dt / 2 * k for s, k in zip(state, k2)]
        k3 = derivs(s3)
        s4 = [s + dt * k for s, k in zip(state, k3)]
        k4 = derivs(s4)
        state = [s + dt / 6 * (a + 2 * b + 2 * c + d)
                 for s, a, b, c, d in zip(state, k1, k2, k3, k4)]

    return trajectory

# ── Pivot & title ─────────────────────────────────────────────────────
pivot_x, pivot_y = 960, 380
pivot = Dot(r=6, cx=pivot_x, cy=pivot_y, fill='#fff')

title = TexObject(r'Double Pendulum: Chaos', x=960, y=60,
                  font_size=42, fill='#fff', stroke_width=0)
title.center_to_pos(960, 60)
title.fadein(0, 0.5)

subtitle = TexObject(r'Nearly identical initial conditions diverge rapidly',
                     x=960, y=110, font_size=22, fill='#888', stroke_width=0)
subtitle.center_to_pos(960, 110)
subtitle.fadein(0.2, 0.7)

# ── Create pendulum visuals ──────────────────────────────────────────
all_objects = [title, subtitle, pivot]

for cfg in configs:
    traj = simulate_double_pendulum(cfg['theta1'], cfg['theta2'])
    color = cfg['color']
    label = cfg['label']

    # Rod 1: pivot to mass 1
    rod1 = Line(x1=pivot_x, y1=pivot_y, x2=traj[0][0], y2=traj[0][1],
                stroke=color, stroke_width=3, stroke_opacity=0.8)

    # Rod 2: mass 1 to mass 2
    rod2 = Line(x1=traj[0][0], y1=traj[0][1], x2=traj[0][2], y2=traj[0][3],
                stroke=color, stroke_width=3, stroke_opacity=0.8)

    # Mass 1 (small)
    mass1 = Dot(r=8, cx=traj[0][0], cy=traj[0][1],
                fill=color, stroke_width=0)

    # Mass 2 (larger, with label)
    mass2 = Dot(r=12, cx=traj[0][2], cy=traj[0][3],
                fill=color, stroke_width=0)

    # Trace path for the tip
    trace = Path('', stroke=color, stroke_width=1.5, stroke_opacity=0.5,
                 fill_opacity=0)

    # Bake trajectories as time functions
    def _make_interp(traj_data, idx):
        def _at(t, _t=traj_data, _i=idx):
            step = t / dt
            i = int(step)
            if i >= len(_t) - 1:
                return _t[-1][_i]
            frac = step - i
            return _t[i][_i] + (_t[i + 1][_i] - _t[i][_i]) * frac
        return _at

    x1_fn = _make_interp(traj, 0)
    y1_fn = _make_interp(traj, 1)
    x2_fn = _make_interp(traj, 2)
    y2_fn = _make_interp(traj, 3)

    rod1.p1.set_onward(0, (pivot_x, pivot_y))
    rod1.p2.set_onward(0, lambda t, _fx=x1_fn, _fy=y1_fn: (_fx(t), _fy(t)))
    rod2.p1.set_onward(0, lambda t, _fx=x1_fn, _fy=y1_fn: (_fx(t), _fy(t)))
    rod2.p2.set_onward(0, lambda t, _fx=x2_fn, _fy=y2_fn: (_fx(t), _fy(t)))
    mass1.c.set_onward(0, lambda t, _fx=x1_fn, _fy=y1_fn: (_fx(t), _fy(t)))
    mass2.c.set_onward(0, lambda t, _fx=x2_fn, _fy=y2_fn: (_fx(t), _fy(t)))

    # Build trace path dynamically
    def _trace_d(t, _traj=traj, _dt=dt):
        n = min(int(t / _dt), len(_traj) - 1)
        if n < 1:
            return ''
        # Sample every 3rd point for performance
        step = max(1, n // 300)
        pts = [_traj[i] for i in range(0, n + 1, step)]
        d = f'M{pts[0][2]},{pts[0][3]}'
        for p in pts[1:]:
            d += f'L{p[2]},{p[3]}'
        return d
    trace.d.set_onward(0, _trace_d)

    all_objects.extend([trace, rod1, rod2, mass1, mass2])

# Legend
for i, cfg in enumerate(configs):
    lx = 100
    ly = 900 + i * 45
    all_objects.append(Circle(r=10, cx=lx, cy=ly, fill=cfg['color'], stroke_width=0))
    angle_str = f"{cfg['theta1']:.2f}"
    label_tex = TexObject(rf'Pendulum {cfg["label"]}: $\theta_1 = {angle_str}$ rad',
                          x=lx + 24, y=ly, font_size=28, fill=cfg['color'],
                          stroke_width=0)
    all_objects.append(label_tex)

canvas.add_objects(*all_objects)

if args.for_docs:
    canvas.export_video('docs/source/_static/videos/double_pendulum.mp4', fps=30, end=T)
if not args.for_docs:
    canvas.browser_display(start=0, end=T, fps=60, port=args.port)
