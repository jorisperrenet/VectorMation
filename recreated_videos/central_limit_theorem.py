"""Central Limit Theorem — demonstration of the CLT.

Rolls dice, computes sample means, and shows how the distribution
of sample means approaches a normal distribution.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math
import random

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/central_limit_theorem')
canvas.set_background()

random.seed(42)

# ── Parameters ─────────────────────────────────────────────────────────
n_samples = 200
sample_size = 10
n_bins = 20
x_range_vals = (1, 6)  # dice values
expected_mean = 3.5
expected_std = math.sqrt(35 / 12) / math.sqrt(sample_size)

# Generate sample means
sample_means = []
for _ in range(n_samples):
    rolls = [random.randint(1, 6) for _ in range(sample_size)]
    sample_means.append(sum(rolls) / len(rolls))

# ── Axes ───────────────────────────────────────────────────────────────
axes = Axes(x_range=(1, 6), y_range=(0, 50),
            x_label='Sample Mean', y_label='Frequency',
            plot_width=1200, plot_height=700,
            x=360, y=120, creation=0)
axes.add_coordinates()
axes.fadein(0, 0.5)
canvas.add(axes)

# ── Build histogram data ──────────────────────────────────────────────
bin_width = (x_range_vals[1] - x_range_vals[0]) / n_bins
bins = [0] * n_bins
for m in sample_means:
    idx = min(int((m - x_range_vals[0]) / bin_width), n_bins - 1)
    bins[idx] += 1

# ── Draw histogram bars progressively ─────────────────────────────────
bar_objects = []
t = 0.5
for i, count in enumerate(bins):
    if count == 0:
        continue
    bx = x_range_vals[0] + i * bin_width
    x1, y1 = axes.coords_to_point(bx, 0)
    x2, y2 = axes.coords_to_point(bx + bin_width, count)
    bar = Rectangle(abs(x2 - x1) - 1, abs(y2 - y1),
                    x=min(x1, x2), y=min(y1, y2),
                    fill='#58C4DD', fill_opacity=0.6,
                    stroke='#58C4DD', stroke_width=1, creation=t)
    bar.grow_from_edge(DOWN, start=t, end=t + 0.8)
    bar_objects.append(bar)
    canvas.add(bar)

# ── Normal curve overlay ──────────────────────────────────────────────
def normal_pdf(x):
    """Normal PDF scaled to match histogram."""
    z = (x - expected_mean) / expected_std
    pdf = math.exp(-0.5 * z * z) / (expected_std * math.sqrt(2 * math.pi))
    return pdf * n_samples * bin_width

curve = axes.plot(normal_pdf, stroke='#FF6B6B', stroke_width=3, creation=1.5)
curve.create(1.5, 2.5)

# ── Labels ────────────────────────────────────────────────────────────
title = Text(text='Central Limit Theorem', x=960, y=55,
             font_size=44, fill='#fff', stroke_width=0,
             text_anchor='middle', creation=0)
title.fadein(0, 0.5)
canvas.add(title)

subtitle = Text(text=f'{n_samples} samples of {sample_size} dice rolls each',
                x=960, y=1030,
                font_size=24, fill='#888', stroke_width=0,
                text_anchor='middle', creation=0.3)
subtitle.fadein(0.3, 0.8)
canvas.add(subtitle)

# Mean line
mx, my1 = axes.coords_to_point(expected_mean, 0)
_, my2 = axes.coords_to_point(expected_mean, 45)
mean_line = Line(x1=mx, y1=my1, x2=mx, y2=my2,
                 stroke='#FFFF00', stroke_width=2,
                 stroke_dasharray='8,4', creation=2.0)
mean_line.fadein(2.0, 2.5)
canvas.add(mean_line)

mean_label = Text(text=f'\u03bc = {expected_mean}', x=mx + 10, y=my2 - 10,
                  font_size=22, fill='#FFFF00', stroke_width=0,
                  creation=2.0)
mean_label.fadein(2.0, 2.5)
canvas.add(mean_label)

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or 5,
                           fps=args.fps, port=args.port)
