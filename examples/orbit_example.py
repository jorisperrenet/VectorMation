import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/orbit')
canvas.set_background()

title = Text(text='Orbit Animation', x=960, y=80,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Sun at center
sun = Circle(r=40, cx=960, cy=500, fill='#FFFF00', fill_opacity=0.9)
sun.fadein(0, 0.5)

# Orbiting planet
planet = Circle(r=15, cx=1200, cy=500, fill='#58C4DD', fill_opacity=0.9)
planet.fadein(0, 0.5)
planet.orbit(960, 500, start=0.5, end=6, degrees=720)

# Small moon orbiting the initial planet position
moon = Dot(cx=1250, cy=500, fill='#ccc')
moon.fadein(0, 0.5)
moon.orbit(1200, 500, radius=50, start=0.5, end=6, degrees=2160)

# Orbit path visualization
orbit_path = Circle(r=240, cx=960, cy=500, fill_opacity=0,
                    stroke='#444', stroke_width=1, stroke_dasharray='5 5')
orbit_path.fadein(0, 0.5)

canvas.add_objects(orbit_path, sun, planet, moon, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
