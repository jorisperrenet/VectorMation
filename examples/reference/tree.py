"""Tree with highlighted search path."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

tree = Tree(('8', [
    ('3', [('1', []), ('6', [('4', []), ('7', [])])]),
    ('10', [('', []), ('14', [('13', [])])]),
]))
tree.center_to_pos()

v.add(tree)

v.show(end=2)
