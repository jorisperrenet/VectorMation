"""Basic shapes intro: circle, rectangle, text with animations."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

# Create three shapes
circle = Circle(r=80, cx=400, cy=540, fill='#58C4DD', fill_opacity=0.8)
rect = Rectangle(160, 160, x=880, y=460, fill='#E74C3C', fill_opacity=0.8)
text = Text('Hello!', x=1440, y=540, font_size=64, fill='WHITE')

# Fade them in one at a time
circle.fadein(start=0, end=1)
rect.fadein(start=0.5, end=1.5)
text.fadein(start=1, end=2)

# Move them together
circle.shift(dy=-150, start=2.5, end=3.5)
rect.shift(dy=-150, start=2.5, end=3.5)
text.shift(dy=-150, start=2.5, end=3.5)

v.add(circle, rect, text)
if args.for_docs:
    v.export_video('docs/source/_static/videos/tutorial_shapes.mp4', fps=30, end=4)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=4)
