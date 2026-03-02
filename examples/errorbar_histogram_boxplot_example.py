import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/errorbar_histogram_boxplot')
canvas.set_background()

title = Text(text='Error Bars, Histogram, Color Bar & Box Plot', x=960, y=40,
             font_size=28, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# --- Error bar plot ---
ax1 = Axes(x_range=(0, 6), y_range=(0, 12),
           plot_width=350, plot_height=220, x=50, y=100)
ax1.add_coordinates()
ax1.fadein(0.5, 1.5)

eb = ax1.plot_error_bar([1, 2, 3, 4, 5], [3, 7, 5, 9, 6],
                        [(0.8, 1.2), (1.0, 0.5), (0.6, 0.9), (1.5, 1.0), (0.7, 1.3)],
                        r=5, fill='#83C167')
eb.fadein(1.5, 2.5)

eb_label = Text(text='Error Bars', x=225, y=90,
                font_size=18, fill='#aaa', stroke_width=0, text_anchor='middle')
eb_label.fadein(1, 1.5)

# --- Histogram ---
import random
random.seed(42)
ax2 = Axes(x_range=(-4, 4), y_range=(0, 25),
           plot_width=350, plot_height=220, x=500, y=100)
ax2.add_coordinates()
ax2.fadein(0.5, 1.5)

data = [random.gauss(0, 1) for _ in range(100)]
hist = ax2.plot_histogram(data, bins=12, fill='#FF79C6', fill_opacity=0.6)
hist.fadein(1.5, 2.5)

h_label = Text(text='Histogram', x=675, y=90,
               font_size=18, fill='#aaa', stroke_width=0, text_anchor='middle')
h_label.fadein(1, 1.5)

# --- Color bar ---
ax3 = Axes(x_range=(0, 5), y_range=(0, 5),
           plot_width=250, plot_height=200, x=1000, y=120)
ax3.add_coordinates()
ax3.fadein(0.5, 1.5)

cb = ax3.add_color_bar(vmin=0, vmax=50, n_segments=30)
cb.fadein(1.5, 2)

cb_label = Text(text='Color Bar', x=1150, y=100,
                font_size=18, fill='#aaa', stroke_width=0, text_anchor='middle')
cb_label.fadein(1, 1.5)

# --- Box Plot ---
random.seed(123)
groups = [[random.gauss(5, 1.5) for _ in range(20)],
          [random.gauss(7, 2) for _ in range(25)],
          [random.gauss(4, 1) for _ in range(18)],
          [random.gauss(8, 2.5) for _ in range(22)]]
bp = BoxPlot(groups, x=200, y=480, plot_width=500, plot_height=250,
             box_width=40, box_color='#58C4DD')
bp.fadein(2, 3)

bp_label = Text(text='Box Plot', x=450, y=460,
                font_size=18, fill='#aaa', stroke_width=0, text_anchor='middle')
bp_label.fadein(1, 1.5)

canvas.add_objects(title, ax1, eb, eb_label,
                   ax2, hist, h_label,
                   ax3, cb, cb_label,
                   bp, bp_label)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/errorbar_histogram_boxplot_example.mp4', fps=30, end=3)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
