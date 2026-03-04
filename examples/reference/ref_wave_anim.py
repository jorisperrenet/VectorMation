"""VCollection.wave_anim: wave animation through children."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

dots = VCollection(*[
    Dot(r=18, fill=['#E74C3C', '#E67E22', '#F1C40F', '#2ECC71',
                    '#3498DB', '#9B59B6', '#E91E63', '#1ABC9C',
                    '#E74C3C', '#E67E22', '#F1C40F', '#2ECC71'][i])
    for i in range(12)
])
dots.arrange(direction='right', buff=30)
dots.center_to_pos()
dots.wave_anim(start=0, end=3, amplitude=60, n_waves=2)

v.add(dots)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_wave_anim.mp4', fps=30, end=3)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=3)
