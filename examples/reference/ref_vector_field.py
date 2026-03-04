"""Arrow vector field (ArrowVectorField)."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

def field(x, y):
    return (y - 540, -(x - 960))

vf = ArrowVectorField(field, x_range=(100, 1820, 150),
                       y_range=(100, 980, 150),
                       max_length=70, stroke='#58C4DD')
v.add(vf)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_vector_field.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
