"""Advanced data visualization demo part 2: population pyramid, error bars,
stacked area, contour, quiver, and dot plot."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import math
from vectormation.objects import (
    VectorMathAnim, Axes, Text, parse_args,
)

args = parse_args()
v = VectorMathAnim(save_dir='out')

title = Text(text='More Advanced Visualizations', x=960, y=50,
             font_size=36, fill='#fff', stroke_width=0, text_anchor='middle')
title.fadein(0, 1)
v.add(title)

# ── 1. Population pyramid ─────────────────────────────────────────────
pp_label = Text(text='Population Pyramid', x=480, y=140,
                font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
pp_label.fadein(0.5, 1.5)
v.add(pp_label)

ax1 = Axes(x_range=(-50, 50), y_range=(0, 8),
           plot_width=700, plot_height=280, x=130, y=160, creation=0.5)
categories = [1, 2, 3, 4, 5, 6, 7]
left_vals = [35, 42, 38, 30, 22, 15, 8]
right_vals = [32, 40, 36, 28, 20, 12, 6]
ax1.plot_population_pyramid(categories, left_vals, right_vals,
                            bar_height=0.7, creation=1)
v.add(ax1)

# ── 2. Error bars ──────────────────────────────────────────────────────
eb_label = Text(text='Error Bars', x=1440, y=140,
                font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
eb_label.fadein(1.5, 2.5)
v.add(eb_label)

ax2 = Axes(x_range=(0, 7), y_range=(0, 12),
           plot_width=700, plot_height=280, x=1090, y=160, creation=1.5)
x_vals = [1, 2, 3, 4, 5, 6]
y_vals = [3, 5, 4, 8, 6, 10]
y_errs = [0.8, 1.2, 0.6, 1.5, 1.0, 0.9]
ax2.plot_error_bar(x_vals, y_vals, y_errs, r=5, creation=2,
                   fill='#50FA7B', stroke='#50FA7B')
v.add(ax2)

# ── 3. Stacked area ───────────────────────────────────────────────────
sa_label = Text(text='Stacked Area', x=480, y=560,
                font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
sa_label.fadein(2.5, 3.5)
v.add(sa_label)

ax3 = Axes(x_range=(0, 7), y_range=(0, 25),
           plot_width=700, plot_height=280, x=130, y=580, creation=2.5)
series1 = [2, 3, 5, 4, 3, 6, 4]
series2 = [4, 5, 3, 6, 5, 4, 7]
series3 = [3, 2, 4, 3, 5, 3, 2]
ax3.plot_stacked_area([series1, series2, series3],
                      colors=['#FF6B6B', '#58C4DD', '#50FA7B'],
                      creation=3)
v.add(ax3)

# ── 4. Contour plot ────────────────────────────────────────────────────
ct_label = Text(text='Contour Plot', x=1440, y=560,
                font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
ct_label.fadein(3.5, 4.5)
v.add(ct_label)

ax4 = Axes(x_range=(-3, 3), y_range=(-3, 3),
           plot_width=700, plot_height=280, x=1090, y=580, creation=3.5)
ax4.plot_contour(lambda x, y: math.sin(x) * math.cos(y),
                 levels=6, x_samples=30, y_samples=30, creation=4)
v.add(ax4)

v.browser_display(start=args.start or 0, end=args.end or 6,
                      fps=args.fps, port=args.port)
