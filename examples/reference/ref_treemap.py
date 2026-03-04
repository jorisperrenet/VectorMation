"""TreeMap visualization of category sizes."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

chart = TreeMap(
    data=[
        ('Python', 35),
        ('JavaScript', 28),
        ('TypeScript', 18),
        ('Rust', 12),
        ('Go', 10),
        ('Java', 8),
        ('C++', 6),
        ('Ruby', 4),
    ],
    x=260, y=140, width=1400, height=800,
    font_size=18,
)

v.add(chart)

v.show(end=0)
