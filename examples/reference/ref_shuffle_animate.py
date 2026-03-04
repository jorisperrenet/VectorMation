"""VCollection.shuffle_animate() randomly shuffling shape positions."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

colors = ['#58C4DD', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6']
group = VCollection(
    *[Circle(r=40, fill=c, fill_opacity=0.8) for c in colors]
)
group.arrange(direction='right', buff=40)
group.center_to_pos()

group.shuffle_animate(start=0.5, end=2)

v.add(group)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_shuffle_animate.mp4', fps=30, end=2.5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2.5)
