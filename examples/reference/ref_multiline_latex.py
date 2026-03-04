"""SplitTexObject: multi-line LaTeX derivation."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

equations = SplitTexObject(
    r'$$\Delta = b^2 - 4ac$$',
    r'$$x = \frac{-b \pm \sqrt{\Delta}}{2a}$$',
    line_spacing=80, font_size=48,
)
for i, line in enumerate(equations):
    line.center_to_pos(posy=440 + i * 120)
    v.add(line)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_multiline_latex.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
