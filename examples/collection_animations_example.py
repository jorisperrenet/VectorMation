"""Showcase VCollection animation methods: fadein, fadeout, grow, spin, etc."""
from vectormation.objects import *

v = VectorMathAnim(duration=10)

# Create a group of circles
circles = VGroup(*[
    Circle(r=30, cx=400 + i * 80, cy=200, fill=c, fill_opacity=0.8, stroke_width=2)
    for i, c in enumerate(('#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
                           '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'))
])

# Fade in the whole group at once
circles.fadein(start=0, end=1.5)

# Create some rectangles
rects = VGroup(*[
    RoundedRectangle(60, 40, x=400 + i * 80, y=400, rx=8, fill=c, fill_opacity=0.8)
    for i, c in enumerate(('#E74C3C', '#3498DB', '#2ECC71', '#F39C12',
                           '#9B59B6', '#1ABC9C', '#E67E22', '#34495E'))
])

# Grow from center
rects.grow_from_center(start=2, end=3.5)

# Create stars
stars = VGroup(*[
    Star(5, outer_r=25, inner_r=12, cx=400 + i * 80, cy=600,
         fill='#FFD700', fill_opacity=0.9, stroke='#DAA520')
    for i in range(8)
])

# Spin in
stars.spin_in(start=4, end=5.5)

# Indicate the circles
circles.indicate(start=6, end=7)

# Fade out everything with stagger
circles.fadeout(start=8, end=9)
rects.fadeout(start=8.3, end=9.3)
stars.spin_out(start=8.6, end=9.6)

v.add(circles, rects, stars)
v.render()
