import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/trace_area')
canvas.set_background()

title = Text(text='Trace Path, Area Between & Flash Color', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# A moving circle that leaves a trace
dot = Circle(r=15, cx=200, cy=300, fill='#FF6B6B', stroke_width=0)
dot.fadein(0.5, 1)
dot.orbit(cx=400, cy=300, radius=120, start=1, end=5, degrees=720)
trace = dot.trace_path(start=1, end=5, stroke='#FF6B6B', stroke_width=2, stroke_opacity=0.5)

# Flash color on a rectangle
rect = Rectangle(width=150, height=100, x=700, y=250, fill='#83C167',
                 stroke_width=2, stroke='#fff')
rect.fadein(0.5, 1)
rect.flash_color('#FFFF00', start=2, duration=0.5)
rect.flash_color('#FF6B6B', start=3.5, duration=0.6)
rect.flash_color('#58C4DD', start=5, duration=0.8, attr='stroke')

# Area between two functions
ax = Axes(x_range=(-2, 4), y_range=(-1, 8),
          plot_width=700, plot_height=350,
          x=600, y=500)
ax.add_coordinates()
ax.fadein(1, 2)

f1 = lambda x: x ** 2
f2 = lambda x: 2 * x + 1
curve1 = ax.plot(f1, stroke='#58C4DD', stroke_width=3)
curve2 = ax.plot(f2, stroke='#FF6B6B', stroke_width=3)
curve1.create(2, 3)
curve2.create(2, 3)

area = ax.get_area_between(f1, f2, x_range=(-0.41, 2.41),
                            fill='#83C167', fill_opacity=0.4)
area.fadein(3, 4)

# Spread: distribute dots along a diagonal
dots = VGroup(
    *[Dot(cx=0, cy=0, r=8, fill='#FFFF00', stroke_width=0) for _ in range(6)]
)
dots.spread(1100, 200, 1700, 400)
dots.cascade('fadein', start=1.5, end=3, overlap=0.4)

canvas.add_objects(dot, trace, rect, ax, dots, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
