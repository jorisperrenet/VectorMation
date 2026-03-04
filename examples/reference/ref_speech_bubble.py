"""SpeechBubble with tail."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

bubble = SpeechBubble(text='Hello there!', x=860, y=480, font_size=24,
                      tail_direction='down', box_fill='#1e1e2e', text_color='#fff')

v.add(bubble)

v.show(end=0)
