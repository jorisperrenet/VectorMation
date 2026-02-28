import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/crossout_pulse')
canvas.set_background()

title = Text(text='Cross Out, Pulse Color & Stamp', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Cross out effect
wrong = Text(text='2 + 2 = 5', x=300, y=250, font_size=48,
             fill='#fff', stroke_width=0)
wrong.fadein(0.5, 1)
cross = wrong.cross_out(start=1.5, end=2, color='#FC6255', stroke_width=5)

correct = Text(text='2 + 2 = 4', x=300, y=350, font_size=48,
               fill='#83C167', stroke_width=0)
correct.fadein(2.5, 3)

# Pulse color effect
circle = Circle(r=50, cx=800, cy=300, fill='#58C4DD', stroke_width=2, stroke='#fff')
circle.fadein(0.5, 1)
circle.pulse_color('#FF6B6B', start=1.5, end=4, n_pulses=4)

pulse_label = Text(text='Pulsing!', x=800, y=380, font_size=20,
                   fill='#aaa', stroke_width=0, text_anchor='middle')
pulse_label.fadein(1, 1.5)

# Stamp effect: leave ghost copies
moving_rect = Rectangle(width=60, height=40, x=1100, y=250,
                         fill='#FFFF00', stroke_width=0)
moving_rect.fadein(0.5, 1)
moving_rect.shift(dx=400, start=1, end=5)

ghosts = [moving_rect.stamp(time=t, opacity=0.15) for t in [1.5, 2.5, 3.5]]

# All objects
canvas.add_objects(wrong, cross, correct, circle, pulse_label,
                   moving_rect, *ghosts, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
