import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/zoom')
canvas.set_background()

title = Text(text='Zoom In / Out Effects', x=960, y=60,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Zoom in effects
r1 = Rectangle(width=200, height=120, x=200, y=250, fill='#FF6B6B', fill_opacity=0.8,
               stroke_width=0)
r1.zoom_in(start=0.5, end=1.5, start_scale=4)

circle = Circle(r=60, cx=600, cy=310, fill='#83C167', fill_opacity=0.8, stroke_width=0)
circle.zoom_in(start=1, end=2, start_scale=2.5)

star = Star(n=5, outer_radius=50, inner_radius=25, cx=960, cy=310,
            fill='#FFFF00', fill_opacity=0.9, stroke_width=0)
star.zoom_in(start=1.5, end=2.5)

# Zoom out effects
r1.zoom_out(start=5, end=6, end_scale=3)
circle.zoom_out(start=5.5, end=6.5, end_scale=4)
star.zoom_out(start=6, end=7, end_scale=2.5)

# Axes with coordinates
ax = Axes(x_range=(-3, 3), y_range=(-2, 8),
          plot_width=800, plot_height=400,
          x=560, y=450)
ax.add_coordinates()
ax.fadein(1, 2)

func = lambda x: x ** 2
curve = ax.plot(func, stroke='#58C4DD', stroke_width=3)

# Add a horizontal reference line
hline = ax.get_horizontal_line(2, 4, stroke='#FF6B6B', stroke_dasharray='5 5')
hline.fadein(2.5, 3)

canvas.add_objects(r1, circle, star, ax, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
