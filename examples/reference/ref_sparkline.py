"""SparkLine inline chart."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

spark = SparkLine(
    data=[10, 14, 12, 18, 15, 22, 20, 26, 24, 30, 28, 35],
    x=560, y=440, width=800, height=200,
    stroke='#58C4DD', stroke_width=3, show_endpoint=True,
)

v.add(spark)

v.show(end=0)
