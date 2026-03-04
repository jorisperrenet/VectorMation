"""VennDiagram with three sets."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

venn = VennDiagram(
    labels=['Math', 'Science', 'Art'],
    colors=['#58C4DD', '#E74C3C', '#2ECC71'],
    radius=180,
)

v.add(venn)

v.show(end=0)
