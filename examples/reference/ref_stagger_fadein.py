"""VCollection.stagger_fadein: staggered fade-in with directional shift."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

shapes = VCollection(
    Circle(r=50, fill='#E74C3C', fill_opacity=0.8),
    Rectangle(90, 90, fill='#3498DB', fill_opacity=0.8),
    RegularPolygon(3, radius=50, fill='#2ECC71', fill_opacity=0.8),
    RegularPolygon(5, radius=50, fill='#F39C12', fill_opacity=0.8),
    Circle(r=50, fill='#9B59B6', fill_opacity=0.8),
)
shapes.arrange(direction='right', buff=40)
shapes.center_to_pos()
shapes.stagger_fadein(start=0, end=2, shift_dir=UP, shift_amount=60, overlap=0.4)

v.add(shapes)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_stagger_fadein.mp4', fps=30, end=2.5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2.5)
