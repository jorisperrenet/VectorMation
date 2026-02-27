"""Fourier Series — recreation of 3b1b's Fourier series visualization.

Shows how adding sine waves of increasing frequency approximates a square wave.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/fourier')
canvas.set_background()

# ── Axes ──────────────────────────────────────────────────────────────
axes = Axes(x_range=(0, 2 * math.pi), y_range=(-1.5, 1.5),
            x=160, y=180, plot_width=1600, plot_height=600,
            show_grid=True, creation=0)
axes.fadein(0, 0.5)

# ── Square wave (target) ─────────────────────────────────────────────
def square_wave(x):
    return 1 if (x % (2 * math.pi)) < math.pi else -1

target = axes.plot(square_wave, stroke='#555', stroke_width=2,
                   stroke_dasharray='8 4', num_points=500)

# ── Fourier partial sums ─────────────────────────────────────────────
colors = color_gradient(['#58C4DD', '#83C167', '#FFFF00', '#FC6255', '#FF6B6B'], n=8)
n_terms_list = [1, 3, 5, 7, 9, 13, 21, 51]

curves = []
labels = []
for idx, n_terms in enumerate(n_terms_list):
    def make_fourier(n=n_terms):
        def f(x):
            s = 0
            for k in range(1, n + 1, 2):
                s += (4 / (math.pi * k)) * math.sin(k * x)
            return s
        return f

    color = colors[idx % len(colors)]
    t_start = 0.5 + idx * 0.8
    t_end = t_start + 0.6

    curve = axes.plot(make_fourier(), stroke=color, stroke_width=3,
                      num_points=300)
    curve.set_opacity(0, start=0)
    curve.set_opacity(1, start=t_start, end=t_end)

    # Fade out previous curve (except the last one)
    if idx > 0 and idx < len(n_terms_list) - 1:
        curve.set_opacity(0.15, start=t_end + 0.5, end=t_end + 0.8)

    lbl = Text(text=f'n={n_terms}', x=1700, y=140 + idx * 30,
               font_size=18, fill=color, stroke_width=0, creation=0)
    lbl.fadein(t_start, t_end)
    curves.append(curve)
    labels.append(lbl)

# ── Title ─────────────────────────────────────────────────────────────
title = Text(text='Fourier Series Approximation', x=960, y=50,
             font_size=42, fill='#fff', stroke_width=0, text_anchor='middle',
             creation=0)
title.fadein(0, 0.5)

subtitle = Text(text='f(x) = Σ (4/πk) sin(kx),  k = 1, 3, 5, ...',
                x=960, y=870, font_size=22, fill='#aaa', stroke_width=0,
                text_anchor='middle', creation=0)
subtitle.fadein(0.5, 1)

canvas.add(axes, target, *curves, *labels, title, subtitle)

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or 8,
                           fps=args.fps, port=args.port)
