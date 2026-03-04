"""Neural network with forward propagation."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

nn = NeuralNetwork([3, 5, 4, 2], width=800, height=500)
nn.label_input(['x1', 'x2', 'x3'])
nn.label_output(['y1', 'y2'])
nn.fadein(start=0, end=1)
nn.propagate(start=1.5, end=4.5)

v.add(nn)

v.show(end=5)
