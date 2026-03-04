from vectormation.objects import *

canvas = VectorMathAnim()
canvas.set_background()

# Objects scattered across the canvas
c1 = Circle(r=60, cx=300, cy=300, fill='#58C4DD', fill_opacity=0.8)
c1.fadein(0, 0.5)

c2 = Circle(r=40, cx=1600, cy=700, fill='#83C167', fill_opacity=0.8)
c2.fadein(0, 0.5)

label1 = Text(text='Object A', x=300, y=220, font_size=24, fill='#fff', stroke_width=0,
              text_anchor='middle')
label1.fadein(0, 0.5)

label2 = Text(text='Object B', x=1560, y=650, font_size=24, fill='#fff', stroke_width=0)
label2.fadein(0, 0.5)

# Focus on first object
canvas.focus_on(c1, label1, start=1, end=2, padding=80)

# Reset view
canvas.camera_reset(3, 4)

# Focus on second object
canvas.focus_on(c2, label2, start=5, end=6, padding=80)

# Reset view
canvas.camera_reset(7, 8)

title = Text(text='Camera Focus Demo', x=960, y=80,
             font_size=48, fill='#FFFF00', stroke_width=0, text_anchor='middle')
title.write(0, 1)

canvas.add_objects(c1, c2, label1, label2, title)

canvas.show(end=6)
