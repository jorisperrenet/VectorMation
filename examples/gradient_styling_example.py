import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/gradient_styling')
canvas.set_background()

# Create a row of circles with gradient coloring
circles = VCollection(*[
    Circle(r=40, cx=300 + i * 130, cy=300, fill_opacity=0.9, stroke_width=0)
    for i in range(10)
])
circles.set_color_by_gradient('#FF0000', '#FFFF00', '#00FF00', attr='fill')
circles.stagger('fadein', delay=0.1, start=0, end=0.5)

# Add opacity gradient to another row of rectangles
rects = VCollection(*[
    Rectangle(100, 60, x=250 + i * 130, y=500, fill='#58C4DD', stroke_width=0)
    for i in range(10)
])
rects.set_opacity_by_gradient(0.1, 1.0, attr='fill')
rects.stagger('fadein', delay=0.1, start=1, end=1.5)

# SurroundingCircle demo
star = Star(n=5, outer_radius=60, inner_radius=30, cx=960, cy=750,
            fill='#FFFF00', fill_opacity=0.8)
star.fadein(2, 2.5)
surround = SurroundingCircle(star, buff=20, stroke='#83C167', stroke_width=3)
surround.fadein(2.5, 3)

title = Text(text='Gradient Styling & SurroundingCircle', x=960, y=100,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

canvas.add_objects(circles, rects, star, surround, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
