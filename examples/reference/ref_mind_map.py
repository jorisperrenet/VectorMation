"""MindMap radial diagram."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

tree = ('AI', [
    ('ML', [
        ('Supervised', []),
        ('Unsupervised', []),
    ]),
    ('NLP', [
        ('Transformers', []),
    ]),
    ('Vision', [
        ('CNNs', []),
        ('GANs', []),
    ]),
    ('Robotics', []),
])

chart = MindMap(tree, radius=280)

v.add(chart)

v.show(end=0)
