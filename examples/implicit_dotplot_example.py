import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/implicit_dotplot')
canvas.set_background()

title = Text(text='Implicit Curve & Dot Plot', x=960, y=40,
             font_size=28, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# --- Implicit curve: x^2 + y^2 = 4 (circle) ---
ax1 = Axes(x_range=(-3, 3), y_range=(-3, 3),
           plot_width=350, plot_height=350, x=50, y=120)
ax1.add_coordinates()
ax1.fadein(0.5, 1.5)

circle_curve = ax1.plot_implicit(
    lambda x, y: x**2 + y**2 - 4,
    num_points=40, stroke='#FF79C6', stroke_width=2.5)
circle_curve.fadein(1.5, 2.5)

# Also plot an implicit ellipse
ellipse_curve = ax1.plot_implicit(
    lambda x, y: (x / 2.5)**2 + (y / 1.5)**2 - 1,
    num_points=40, stroke='#83C167', stroke_width=2)
ellipse_curve.fadein(2, 3)

imp_label = Text(text='Implicit Curves', x=225, y=105,
                 font_size=18, fill='#aaa', stroke_width=0, text_anchor='middle')
imp_label.fadein(1, 1.5)

# --- Dot plot ---
ax2 = Axes(x_range=(0, 8), y_range=(0, 5),
           plot_width=400, plot_height=250, x=550, y=150)
ax2.add_coordinates()
ax2.fadein(0.5, 1.5)

import random
random.seed(42)
values = [random.choice([1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 6, 6, 7]) for _ in range(30)]
dp = ax2.plot_dot_plot(values, stack_spacing=0.35, r=6, fill='#58C4DD')
dp.fadein(1.5, 2.5)

dp_label = Text(text='Dot Plot', x=750, y=130,
                font_size=18, fill='#aaa', stroke_width=0, text_anchor='middle')
dp_label.fadein(1, 1.5)

canvas.add_objects(title, ax1, circle_curve, ellipse_curve, imp_label,
                   ax2, dp, dp_label)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
