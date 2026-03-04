"""Tree with highlighted search path."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

tree = Tree(('8', [
    ('3', [('1', []), ('6', [('4', []), ('7', [])])]),
    ('10', [('', []), ('14', [('13', [])])]),
]))
tree.center_to_pos()

v.add(tree)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/tree.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
