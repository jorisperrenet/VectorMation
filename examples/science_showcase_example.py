"""Showcase of science/electronics classes: Resistor, Capacitor, NeuralNetwork, Pendulum."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim(verbose=args.verbose, save_dir='svgs/science_showcase')

title = Text("Science & Electronics", x=960, y=50, font_size=40, fill='#fff')
title.fadein(start=0, end=0.5)

# --- Circuit components (left side) ---
r = Resistor(x1=200, y1=250, x2=500, y2=250, label='R₁', stroke='#E74C3C')
r.fadein(start=0.5, end=1.5)

c = Capacitor(x1=200, y1=400, x2=500, y2=400, label='C₁', stroke='#3498DB')
c.fadein(start=1, end=2)

ind = Inductor(x1=200, y1=550, x2=500, y2=550, label='L₁', stroke='#2ECC71')
ind.fadein(start=1.5, end=2.5)

d = Diode(x1=200, y1=700, x2=500, y2=700, label='D₁', stroke='#F39C12')
d.fadein(start=2, end=3)

# --- Neural Network (right side) ---
nn = NeuralNetwork([3, 4, 2], cx=1200, cy=450, width=400, height=400,
                   neuron_radius=18)
nn.fadein(start=2.5, end=3.5)
nn_label = Text("Neural Network", x=1200, y=150, font_size=22, fill='#888')
nn_label.fadein(start=2.5, end=3.5)

# --- Labels ---
for lbl, y in [("Resistor", 250), ("Capacitor", 400), ("Inductor", 550), ("Diode", 700)]:
    t = Text(lbl, x=100, y=y - 30, font_size=16, fill='#888')
    t.fadein(start=0.5, end=1)
    v.add(t)

# Fade out
for obj in [title, r, c, ind, d, nn, nn_label]:
    obj.fadeout(start=8, end=9)

v.add(title, r, c, ind, d, nn, nn_label)
if not args.no_display:
    v.browser_display(end=args.duration or 10, fps=args.fps, port=args.port, hot_reload=args.hot_reload)
