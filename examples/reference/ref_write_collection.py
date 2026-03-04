"""VCollection.write: staggered write animation across children."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

shapes = VCollection(
    Circle(r=60, stroke='#E74C3C', fill='#E74C3C', fill_opacity=0.6),
    Rectangle(110, 110, stroke='#3498DB', fill='#3498DB', fill_opacity=0.6),
    RegularPolygon(6, radius=60, stroke='#2ECC71', fill='#2ECC71', fill_opacity=0.6),
)
shapes.arrange(direction='right', buff=60)
shapes.center_to_pos()
shapes.write(start=0.2, end=2.5)

v.add(shapes)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_write_collection.mp4', fps=30, end=3)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=3)
