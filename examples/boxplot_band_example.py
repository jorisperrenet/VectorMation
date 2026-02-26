import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math, random
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/boxplot_band')
canvas.set_background()

title = Text(text='Box Plots, Confidence Bands & Shuffle', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# --- Axes with confidence band ---
ax = Axes(x_range=(0, 7), y_range=(-2, 5),
          plot_width=500, plot_height=300,
          x=50, y=130)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

func = lambda x: math.sin(x) + 2
curve = ax.plot(func, stroke='#83C167', stroke_width=3)
curve.create(1.5, 2.5)

band = ax.add_confidence_band(
    lambda x: func(x) - 0.8,
    lambda x: func(x) + 0.8,
    creation=2, fill='#83C167', fill_opacity=0.15)
band.fadein(2, 2.5)

band_label = Text(text='±0.8 band', x=350, y=120,
                  font_size=18, fill='#aaa', stroke_width=0, text_anchor='middle')
band_label.fadein(2, 2.5)

# --- Axes with boxplot ---
ax2 = Axes(x_range=(0, 5), y_range=(0, 25),
           plot_width=450, plot_height=300,
           x=700, y=130)
ax2.add_coordinates()
ax2.fadein(0.5, 1.5)

random.seed(42)
data1 = [random.gauss(10, 3) for _ in range(30)]
data2 = [random.gauss(15, 2) for _ in range(30)]
data3 = [random.gauss(8, 4) for _ in range(30)]
data4 = [random.gauss(18, 2.5) for _ in range(30)]

boxes = ax2.plot_bar([1, 2, 3, 4], [0]*4, width=0)  # placeholder
boxes = ax2.add_boxplot([data1, data2, data3, data4],
                         x_positions=[1, 2, 3, 4], width=0.6,
                         creation=2, stroke='#FF6B6B')
boxes.fadein(2, 3)

# --- Shuffle demo ---
dots = VCollection(
    *[Dot(cx=300 + i * 80, cy=700, r=20,
          fill=['#FF6B6B', '#83C167', '#58C4DD', '#FFFF00', '#FF79C6'][i])
      for i in range(5)]
)
dots.fadein(1, 1.5)
shuffle_label = Text(text='Shuffle Positions', x=460, y=640,
                     font_size=24, fill='#aaa', stroke_width=0, text_anchor='middle')
shuffle_label.fadein(1, 1.5)

dots.shuffle_positions(start=3, end=4.5, seed=7)

canvas.add_objects(ax, ax2, title, band, band_label, boxes, dots, shuffle_label)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
