"""Dot: small filled circle."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

dots = VCollection(
    Dot(fill='#FFFFFF'),
    Dot(r=20, fill='#58C4DD'),
    Dot(r=30, fill='#FF6B6B'),
    AnnotationDot(fill='#83C167'),
)
dots.arrange(direction='right', buff=80)
dots.center_to_pos()

v.add(dots)

v.show(end=0)
