"""Neural network diagram with layer labels and forward propagation."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

canvas = VectorMathAnim(save_dir='svgs/neural_network')
canvas.set_background()

nn = NeuralNetwork([4, 6, 6, 3], cx=960, cy=540, width=900, height=500,
                   neuron_radius=18, neuron_fill='#58C4DD',
                   edge_color='#555', edge_width=1)
nn.label_input(['x₁', 'x₂', 'x₃', 'x₄'], font_size=24, buff=35)
nn.label_output(['y₁', 'y₂', 'y₃'], font_size=24, buff=35)

title = Text('Feed-Forward Neural Network', x=960, y=80, font_size=36,
             text_anchor='middle', fill='#fff')

nn.fadein(start=0, end=1)
title.fadein(start=0.5, end=1.5)
nn.propagate(start=2, end=4, delay=0.5, color='#FFFF00')

canvas.add_objects(nn, title)
args = parse_args()
if args.verbose:
    canvas.export_video('docs/source/_static/videos/neural_network_example.mp4', fps=30, end=5)
if not args.no_display:
    canvas.browser_display(start=0, end=5, fps=args.fps, port=args.port,
                           hot_reload=True)
