"""VCollection.shuffle_animate() randomly shuffling shape positions."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

colors = ['#58C4DD', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6']
group = VCollection(
    *[Circle(r=40, fill=c, fill_opacity=0.8) for c in colors]
)
group.arrange(direction='right', buff=40)
group.center_to_pos()

group.shuffle_animate(start=0.5, end=2)

v.add(group)

v.show(end=2.5)
