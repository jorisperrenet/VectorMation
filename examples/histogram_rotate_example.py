import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import random
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/histogram_rotate')
canvas.set_background()

title = Text(text='Histogram, Rotate Children & Labels', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Histogram on axes
ax = Axes(x_range=(0, 10), y_range=(0, 15),
          plot_width=600, plot_height=350,
          x=150, y=180)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

# Generate some data
random.seed(42)
data = [random.gauss(5, 1.5) for _ in range(100)]
hist = ax.plot_histogram(data, bins=12, fill='#83C167', fill_opacity=0.6, stroke='#83C167')
hist.fadein(1.5, 2.5)

# Add labels
lbl_mean = ax.add_vertical_label(5, 'mean', side='bottom', fill='#FF6B6B')
lbl_mean.fadein(2.5, 3)

lbl_hi = ax.add_horizontal_label(10, 'peak', side='right', fill='#FFFF00')
lbl_hi.fadein(2.5, 3)

# Rotate children demo
dots = VCollection(
    Dot(cx=1400, cy=500, r=18, fill='#FF6B6B'),
    Dot(cx=1500, cy=500, r=18, fill='#83C167'),
    Dot(cx=1400, cy=600, r=18, fill='#58C4DD'),
    Dot(cx=1500, cy=600, r=18, fill='#FFFF00'),
)
dots.fadein(3, 3.5)

label2 = Text(text='Rotate Children', x=1450, y=440,
              font_size=22, fill='#aaa', stroke_width=0, text_anchor='middle')
label2.fadein(3, 3.5)

# Rotate 90° around group center
dots.rotate_children(degrees=90, start=4, end=5)

canvas.add_objects(ax, title, dots, label2)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
