"""TagCloud with weighted words."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

cloud = TagCloud(
    data=[
        ('Python', 10), ('Animation', 8), ('SVG', 7), ('Math', 6),
        ('Vector', 5), ('Graphics', 4), ('Code', 3), ('Design', 3),
        ('Canvas', 2), ('Render', 2),
    ],
    x=560, y=400, width=800,
    colors=['#58C4DD', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6', '#3498DB'],
)

v.add(cloud)

v.show(end=0)
