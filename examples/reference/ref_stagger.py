"""Stagger method: staggered animation across children."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

squares = VCollection(*[
    Rectangle(60, 60, fill=['#E74C3C', '#E67E22', '#F1C40F', '#2ECC71',
                            '#3498DB', '#9B59B6', '#E91E63', '#1ABC9C'][i],
              fill_opacity=0.9) for i in range(8)
])
squares.arrange(direction='right', buff=20)
squares.center_to_pos()
squares.stagger('rotate_by', start=0.3, end=2.5, overlap=0.5, degrees=360)

v.add(squares)

v.show(end=3)
