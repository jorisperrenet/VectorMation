"""Dot: small filled circle."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

dots = VCollection(
    Dot(fill='#FFFFFF'),
    Dot(r=20, fill='#58C4DD'),
    Dot(r=30, fill='#FF6B6B'),
    AnnotationDot(fill='#83C167'),
)
dots.arrange(direction='right', buff=80)
dots.center_to_pos()

v.add(dots)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_dot.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
