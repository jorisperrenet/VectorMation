"""Stagger fadein animation."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

dots = VCollection(*[Dot(cx=200 + i * 80, cy=540, r=15,
                         fill=['#E74C3C', '#E67E22', '#F1C40F', '#2ECC71', '#1ABC9C',
                              '#3498DB', '#9B59B6', '#E91E63', '#E74C3C', '#E67E22',
                              '#F1C40F', '#2ECC71', '#1ABC9C', '#3498DB', '#9B59B6',
                              '#E91E63'][i]) for i in range(16)])
dots.center_to_pos()
dots.stagger('fadein', start=0, end=2, overlap=0.5)

v.add(dots)

v.show(end=3)
