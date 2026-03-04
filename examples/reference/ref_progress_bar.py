"""ProgressBar at 70% fill."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

bar = ProgressBar(width=600, height=35, x=660, y=520, fill_color='#58C4DD')
bar.set_progress(0.7)

v.add(bar)

v.show(end=0)
