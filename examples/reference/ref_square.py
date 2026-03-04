"""Square shape."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

squares = VCollection(
    Square(side=120, fill='#58C4DD', fill_opacity=0.7, stroke='#58C4DD'),
    Square(side=160, fill='#FF6B6B', fill_opacity=0.7, stroke='#FF6B6B'),
    Square(side=200, fill='#83C167', fill_opacity=0.7, stroke='#83C167'),
)
squares.arrange(direction='right', buff=60)
squares.center_to_pos()

v.add(squares)

v.show(end=0)
