import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/numberline_pointer')
canvas.set_background()

title = Text(text='NumberLine Pointer & Color Cycle', x=960, y=60,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Number line with pointer
nl = NumberLine(x_range=(-5, 5, 1), length=1200, x=360, y=400)
nl.fadein(0.5, 1)

ptr = nl.add_pointer(-3, label='x', color='#FF6B6B', creation=0.5)
nl.animate_pointer(ptr, 3, start=2, end=4)
nl.animate_pointer(ptr, 0, start=4.5, end=6)

# Color cycling circle
circle = Circle(r=60, cx=960, cy=700, fill='#FF6B6B', stroke_width=0)
circle.fadein(0.5, 1)
circle.color_cycle(['#FF6B6B', '#FFFF00', '#83C167', '#58C4DD', '#9B59B6', '#FF6B6B'],
                   start=1, end=6)

# Glitch effect demo
txt = Text(text='GLITCH', x=960, y=250, font_size=64,
           fill='#FF6B6B', stroke_width=0, text_anchor='middle')
txt.fadein(0.5, 1)
txt.glitch(start=2, end=5, intensity=15, n_flashes=8)

canvas.add_objects(nl, circle, txt, title)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/numberline_pointer_example.mp4', fps=30, end=6)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
