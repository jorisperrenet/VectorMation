"""Cloth simulation with the top row pinned, fluttering under gravity."""
from vectormation.objects import *

canvas = VectorMathAnim()
canvas.set_background()

duration = 8

# Title
title = Text(text='Cloth Simulation', x=960, y=60,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Create a cloth: top row pinned, draping under gravity
# Centered horizontally, starting near the top of the canvas
cloth = Cloth(
    x=510, y=120,
    width=900, height=300,
    cols=18, rows=10,
    pin_top=True,
    stiffness=18,
    color='#58C4DD',
)

# Add a gentle sideways wind force that varies over time
import math
def wind_force(body, t):
    # Oscillating horizontal wind with some vertical turbulence
    wind_x = 30 * math.sin(t * 1.2) + 10 * math.sin(t * 3.7)
    wind_y = 8 * math.cos(t * 2.5)
    return (wind_x, wind_y)

cloth.space.add_force(wind_force)
cloth.space.add_drag(coefficient=0.02)

# Run the simulation
cloth.simulate(duration=duration)

# Get all the visual objects (lines + dots)
cloth_objects = cloth.objects()

# Add everything to canvas
canvas.add_objects(title, *cloth_objects)

canvas.show(end=8)
