import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/ribbon_swarm_heatmap')
canvas.set_background()

title = Text(text='Ribbon, Swarm Plot, Axis Break & Matrix Heatmap', x=960, y=40,
             font_size=28, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# --- Ribbon plot ---
ax1 = Axes(x_range=(0, 6), y_range=(0, 10),
           plot_width=350, plot_height=220, x=50, y=100)
ax1.add_coordinates()
ax1.fadein(0.5, 1.5)

import math
xs = [i * 0.5 for i in range(13)]
y_mid = [3 + 2 * math.sin(x) for x in xs]
y_lo = [y - 1.2 for y in y_mid]
y_hi = [y + 1.2 for y in y_mid]
ribbon = ax1.plot_ribbon(xs, y_lo, y_hi, fill='#58C4DD', fill_opacity=0.3,
                         stroke='#58C4DD')
ribbon.fadein(1.5, 2.5)

line = ax1.plot(lambda x: 3 + 2 * math.sin(x), stroke='#58C4DD', stroke_width=2)
line.fadein(1.5, 2.5)

r_label = Text(text='Confidence Ribbon', x=225, y=90,
               font_size=18, fill='#aaa', stroke_width=0, text_anchor='middle')
r_label.fadein(1, 1.5)

# --- Swarm plot ---
ax2 = Axes(x_range=(0, 4), y_range=(0, 15),
           plot_width=250, plot_height=220, x=500, y=100)
ax2.add_coordinates()
ax2.fadein(0.5, 1.5)

import random
random.seed(7)
groups = [[random.gauss(7, 2) for _ in range(15)],
          [random.gauss(9, 1.5) for _ in range(12)],
          [random.gauss(5, 3) for _ in range(18)]]
swarm = ax2.plot_swarm([1, 2, 3], groups, r=5, jitter_width=0.25,
                       fill='#FF79C6')
swarm.fadein(2, 3)

s_label = Text(text='Swarm Plot', x=625, y=90,
               font_size=18, fill='#aaa', stroke_width=0, text_anchor='middle')
s_label.fadein(1, 1.5)

# --- Axis break ---
ax3 = Axes(x_range=(0, 5), y_range=(0, 100),
           plot_width=250, plot_height=220, x=850, y=100)
ax3.add_coordinates()
ax3.fadein(0.5, 1.5)

bars = ax3.plot_bar([1, 2, 3, 4], [15, 85, 12, 90], bar_width=0.6)
bars.fadein(1, 2)

brk = ax3.add_axis_break(20, axis='y')
brk.fadein(1.5, 2)

b_label = Text(text='Axis Break', x=975, y=90,
               font_size=18, fill='#aaa', stroke_width=0, text_anchor='middle')
b_label.fadein(1, 1.5)

# --- Matrix Heatmap ---
data = [[1.0, 2.3, 3.1, 4.5],
        [5.2, 6.0, 7.8, 2.1],
        [3.3, 8.9, 1.5, 6.7],
        [7.0, 4.2, 5.5, 9.1]]
mh = MatrixHeatmap(data, row_labels=['A', 'B', 'C', 'D'],
                   col_labels=['Q1', 'Q2', 'Q3', 'Q4'],
                   x=350, y=450, cell_size=55, font_size=14)
mh.fadein(2, 3)

mh_label = Text(text='Matrix Heatmap', x=550, y=430,
                font_size=18, fill='#aaa', stroke_width=0, text_anchor='middle')
mh_label.fadein(1, 1.5)

canvas.add_objects(title, ax1, ribbon, line, r_label,
                   ax2, swarm, s_label,
                   ax3, bars, brk, b_label,
                   mh, mh_label)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/ribbon_swarm_heatmap_example.mp4', fps=30, end=3)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
