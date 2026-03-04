"""Stagger fadein animation."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

dots = VCollection(*[Dot(cx=200 + i * 80, cy=540, r=15,
                         fill=['#E74C3C', '#E67E22', '#F1C40F', '#2ECC71', '#1ABC9C',
                              '#3498DB', '#9B59B6', '#E91E63', '#E74C3C', '#E67E22',
                              '#F1C40F', '#2ECC71', '#1ABC9C', '#3498DB', '#9B59B6',
                              '#E91E63'][i]) for i in range(16)])
dots.center_to_pos()
dots.stagger('fadein', start=0, end=2, overlap=0.5)

v.add(dots)
if args.for_docs:
    v.export_video('docs/source/_static/videos/stagger.mp4', fps=30, end=3)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=3)
