"""PhysicsSpace: cloth simulation with wind."""
import math
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

duration = 5

# Create a cloth: top row pinned, draping under gravity
cloth = Cloth(
    x=510, y=120,
    width=900, height=300,
    cols=18, rows=10,
    pin_top=True,
    stiffness=18,
    color='#58C4DD',
)

# Add a gentle sideways wind force
def wind_force(body, t):
    wind_x = 30 * math.sin(t * 1.2) + 10 * math.sin(t * 3.7)
    wind_y = 8 * math.cos(t * 2.5)
    return (wind_x, wind_y)

cloth.space.add_force(wind_force)
cloth.space.add_drag(coefficient=0.02)

cloth.simulate(duration=duration)

v.add(*cloth.objects())

v.show(end=duration)
