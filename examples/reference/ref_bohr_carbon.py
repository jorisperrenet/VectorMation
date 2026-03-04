"""BohrAtom: Carbon atom with electron configuration."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

carbon = BohrAtom(protons=6, neutrons=6, nucleus_r=40, shell_spacing=60)

v.add(carbon)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_bohr_carbon.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
