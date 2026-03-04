"""VCollection.swap_children() animating two shapes swapping positions."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

group = VCollection(
    Circle(r=50, fill='#58C4DD', fill_opacity=0.8),
    Rectangle(90, 90, fill='#E74C3C', fill_opacity=0.8),
    RegularPolygon(3, radius=50, fill='#2ECC71', fill_opacity=0.8),
)
group.arrange(direction='right', buff=80)
group.center_to_pos()

group.swap_children(0, 2, start=0.5, end=2)

v.add(group)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_swap_children.mp4', fps=30, end=2.5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2.5)
