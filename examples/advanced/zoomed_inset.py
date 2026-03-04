"""ZoomedInset Demo — magnify a region of the canvas."""
from vectormation.objects import *

canvas = VectorMathAnim()
canvas.set_background()

title = TexObject(r'ZoomedInset', x=960, y=70, font_size=52,
                  fill='#FFFFFF', stroke_width=0, anchor='center')
canvas.add(title)

# --- Small detailed scene to magnify (left side) ---
source_label = TexObject(r'Source region', x=350, y=770, font_size=22,
                         fill='#FFFFFF', stroke_width=0, anchor='center')
canvas.add(source_label)

tiny_sq = Square(side=40, x=300, y=550, fill='#4ECDC4',
                 stroke='#FFFFFF', stroke_width=1)
canvas.add(tiny_sq)

tiny_circle = Circle(r=18, cx=360, cy=575, fill='#E84D60',
                     stroke='#FFFFFF', stroke_width=1)
canvas.add(tiny_circle)

tiny_tri = EquilateralTriangle(side_length=35, cx=330, cy=510,
                               fill='#FFFF00', fill_opacity=0.6,
                               stroke='#FFFF00', stroke_width=1)
canvas.add(tiny_tri)

tiny_dot1 = Dot(cx=310, cy=490, r=6, fill='#9B59B6', stroke_width=0)
tiny_dot2 = Dot(cx=370, cy=530, r=5, fill='#83C167', stroke_width=0)
tiny_dot3 = Dot(cx=295, cy=590, r=7, fill='#F5A623', stroke_width=0)
canvas.add(tiny_dot1, tiny_dot2, tiny_dot3)

# Connector line from source to display
connect_line = DashedLine(x1=420, y1=500, x2=600, y2=300,
                          stroke='#FFFF00', stroke_width=1, stroke_opacity=0.5)
canvas.add(connect_line)

# ZoomedInset: magnify the tiny scene
zoomed_inset = ZoomedInset(
    canvas,
    source=(270, 475, 130, 140),
    display=(600, 200, 700, 600),
    creation=0, z=100,
    frame_color='#FFFF00', display_color='#FFFF00', frame_width=2,
)
canvas.add(zoomed_inset)

zoom_label = TexObject(r'Magnified detail', x=950, y=830, font_size=24,
                       fill='#FFFF00', stroke_width=0, anchor='center')
canvas.add(zoom_label)

canvas.show(end=0)
