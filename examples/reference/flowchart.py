"""Simple flowchart."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

flow = FlowChart(['Input', 'Validate', 'Process', 'Output'],
                 direction='right', box_color='#58C4DD', spacing=100)
flow.center_to_pos()

v.add(flow)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/flowchart.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
