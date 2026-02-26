import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/trail_reveal')
canvas.set_background()

title = Text(text='Trail, Reveal & Min/Max Labels', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Trail demo — ball moving in arc
ball = Dot(cx=200, cy=500, r=15, fill='#FF6B6B')
ball.fadein(1, 1.3)
ball.path_arc(700, 400, start=1.5, end=3.5, angle=math.pi / 3)
ghosts = ball.trail(start=1.5, end=3.5, num_copies=6)

# Reveal demo — letters appearing
letters = VCollection(
    *[Text(text=ch, x=1100 + i * 40, y=500,
           font_size=36, fill='#83C167', stroke_width=0, text_anchor='middle')
      for i, ch in enumerate('REVEAL')]
)
letters.reveal(start=2, end=3.5, direction='left')

# Axes with min/max labels
ax = Axes(x_range=(-1, 7), y_range=(-2, 3),
          plot_width=500, plot_height=300,
          x=100, y=650)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

func = lambda x: math.sin(x * 1.5) * 2
curve = ax.plot(func, stroke='#58C4DD', stroke_width=3)
curve.create(1.5, 2.5)

labels = ax.add_min_max_labels(func, creation=2.5)
labels.fadein(2.5, 3)

canvas.add_objects(ax, title, ball, *ghosts, letters, labels)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
