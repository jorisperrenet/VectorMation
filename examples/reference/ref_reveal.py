"""VCollection.reveal: staggered reveal of children sliding into view."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

items = VCollection(*[
    Text(word, font_size=48, fill='#fff')
    for word in ['Hello', 'World', 'From', 'VectorMation']
])
items.arrange(direction='right', buff=30)
items.center_to_pos()
items.reveal(start=0, end=2, direction='left')

v.add(items)

v.show(end=2.5)
