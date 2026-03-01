import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from vectormation.objects import *
import math
import random

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/axes_extensions')
canvas.set_background()
T = 20.0

# ─── Phase 1 (0–5s): Scatter & Regression ───────────────────────────

ax1 = Axes(x_range=(0, 10), y_range=(0, 25),
           plot_width=1200, plot_height=700,
           x=360, y=160)
ax1.add_coordinates()
ax1.fadein(0, 0.8)

title1 = ax1.add_title('Scatter & Regression', font_size=36, fill='#58C4DD')
title1.fadein(0, 0.8)

# Generate scatter data: y = 0.3x^2 + noise
random.seed(42)
xs = [i * 0.5 for i in range(1, 19)]
ys = [0.3 * x ** 2 + random.uniform(-2, 3) for x in xs]

scatter = ax1.plot_scatter(xs, ys, r=6, fill='#FF6B6B')
scatter.fadein(0.8, 2.0)

# Regression line on top
reg_line = ax1.add_regression_line(xs, ys, stroke='#FFFF00', stroke_width=3)
reg_line.fadein(2.0, 3.0)

# Fade out phase 1 before phase 2
ax1.fadeout(4.0, 5.0)

canvas.add_objects(ax1)

# ─── Phase 2 (5–10s): Step Plot & Error Bars ─────────────────────────

ax2 = Axes(x_range=(0, 8), y_range=(0, 12),
           plot_width=1200, plot_height=700,
           x=360, y=160, creation=5.0)
ax2.add_coordinates()
ax2.fadein(5.0, 5.8)

title2 = ax2.add_title('Step Plot & Error Bars', font_size=36, fill='#58C4DD',
                        creation=5.0)
title2.fadein(5.0, 5.8)

# Step function data
step_x = [0, 1, 2, 3, 4, 5, 6, 7]
step_y = [2, 4, 3, 7, 5, 9, 6, 8]

step = ax2.plot_step(step_x, step_y, creation=5.0,
                     stroke='#83C167', stroke_width=3)
step.fadein(5.8, 7.0)

# Error bars at the data points
err_x = [1, 2, 3, 4, 5, 6, 7]
err_y = [4, 3, 7, 5, 9, 6, 8]
err_vals = [0.8, 1.2, 1.0, 0.6, 1.5, 0.9, 1.1]

error_bars = ax2.add_error_bars(err_x, err_y, err_vals, creation=5.0,
                                stroke='#aaa', stroke_width=1.5)
error_bars.fadein(7.0, 8.0)

# Fade out phase 2
ax2.fadeout(9.0, 10.0)

canvas.add_objects(ax2)

# ─── Phase 3 (10–15s): Histogram & Highlighting ──────────────────────

ax3 = Axes(x_range=(-4, 4), y_range=(0, 30),
           plot_width=1200, plot_height=700,
           x=360, y=160, creation=10.0)
ax3.add_coordinates()
ax3.fadein(10.0, 10.8)

title3 = ax3.add_title('Histogram & Highlighting', font_size=36, fill='#58C4DD',
                        creation=10.0)
title3.fadein(10.0, 10.8)

# Gaussian data
random.seed(123)
data = [random.gauss(0, 1) for _ in range(150)]

hist = ax3.plot_histogram(data, bins=16, creation=10.0,
                          fill='#FF79C6', fill_opacity=0.6,
                          stroke='#FF79C6', stroke_width=1)
hist.fadein(10.8, 12.0)

# Highlight the +/- 1 std dev range
highlight = ax3.highlight_x_range(-1, 1, creation=10.0,
                                  fill='#FFFF00', fill_opacity=0.15)
highlight.fadein(12.0, 13.0)

# Add a zero line for reference
zero = ax3.add_zero_line(axis='y', creation=10.0,
                         stroke='#888', stroke_width=2)
zero.fadein(12.0, 13.0)

# Fade out phase 3
ax3.fadeout(14.0, 15.0)

canvas.add_objects(ax3)

# ─── Phase 4 (15–20s): Slope Field ───────────────────────────────────

ax4 = Axes(x_range=(-3, 3), y_range=(-3, 3),
           plot_width=900, plot_height=700,
           x=510, y=160, creation=15.0)
ax4.add_coordinates()
ax4.fadein(15.0, 15.8)

title4 = ax4.add_title('Slope Field', font_size=36, fill='#58C4DD',
                        creation=15.0)
title4.fadein(15.0, 15.8)

# Slope field for dy/dx = -x/y  (circles as solution curves)
field = ax4.add_slope_field(
    lambda x, y: -x / y if abs(y) > 0.05 else 0,
    x_step=0.5, y_step=0.5, seg_length=0.2,
    creation=15.0, stroke='#58C4DD', stroke_width=1)
field.fadein(15.8, 17.0)

# Solution curve: circle of radius 2 -> y = sqrt(4 - x^2) (upper half)
solution = ax4.add_function(
    lambda x: math.sqrt(max(4 - x ** 2, 0)),
    x_range=(-1.95, 1.95), num_points=100,
    creation=15.0, stroke='#FFFF00', stroke_width=3)
solution.create(start=17.0, end=18.5)

canvas.add_objects(ax4)


if not args.no_display:
    canvas.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
        hot_reload=args.hot_reload,
    )
