import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/clone')
canvas.set_background()

title = Text(text='Clone & Filter', x=960, y=60,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Create a star and clone it into a row
star = Star(n=5, outer_radius=40, inner_radius=20, cx=200, cy=300,
            fill='#FFFF00', fill_opacity=0.8)
star.fadein(0, 1)

clones = star.clone(count=6, dx=120)
clones.stagger('fadein', delay=0.2, start=0.5, end=1.5)

# Create circles and use filter to animate only large ones
circles = VGroup(
    Circle(r=30, cx=300, cy=600, fill='#58C4DD', fill_opacity=0.7),
    Circle(r=60, cx=500, cy=600, fill='#83C167', fill_opacity=0.7),
    Circle(r=20, cx=700, cy=600, fill='#FC6255', fill_opacity=0.7),
    Circle(r=50, cx=900, cy=600, fill='#9A72AC', fill_opacity=0.7),
    Circle(r=15, cx=1100, cy=600, fill='#F0AC5F', fill_opacity=0.7),
)
circles.fadein(0, 1)

# Filter: pulse only circles with radius > 40
big = circles.filter(lambda obj: obj.rx.at_time(0) > 40)
big.stagger('pulse', delay=0.3, start=2, end=3)

canvas.add_objects(title, star, clones, circles)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
