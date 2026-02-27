"""Pendulum Wave — recreation of the classic pendulum wave demonstration.

Multiple pendulums of slightly different lengths create mesmerizing
wave patterns as they go in and out of phase.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/pendulum_wave')
canvas.set_background()

# ── Parameters ────────────────────────────────────────────────────────
n_pendulums = 15
pivot_y = 150
base_length = 400  # longest pendulum (pixels)
base_period = 6.0  # period of longest pendulum (seconds)
T = 8.0

# Each pendulum completes a different number of oscillations in T seconds
# Pendulum i completes (n_pendulums + i) oscillations in T
colors = color_gradient(['#58C4DD', '#83C167', '#FFFF00', '#FC6255'], n=n_pendulums)

# ── Build pendulums ──────────────────────────────────────────────────
spacing = 1400 / (n_pendulums + 1)
x_start = 260

for i in range(n_pendulums):
    px = x_start + (i + 1) * spacing
    # frequency increases with index
    freq = (n_pendulums + i) / T
    omega = 2 * math.pi * freq
    amplitude = 30  # degrees
    length = base_length - i * 12

    # Pre-compute trajectory
    dt = 0.01
    n_steps = int(T / dt)

    # Create the rod (Line) and bob (Dot)
    rod = Line(x1=px, y1=pivot_y, x2=px, y2=pivot_y + length,
               stroke='#555', stroke_width=2, creation=0)
    bob = Dot(cx=px, cy=pivot_y + length, r=10,
              fill=colors[i], stroke_width=0, creation=0)

    # Animate using shift
    prev_bx, prev_by = px, pivot_y + length
    for step in range(1, n_steps):
        t = step * dt
        t_prev = (step - 1) * dt
        theta = math.radians(amplitude) * math.sin(omega * t)
        theta_prev = math.radians(amplitude) * math.sin(omega * t_prev)

        bx = px + length * math.sin(theta)
        by = pivot_y + length * math.cos(theta)
        bx_prev = px + length * math.sin(theta_prev)
        by_prev = pivot_y + length * math.cos(theta_prev)

        dx = bx - bx_prev
        dy = by - by_prev
        if abs(dx) > 0.05 or abs(dy) > 0.05:
            bob.shift(dx=dx, dy=dy, start=t_prev, end=t)
            rod.p2.set(t_prev, t,
                       lambda tt, _s=t_prev, _e=t, _sp=(bx_prev, by_prev), _ep=(bx, by):
                       (round(_sp[0] + (_ep[0] - _sp[0]) * min(1, (tt - _s) / max(_e - _s, 1e-9))),
                        round(_sp[1] + (_ep[1] - _sp[1]) * min(1, (tt - _s) / max(_e - _s, 1e-9)))))

    canvas.add(rod, bob)

# ── Pivot bar ─────────────────────────────────────────────────────────
bar = Line(x1=x_start, y1=pivot_y, x2=x_start + (n_pendulums + 1) * spacing,
           y2=pivot_y, stroke='#888', stroke_width=4, creation=0)
canvas.add(bar)

# ── Title ─────────────────────────────────────────────────────────────
title = Text(text='Pendulum Wave', x=960, y=60,
             font_size=42, fill='#fff', stroke_width=0, text_anchor='middle',
             creation=0)
title.fadein(0, 0.5)
canvas.add(title)

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or 8,
                           fps=args.fps, port=args.port)
