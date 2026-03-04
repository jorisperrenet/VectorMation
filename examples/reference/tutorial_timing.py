"""Timing model demo: sequential start/end animations."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

dot = Dot(cx=300, cy=540, r=20, fill='#58C4DD')
dot.fadein(start=0, end=0.5)

# Sequential animations using start= and end=
dot.shift(dx=300, start=0.5, end=1.5)   # move right
dot.shift(dy=-200, start=1.5, end=2.5)  # move up
dot.shift(dx=300, start=2.5, end=3.5)   # move right again
dot.shift(dy=200, start=3.5, end=4.5)   # move down

# Add time markers as text
for i, t in enumerate([0.5, 1.5, 2.5, 3.5, 4.5]):
    label = Text(f't={t}', x=300 + i * 150, y=900, font_size=24, fill='#666666')
    label.fadein(start=t - 0.2, end=t + 0.2)
    v.add(label)

v.add(dot)
if args.for_docs:
    v.export_video('docs/source/_static/videos/tutorial_timing.mp4', fps=30, end=5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=5)
