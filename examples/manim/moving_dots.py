"""Manim equivalent: MovingDots -- two dots linked by a line, each moving independently."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/manim/moving_dots')
canvas.set_background()
d1, d2 = Dot(r=12, fill='#58C4DD', fill_opacity=1), Dot(r=12, fill='#83C167', fill_opacity=1)
l = Line(x1=960, y1=540, x2=860, y2=540, stroke='#FC6255')
d1.c.set_to(l.p1)
d2.c.set_to(l.p2)
l.p1.move_to(1.5, 3, (960, 240))
l.p2.move_to(1, 2.5, (1260, 540))

canvas.add_objects(l, d1, d2)
if args.for_docs:
    canvas.export_video('docs/source/_static/videos/moving_dots.mp4', fps=30)
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
