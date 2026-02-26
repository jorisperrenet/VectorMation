import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/progress_bar')
canvas.set_background()

title = Text(text='Progress Bar & Marching Ants', x=960, y=100,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Progress bar animation
bar = ProgressBar(width=600, height=30, x=660, y=250, fill_color='#83C167')
bar.fadein(0, 0.5)
bar.animate_to(0.3, 0.5, 1.5)
bar.animate_to(0.7, 2, 3)
bar.animate_to(1.0, 3.5, 4.5)

label = Text(text='Loading...', x=960, y=320, font_size=24,
             fill='#fff', stroke_width=0, text_anchor='middle')
label.fadein(0, 0.5)

# Marching ants on a rectangle
rect = Rectangle(300, 200, x=350, y=450, fill_opacity=0, stroke='#FFFF00', stroke_width=2)
rect.fadein(1, 1.5)
rect.animate_dash(start=1.5, end=8, dash_length=15, gap=10)

# Marching ants on a circle
circ = Circle(r=100, cx=1300, cy=550, fill_opacity=0, stroke='#58C4DD', stroke_width=2)
circ.fadein(1, 1.5)
circ.animate_dash(start=1.5, end=8, dash_length=20, gap=15)

canvas.add_objects(title, bar, label, rect, circ)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
