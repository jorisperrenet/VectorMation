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
T = 8.0

# Each pendulum i completes (n_pendulums + i) oscillations in T seconds
colors = color_gradient(['#58C4DD', '#83C167', '#FFFF00', '#FC6255'], n=n_pendulums)

# ── Build pendulums ──────────────────────────────────────────────────
spacing = 1400 / (n_pendulums + 1)
x_start = 260
amplitude = math.radians(30)

for i in range(n_pendulums):
    px = x_start + (i + 1) * spacing
    freq = (n_pendulums + i) / T
    omega = 2 * math.pi * freq
    length = base_length - i * 12

    # Position functions using closures
    def _make_bob_fn(px=px, omega=omega, length=length, amp=amplitude, py=pivot_y):
        def _fn(t):
            theta = amp * math.sin(omega * t)
            return (px + length * math.sin(theta),
                    py + length * math.cos(theta))
        return _fn

    bob_fn = _make_bob_fn()

    rod = Line(x1=px, y1=pivot_y, x2=px, y2=pivot_y + length,
               stroke='#555', stroke_width=2, creation=0)
    bob = Dot(cx=px, cy=pivot_y + length, r=10,
              fill=colors[i], stroke_width=0, creation=0)

    # Animate using set_onward with time functions
    rod.p1.set_onward(0, (px, pivot_y))
    rod.p2.set_onward(0, bob_fn)
    bob.c.set_onward(0, bob_fn)

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
