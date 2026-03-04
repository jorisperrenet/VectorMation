"""ClipPath clipping a rectangle with a circle."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

clip = ClipPath(Circle(r=150, cx=960, cy=540))
v.add_def(clip)

rect = Rectangle(500, 500, fill='#58C4DD', fill_opacity=0.9,
                 stroke='#FFFFFF', stroke_width=3,
                 clip_path=clip.clip_ref())
rect.center_to_pos(posx=960, posy=540)

# Show the clip circle outline for reference
outline = Circle(r=150, cx=960, cy=540, fill_opacity=0,
                 stroke='#FFFF00', stroke_width=2, stroke_dasharray='8,6')
v.add(rect, outline)

v.show(end=0)
