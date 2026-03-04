"""Stagger method: staggered animation across children."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

squares = VCollection(*[
    Rectangle(60, 60, fill=['#E74C3C', '#E67E22', '#F1C40F', '#2ECC71',
                            '#3498DB', '#9B59B6', '#E91E63', '#1ABC9C'][i],
              fill_opacity=0.9) for i in range(8)
])
squares.arrange(direction='right', buff=20)
squares.center_to_pos()
squares.stagger('rotate_by', start=0.3, end=2.5, overlap=0.5, degrees=360)

v.add(squares)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_stagger.mp4', fps=30, end=3)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=3)
