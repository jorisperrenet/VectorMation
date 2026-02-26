import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/bar_heartbeat')
canvas.set_background()

title = Text(text='Bar Plot, Heartbeat & Flip', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Bar chart on axes
ax = Axes(x_range=(0, 7), y_range=(0, 10),
          plot_width=500, plot_height=350,
          x=100, y=150)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

x_vals = [1, 2, 3, 4, 5, 6]
y_vals = [3, 7, 5, 9, 4, 6]
bars = ax.plot_bar(x_vals, y_vals, width=0.7, creation=1.5,
                   fill='#83C167', fill_opacity=0.6, stroke='#83C167')
bars.fadein(1.5, 2.5)

# Heartbeat on a circle
heart = Circle(cx=1300, cy=350, r=60, fill='#FF6B6B', stroke='#FF6B6B')
heart.fadein(1, 1.5)
heart.heartbeat(start=2, end=5, beats=4, scale_factor=1.4)

heart_label = Text(text='Heartbeat', x=1300, y=250,
                   font_size=24, fill='#aaa', stroke_width=0, text_anchor='middle')
heart_label.fadein(1, 1.5)

# Flip demo
letters = VCollection(
    *[Text(text=ch, x=800 + i * 60, y=750,
           font_size=48, fill='#FFFF00', stroke_width=0, text_anchor='middle')
      for i, ch in enumerate('ABCDE')]
)
letters.fadein(1, 1.5)
letters.flip_all(start=3, end=4, axis='x')

flip_label = Text(text='Flip All', x=920, y=680,
                  font_size=24, fill='#aaa', stroke_width=0, text_anchor='middle')
flip_label.fadein(1, 1.5)

canvas.add_objects(ax, title, heart, heart_label, letters, flip_label)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
