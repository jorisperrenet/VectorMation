"""Demonstrate transform_from_copy: morph a ghost copy while keeping the original."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim(verbose=args.verbose, save_dir='svgs/transform_from_copy')

# Source objects
circle = Circle(r=60, cx=400, cy=540, fill='#3498DB', fill_opacity=0.8, stroke_width=3)
circle.fadein(start=0, end=0.5)

square = Square(side=120, x=960, y=540, fill='#E74C3C', fill_opacity=0.8, stroke_width=3)
square.fadein(start=0, end=0.5)

star = Star(5, outer_radius=70, inner_radius=30, cx=1520, cy=540,
            fill='#F1C40F', fill_opacity=0.8, stroke_width=3)
star.fadein(start=0, end=0.5)

# Ghost copies morph between shapes (originals stay put)
ghost1 = circle.transform_from_copy(square, start=1, end=3)
ghost2 = square.transform_from_copy(star, start=2, end=4)
ghost3 = star.transform_from_copy(circle, start=3, end=5)

v.add(circle, square, star, ghost1, ghost2, ghost3)
if args.verbose:
    v.export_video('docs/source/_static/videos/transform_from_copy_example.mp4', fps=30, end=6)
if not args.no_display:
    v.browser_display(end=args.duration or 6, fps=args.fps, port=args.port, hot_reload=args.hot_reload)
