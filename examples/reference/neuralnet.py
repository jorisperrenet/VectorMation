"""Neural network with forward propagation."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

nn = NeuralNetwork([3, 5, 4, 2], width=800, height=500)
nn.label_input(['x1', 'x2', 'x3'])
nn.label_output(['y1', 'y2'])
nn.fadein(start=0, end=1)
nn.propagate(start=1.5, end=4.5)

v.add(nn)
if args.for_docs:
    v.export_video('docs/source/_static/videos/neuralnet.mp4', fps=30, end=5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=5)
