"""BohrAtom: Carbon atom with electron configuration."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

carbon = BohrAtom(protons=6, neutrons=6, nucleus_r=40, shell_spacing=60)

v.add(carbon)

v.show(end=0)
