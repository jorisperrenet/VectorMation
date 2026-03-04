"""StandingWave: third harmonic."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

wave = StandingWave(
    x1=300, y1=540, x2=1620, y2=540,
    amplitude=100, harmonics=3, frequency=2.0,
    start=0, end=5, stroke='#58C4DD', stroke_width=3,
)

v.add(wave)

v.show(end=5)
