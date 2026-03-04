"""BulletedList example."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

bl = BulletedList(
    'Install dependencies',
    'Configure settings',
    'Run the application',
    font_size=40, fill='#fff', stroke_width=0,
)
v.add(bl)

v.show(end=0)
