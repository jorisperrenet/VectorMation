"""Badge pill-shaped label."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

b1 = Badge(text='v2.0', x=860, y=520, bg_color='#58C4DD', text_color='#000')
b2 = Badge(text='stable', x=960, y=520, bg_color='#2ECC71', text_color='#000')
b3 = Badge(text='beta', x=1050, y=520, bg_color='#F39C12', text_color='#000')

v.add(b1, b2, b3)

v.show(end=0)
