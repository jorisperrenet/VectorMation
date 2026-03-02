import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/candlestick_gantt')
canvas.set_background()

title = Text(text='Candlestick, Dumbbell, Parametric Area & Gantt', x=960, y=50,
             font_size=36, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# --- Candlestick chart ---
ax = Axes(x_range=(0, 8), y_range=(0, 25),
          plot_width=350, plot_height=250,
          x=50, y=120)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

data = [(1, 10, 15, 8, 14), (2, 14, 18, 12, 11),
        (3, 11, 16, 9, 15), (4, 15, 20, 13, 12),
        (5, 12, 17, 10, 16), (6, 16, 22, 14, 19)]
candles = ax.plot_candlestick(data, creation=1.5)
candles.fadein(1.5, 2.5)

candle_label = Text(text='Candlestick (OHLC)', x=225, y=110,
                    font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
candle_label.fadein(1, 1.5)

# --- Dumbbell chart ---
ax2 = Axes(x_range=(0, 100), y_range=(0, 5),
           plot_width=350, plot_height=200,
           x=500, y=120)
ax2.add_coordinates()
ax2.fadein(0.5, 1.5)

db = ax2.plot_dumbbell(
    [1, 2, 3, 4], [20, 35, 50, 15], [70, 80, 60, 45],
    start_color='#FF6B6B', end_color='#83C167', creation=1.5)
db.fadein(1.5, 2.5)

db_label = Text(text='Dumbbell Chart', x=675, y=110,
                font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
db_label.fadein(1, 1.5)

# --- Parametric area ---
ax3 = Axes(x_range=(-3, 3), y_range=(-3, 3),
           plot_width=300, plot_height=300,
           x=1000, y=120)
ax3.add_coordinates()
ax3.fadein(0.5, 1.5)

# Lissajous curve
fx = lambda t: 2 * math.sin(2 * t)
fy = lambda t: 2 * math.sin(3 * t)
area = ax3.add_parametric_area(fx, fy, t_range=(0, 2 * math.pi),
                                fill='#FF79C6', fill_opacity=0.3, creation=1.5)
area.fadein(1.5, 2.5)

# Draw the curve outline too
curve = ax3.plot_parametric(lambda t: (fx(t), fy(t)),
                             t_range=(0, 2 * math.pi),
                             stroke='#FF79C6', stroke_width=2)
curve.create(1.5, 2.5)

param_label = Text(text='Parametric Area', x=1150, y=110,
                   font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
param_label.fadein(1, 1.5)

# --- Gantt chart ---
tasks = [
    ('Research', 0, 3),
    ('Design', 2, 5),
    ('Frontend', 4, 9),
    ('Backend', 3, 8),
    ('Testing', 7, 11),
    ('Deploy', 10, 12),
]
gantt = GanttChart(tasks, x=200, y=550, width=1000, bar_height=35)
gantt.fadein(1, 2)

gantt_label = Text(text='Gantt Chart', x=700, y=530,
                   font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
gantt_label.fadein(1, 1.5)

canvas.add_objects(ax, ax2, ax3, title, candles, db, area, gantt,
                   candle_label, db_label, param_label, gantt_label)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/candlestick_gantt_example.mp4', fps=30, end=3)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
