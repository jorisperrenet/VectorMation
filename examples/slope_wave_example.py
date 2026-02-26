import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/slope_wave')
canvas.set_background()

title = Text(text='Slope Field, Wave & Glitch', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Slope field for dy/dx = -x/y (circle field)
ax = Axes(x_range=(-3, 3), y_range=(-3, 3),
          plot_width=500, plot_height=500,
          x=100, y=150)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

field = ax.add_slope_field(
    lambda x, y: -x / y if abs(y) > 0.01 else 0,
    x_step=0.5, y_step=0.5, seg_length=0.2,
    stroke='#58C4DD', stroke_width=1)
field.fadein(1.5, 2.5)

# Wave effect demo
dots = VCollection(
    *[Dot(cx=1100 + i * 50, cy=500, r=12, fill='#FF6B6B') for i in range(10)]
)
dots.fadein(2.5, 3)

wave_label = Text(text='Wave Effect', x=1350, y=430,
                  font_size=24, fill='#aaa', stroke_width=0, text_anchor='middle')
wave_label.fadein(2.5, 3)

dots.wave_effect(start=3, end=5, amplitude=30, axis='y')

# Glitch effect demo
glitch_text = Text(text='GLITCH', x=1350, y=700,
                   font_size=48, fill='#83C167', stroke_width=0, text_anchor='middle')
glitch_text.fadein(3.5, 4)
glitch_text.glitch(start=4, end=5.5, intensity=15, flashes=8)

glitch_rect = Rectangle(120, 80, x=1150, y=660, fill='#FFFF00', fill_opacity=0.5,
                         stroke='#FFFF00', stroke_width=2)
glitch_rect.fadein(3.5, 4)
glitch_rect.glitch(start=4.5, end=6, intensity=20, flashes=6)

canvas.add_objects(ax, title, dots, wave_label, glitch_text, glitch_rect)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
