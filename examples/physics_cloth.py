"""Cloth simulation with the top row pinned, fluttering under gravity."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/physics_cloth')
canvas.set_background()

duration = 8

# Title
title = Text(text='Cloth Simulation', x=960, y=60,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Create a cloth: top row pinned, draping under gravity
# Centered horizontally, starting near the top of the canvas
cloth = Cloth(
    x=460, y=150,
    width=1000, height=600,
    cols=20, rows=14,
    pin_top=True,
    stiffness=3.0,
    color='#58C4DD',
)

# Add a gentle sideways wind force that varies over time
import math
def wind_force(body, t):
    # Oscillating horizontal wind with some vertical turbulence
    wind_x = 60 * math.sin(t * 1.2) + 20 * math.sin(t * 3.7)
    wind_y = 15 * math.cos(t * 2.5)
    return (wind_x, wind_y)

cloth.space.add_force(wind_force)
cloth.space.add_drag(coefficient=0.01)

# Run the simulation
cloth.simulate(duration=duration)

# Get all the visual objects (lines + dots)
cloth_objects = cloth.objects()

# Add everything to canvas
canvas.add_objects(title, *cloth_objects)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/physics_cloth.mp4', fps=30, end=8)
if not args.no_display:
    canvas.browser_display(start=0, end=duration, fps=args.fps, port=args.port,
                           hot_reload=True)
