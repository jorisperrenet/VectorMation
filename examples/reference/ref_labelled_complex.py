"""Labelled complex numbers on ComplexPlane."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

cp = ComplexPlane(x_range=(-3, 3), y_range=(-3, 3))
cp.add_coordinates()
cp.add_complex_label(1 + 2j, 'z\u2081')
cp.add_complex_label(-1 + 1j, 'z\u2082')
cp.add_complex_label(2 - 1j, 'z\u2083')

v.add(cp)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_labelled_complex.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
