"""Spring-Mass System — simple harmonic motion with damping.

Inspired by 3b1b's Laplace transform series. Shows a mass on a spring
oscillating with damping, alongside a phase-space diagram and the
governing equation.
"""
from vectormation.objects import *
import math

canvas = VectorMathAnim()
canvas.set_background()

# ── Parameters ────────────────────────────────────────────────────────
k = 3.0       # spring constant
mu = 0.15     # damping coefficient
x0 = 150      # initial displacement (pixels)
v0 = 0        # initial velocity
dt = 1 / 240
T = 10.0
n_steps = int(T / dt)

# ── Simulate ──────────────────────────────────────────────────────────
# x'' + mu*x' + k*x = 0  (mass = 1)
trajectory = []  # (x_displacement, velocity) pairs
x, v = float(x0), float(v0)
for _ in range(n_steps + 1):
    trajectory.append((x, v))
    a = -k * x - mu * v
    v += a * dt
    x += v * dt

# ── Spring visualization ─────────────────────────────────────────────
anchor_x, anchor_y = 810, 220
eq_length = 300  # equilibrium spring length

def _make_interp(idx):
    def _at(t, _tr=trajectory, _i=idx):
        step = t / dt
        i = int(step)
        if i >= len(_tr) - 1:
            return _tr[-1][_i]
        frac = step - i
        return _tr[i][_i] + (_tr[i + 1][_i] - _tr[i][_i]) * frac
    return _at

x_fn = _make_interp(0)
v_fn = _make_interp(1)

# Spring as a zigzag path
n_coils = 12
def _spring_path(t):
    disp = x_fn(t)
    mass_x = anchor_x + eq_length + disp
    coil_w = (mass_x - anchor_x - 30) / n_coils  # leave room for end segments
    d = f'M{anchor_x},{anchor_y} L{anchor_x + 15},{anchor_y}'
    for i in range(n_coils):
        cx = anchor_x + 15 + (i + 0.5) * coil_w
        sign = 1 if i % 2 == 0 else -1
        d += f' L{cx},{anchor_y + sign * 20}'
    d += f' L{mass_x},{anchor_y}'
    return d

spring = Path('', stroke='#888', stroke_width=2.5, fill_opacity=0, creation=0)
spring.d.set_onward(0, _spring_path)

# Mass
mass = Rectangle(x=anchor_x + eq_length + x0 - 25, y=anchor_y - 25,
                 width=50, height=50, fill='#58C4DD', stroke='#fff',
                 stroke_width=2, rx=5, creation=0)
mass.x.set_onward(0, lambda t: anchor_x + eq_length + x_fn(t) - 25)

# Anchor wall
wall = Line(x1=anchor_x, y1=anchor_y - 60, x2=anchor_x, y2=anchor_y + 60,
            stroke='#888', stroke_width=4, creation=0)
# Hash marks on wall
hashes = []
for i in range(5):
    hy = anchor_y - 40 + i * 20
    h = Line(x1=anchor_x - 12, y1=hy + 12, x2=anchor_x, y2=hy,
             stroke='#666', stroke_width=2, creation=0)
    hashes.append(h)

# Equilibrium dashed line
eq_line = Line(x1=anchor_x + eq_length, y1=anchor_y - 80,
               x2=anchor_x + eq_length, y2=anchor_y + 80,
               stroke='#444', stroke_width=1, stroke_dasharray='6 4', creation=0)

# ── Phase space diagram ──────────────────────────────────────────────
phase_axes = Axes(x_range=(-200, 200), y_range=(-600, 600),
                  x=1000, y=400, plot_width=820, plot_height=380,
                  show_grid=True, x_label='x', y_label='v', creation=0)

# Plot phase trajectory as a growing path
def _phase_path(t):
    n = min(int(t / dt), len(trajectory) - 1)
    if n < 1:
        return ''
    step = max(1, n // 500)
    pts = [trajectory[i] for i in range(0, n + 1, step)]
    sx, sy = phase_axes.coords_to_point(pts[0][0], pts[0][1])
    d = f'M{sx:.1f},{sy:.1f}'
    for px, pv in pts[1:]:
        sx, sy = phase_axes.coords_to_point(px, pv)
        d += f'L{sx:.1f},{sy:.1f}'
    return d

phase_path = Path('', stroke='#FC6255', stroke_width=2, fill_opacity=0, creation=0)
phase_path.d.set_onward(0, _phase_path)

# Current point on phase space
phase_dot = Dot(r=6, fill='#FFFF00', stroke_width=0, creation=0)
phase_dot.c.set_onward(0, lambda t: phase_axes.coords_to_point(x_fn(t), v_fn(t)))

# ── Time-displacement graph ──────────────────────────────────────────
time_axes = Axes(x_range=(0, T), y_range=(-200, 200),
                 x=80, y=400, plot_width=820, plot_height=380,
                 show_grid=True, x_label='t', y_label='x', creation=0)

# Displacement curve (grows over time)
def _disp_path(t):
    n = min(int(t / dt), len(trajectory) - 1)
    if n < 1:
        return ''
    step = max(1, n // 300)
    pts_t = [(i * dt, trajectory[i][0]) for i in range(0, n + 1, step)]
    sx, sy = time_axes.coords_to_point(pts_t[0][0], pts_t[0][1])
    d = f'M{sx:.1f},{sy:.1f}'
    for pt, px in pts_t[1:]:
        sx, sy = time_axes.coords_to_point(pt, px)
        d += f'L{sx:.1f},{sy:.1f}'
    return d

disp_path = Path('', stroke='#58C4DD', stroke_width=2, fill_opacity=0, creation=0)
disp_path.d.set_onward(0, _disp_path)

# Envelope curves (exponential decay)
omega_d = math.sqrt(k - (mu / 2) ** 2) if k > (mu / 2) ** 2 else 0
env_upper = time_axes.plot(lambda t: x0 * math.exp(-mu * t / 2),
                            stroke='#555', stroke_width=1,
                            stroke_dasharray='4 4', num_points=100)
env_lower = time_axes.plot(lambda t: -x0 * math.exp(-mu * t / 2),
                            stroke='#555', stroke_width=1,
                            stroke_dasharray='4 4', num_points=100)

# ── Title & equation ─────────────────────────────────────────────────
title = TexObject(r'\text{Damped Spring-Mass System}', x=960, y=860,
                  font_size=36, fill='#fff', stroke_width=0, anchor='center',
                  creation=0)
title.fadein(0, 0.5)

eq_text = TexObject(r"$\ddot{x} + \mu \dot{x} + kx = 0$", x=960, y=930,
                    font_size=32, fill='#fff', stroke_width=0, anchor='center',
                    creation=0)
eq_text.fadein(0.3, 0.8)

# ── Assemble ──────────────────────────────────────────────────────────
canvas.add(wall, *hashes, eq_line, spring, mass)
canvas.add(time_axes, disp_path, env_upper, env_lower)
canvas.add(phase_axes, phase_path, phase_dot)
canvas.add(title, eq_text)

canvas.show(end=T)
