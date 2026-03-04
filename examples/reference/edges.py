"""get_edge() positions diagram."""
from vectormation.objects import *

W, H = 440, 320
v = VectorMathAnim(width=W, height=H)
v.set_background(fill='#1e1e2e')

RX, RY, RW, RH = 120, 80, 200, 140
v.add(Rectangle(RW, RH, x=RX, y=RY,
                fill='#58C4DD', fill_opacity=0.1, stroke='#58C4DD', stroke_width=2))

edges = [
    ('top_left',     RX,          RY,          RX - 55,     RY - 10),
    ('top',          RX + RW//2,  RY,          RX + RW//2 - 10, RY - 14),
    ('top_right',    RX + RW,     RY,          RX + RW + 6, RY - 10),
    ('left',         RX,          RY + RH//2,  RX - 30,     RY + RH//2 + 15),
    ('center',       RX + RW//2,  RY + RH//2,  RX + RW//2 + 8, RY + RH//2 + 15),
    ('right',        RX + RW,     RY + RH//2,  RX + RW + 6, RY + RH//2 + 15),
    ('bottom_left',  RX,          RY + RH,     RX - 70,     RY + RH + 16),
    ('bottom',       RX + RW//2,  RY + RH,     RX + RW//2 - 18, RY + RH + 18),
    ('bottom_right', RX + RW,     RY + RH,     RX + RW + 6, RY + RH + 16),
]

for name, ex, ey, lx, ly in edges:
    color = '#f38ba8' if name == 'center' else '#a6e3a1'
    v.add(
        Dot(r=4, cx=ex, cy=ey, fill=color, stroke_width=0),
        Text(name, x=lx, y=ly, font_size=10, fill=color),
    )

v.add(Text('get_edge() positions', x=145, y=275, font_size=14, fill='#cdd6f4'))
v.add(Text("obj.get_edge('top_right')  →  (x, y)", x=90, y=300, font_size=11, fill='#585b70'))

v.show(end=2)
