"""VCollection.distribute_radial: arrange children in a circle."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

group = VCollection(*[
    RegularPolygon(n, radius=30, fill=['#E74C3C', '#E67E22', '#F1C40F',
                                        '#2ECC71', '#3498DB', '#9B59B6'][i],
                   fill_opacity=0.8, stroke='#fff', stroke_width=2)
    for i, n in enumerate([3, 4, 5, 6, 7, 8])
])
group.distribute_radial(cx=960, cy=540, radius=250)

v.add(group)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_distribute_radial.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
