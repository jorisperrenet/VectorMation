import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/textbox_bracket_icongrid')
canvas.set_background()

title = Text(text='TextBox, Bracket, Area Chart & Icon Grid', x=960, y=40,
             font_size=28, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# --- TextBox examples ---
tb1 = TextBox('Important Note', x=50, y=120, font_size=18, box_fill='#2a4a6b')
tb1.fadein(1, 2)

tb2 = TextBox('Warning!', x=50, y=180, font_size=22, box_fill='#6b2a2a',
              corner_radius=12, padding=16)
tb2.fadein(1.2, 2.2)

tb3 = TextBox('Success', x=50, y=250, font_size=16, box_fill='#2a6b3a',
              corner_radius=3)
tb3.fadein(1.4, 2.4)

# --- Bracket examples ---
line1 = Line(x1=450, y1=150, x2=750, y2=150, stroke='#58C4DD', stroke_width=2)
line1.fadein(1, 1.5)

br1 = Bracket(x=450, y=155, width=300, direction='down', text='300px span',
              font_size=16, height=15)
br1.fadein(1.5, 2.5)

br2 = Bracket(x=450, y=200, width=150, direction='down', text='First half',
              font_size=14, height=12, stroke='#83C167')
br2.fadein(2, 3)

# --- Area chart ---
ax = Axes(x_range=(0, 6), y_range=(0, 5),
          plot_width=350, plot_height=220, x=50, y=400)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

area = ax.plot_area(lambda x: 2 + math.sin(x) * 1.5, baseline=0,
                    fill='#58C4DD', fill_opacity=0.25)
area.fadein(1.5, 2.5)

curve = ax.plot(lambda x: 2 + math.sin(x) * 1.5, stroke='#58C4DD', stroke_width=2)
curve.fadein(1.5, 2.5)

area_label = Text(text='Area Chart', x=225, y=385,
                  font_size=18, fill='#aaa', stroke_width=0, text_anchor='middle')
area_label.fadein(1, 1.5)

# --- Icon Grid ---
ig = IconGrid([
    (30, '#58C4DD'), (20, '#83C167'), (10, '#FF6B6B'),
    (5, '#FFFF00'), (35, '#666'),
], x=550, y=400, cols=10, size=18, gap=3)
ig.fadein(2, 3)

ig_label = Text(text='Icon Grid (100 units)', x=700, y=385,
                font_size=18, fill='#aaa', stroke_width=0, text_anchor='middle')
ig_label.fadein(1, 1.5)

canvas.add_objects(title, tb1, tb2, tb3, line1, br1, br2,
                   ax, area, curve, area_label,
                   ig, ig_label)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/textbox_bracket_icongrid_example.mp4', fps=30, end=3)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
