import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import math
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/spiral_secant')
canvas.set_background()

title = Text(text='Spiral Out & Secant Line', x=960, y=60,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Spiral in and out
star = Star(n=5, outer_radius=60, inner_radius=30, cx=300, cy=350,
            fill='#FFFF00', fill_opacity=0.9, stroke_width=0)
star.spiral_in(start=0.5, end=1.5, n_turns=2)
star.spiral_out(start=4, end=5.5, n_turns=2)

# Emphasize effect
circle = Circle(r=50, cx=600, cy=350, fill='#FF6B6B', stroke_width=0)
circle.fadein(0.5, 1)
circle.emphasize(start=2, end=3)
circle.emphasize(start=3.5, end=4.1, color='#83C167')

# Secant line on Axes
ax = Axes(x_range=(-2, 4), y_range=(-1, 10),
          plot_width=800, plot_height=500,
          x=900, y=200)
ax.fadein(0.5, 1)

func = lambda x: 0.5 * x ** 2
curve = ax.plot(func, stroke='#58C4DD', stroke_width=3)

# Secant line between x=0 and x=3
sec = ax.get_secant_line(func, x1=0, x2=3, length=400, stroke='#FF6B6B')
sec.fadein(2, 2.5)

# Tangent line at x=1.5 for comparison
tan = ax.get_tangent_line(func, x_val=1.5, length=300, stroke='#83C167')
tan.fadein(3, 3.5)

# Labeled dots
d1, l1 = ax.add_dot_label(0, func(0), label='(0, 0)', dot_color='#FF6B6B')
d2, l2 = ax.add_dot_label(3, func(3), label='(3, 4.5)', dot_color='#FF6B6B')
d1.fadein(2, 2.5)
l1.fadein(2, 2.5)
d2.fadein(2, 2.5)
l2.fadein(2, 2.5)

canvas.add_objects(ax, star, circle, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
