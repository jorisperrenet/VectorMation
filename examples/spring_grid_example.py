import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/spring_grid')
canvas.set_background()

title = Text(text='Spring, Grid & For Each', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Axes with grid enabled
ax = Axes(x_range=(-3, 3), y_range=(-2, 2),
          plot_width=700, plot_height=350,
          x=200, y=200)
ax.add_grid()
ax.add_coordinates()
ax.fadein(0.5, 1.5)

# Plot a sine wave
import math
curve = ax.plot(math.sin, stroke='#58C4DD', stroke_width=3)
curve.create(1.5, 2.5)

# Spring animation demo - ball on a spring
ball = Circle(cx=1450, cy=400, r=25, fill='#FF6B6B', fill_opacity=0.7,
              stroke='#FF6B6B', stroke_width=2)
ball.fadein(2, 2.5)
ball.spring(start=2.5, end=5.5, amplitude=60, damping=3, frequency=5, axis='y')

spring_label = Text(text='Damped Spring', x=1450, y=300,
                    font_size=24, fill='#FF6B6B', stroke_width=0, text_anchor='middle')
spring_label.fadein(2, 2.5)

# Horizontal spring
ball2 = Circle(cx=1450, cy=600, r=25, fill='#83C167', fill_opacity=0.7,
               stroke='#83C167', stroke_width=2)
ball2.fadein(2, 2.5)
ball2.spring(start=3, end=6, amplitude=50, damping=4, frequency=3, axis='x')

# For each demo - color all dots at once
dots = VCollection(
    Dot(cx=1200, cy=800, r=15, fill='#aaa'),
    Dot(cx=1300, cy=800, r=15, fill='#aaa'),
    Dot(cx=1400, cy=800, r=15, fill='#aaa'),
    Dot(cx=1500, cy=800, r=15, fill='#aaa'),
    Dot(cx=1600, cy=800, r=15, fill='#aaa'),
)
dots.fadein(3.5, 4)
# Change all colors at once
dots.for_each('set_color', fill='#58C4DD', start=4.5, end=5)

canvas.add_objects(ax, title, ball, ball2, dots, spring_label)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
