import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/gradient')
canvas.set_background()

# Create gradients
sunset = LinearGradient([
    (0, '#FC6255'),
    (0.5, '#F0AC5F'),
    (1, '#FFFF00'),
])
canvas.add_def(sunset)

ocean = LinearGradient([
    (0, '#1e3a5f'),
    (0.5, '#58C4DD'),
    (1, '#5CD0B3'),
], x1='0%', y1='100%', x2='0%', y2='0%')  # vertical
canvas.add_def(ocean)

glow = RadialGradient([
    (0, '#FFFF00', 1),
    (0.5, '#FC6255', 0.6),
    (1, '#1e1e2e', 0),
])
canvas.add_def(glow)

# Apply gradients to shapes
r1 = Rectangle(400, 300, x=100, y=200, fill=sunset.fill_ref(),
               fill_opacity=1, stroke_width=0)
r1.fadein(0, 1)

r2 = Rectangle(400, 300, x=600, y=200, fill=ocean.fill_ref(),
               fill_opacity=1, stroke_width=0)
r2.fadein(0.3, 1.3)

c1 = Circle(r=150, cx=1500, cy=350, fill=glow.fill_ref(),
            fill_opacity=1, stroke_width=0)
c1.fadein(0.6, 1.6)

# Labels
l1 = Text(text='Linear (horizontal)', x=300, y=560, font_size=24,
          fill='#aaa', stroke_width=0, text_anchor='middle')
l2 = Text(text='Linear (vertical)', x=800, y=560, font_size=24,
          fill='#aaa', stroke_width=0, text_anchor='middle')
l3 = Text(text='Radial', x=1500, y=560, font_size=24,
          fill='#aaa', stroke_width=0, text_anchor='middle')
l1.fadein(0, 1)
l2.fadein(0, 1)
l3.fadein(0, 1)

title = Text(text='SVG Gradient Support', x=960, y=80,
             font_size=48, fill='#fff', stroke_width=0, text_anchor='middle')
title.write(0, 1)

canvas.add_objects(r1, r2, c1, l1, l2, l3, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
