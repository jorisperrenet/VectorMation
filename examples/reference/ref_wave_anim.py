"""VCollection.wave_anim: wave animation through children."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

dots = VCollection(*[
    Dot(r=18, fill=['#E74C3C', '#E67E22', '#F1C40F', '#2ECC71',
                    '#3498DB', '#9B59B6', '#E91E63', '#1ABC9C',
                    '#E74C3C', '#E67E22', '#F1C40F', '#2ECC71'][i])
    for i in range(12)
])
dots.arrange(direction='right', buff=30)
dots.center_to_pos()
dots.wave_anim(start=0, end=3, amplitude=60, n_waves=2)

v.add(dots)

v.show(end=3)
