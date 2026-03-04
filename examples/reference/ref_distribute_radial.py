"""VCollection.distribute_radial: arrange children in a circle."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

group = VCollection(*[
    RegularPolygon(n, radius=30, fill=['#E74C3C', '#E67E22', '#F1C40F',
                                        '#2ECC71', '#3498DB', '#9B59B6'][i],
                   fill_opacity=0.8, stroke='#fff', stroke_width=2)
    for i, n in enumerate([3, 4, 5, 6, 7, 8])
])
group.distribute_radial(cx=960, cy=540, radius=250)

v.add(group)

v.show(end=0)
