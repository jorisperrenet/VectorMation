import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/pop_and_float')
canvas.set_background()

title = Text(text='Pop In/Out & Float Animations', x=960, y=80,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Pop in effect
circles = [
    Circle(r=40, cx=200 + i * 150, cy=300, fill=c, fill_opacity=0.9, stroke_width=0)
    for i, c in enumerate(['#FF6B6B', '#FFFF00', '#83C167', '#58C4DD', '#9B59B6'])
]
for i, c in enumerate(circles):
    c.pop_in(start=0.5 + i * 0.2, end=0.9 + i * 0.2, overshoot=1.3)
    canvas.add_objects(c)

# Floating objects
for c in circles:
    c.float_anim(start=2, end=8, amplitude=15, speed=0.5)

# Pop out at the end
for i, c in enumerate(circles):
    c.pop_out(start=6 + i * 0.15, end=6.3 + i * 0.15)

# Legend demo
legend = Legend([
    ('#FF6B6B', 'Error'),
    ('#FFFF00', 'Warning'),
    ('#83C167', 'Success'),
    ('#58C4DD', 'Info'),
], x=100, y=500, direction='down', font_size=20)
legend.fadein(1, 1.5)

canvas.add_objects(legend, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
