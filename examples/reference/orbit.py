"""Planet orbiting a point."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

sun = Dot(cx=960, cy=540, r=30, fill='#FFFF00')
sun.fadein(start=0, end=0.5)

planet = Dot(cx=1200, cy=540, r=12, fill='#58C4DD')
planet.fadein(start=0, end=0.5)
planet.orbit(960, 540, start=0.5, end=4.5)

trail = planet.trace_path(start=0.5, end=4.5, stroke='#58C4DD',
                          stroke_width=1, stroke_opacity=0.4)

v.add(sun, trail, planet)

v.show(end=5)
