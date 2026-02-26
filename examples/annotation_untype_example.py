import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/annotation_untype')
canvas.set_background()

title = Text(text='Arrow Annotation & Untype', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Axes with annotations
ax = Axes(x_range=(-1, 5), y_range=(-1, 10),
          plot_width=700, plot_height=400,
          x=100, y=180)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

f = lambda x: x ** 2
curve = ax.plot(f, stroke='#58C4DD', stroke_width=3)
curve.create(1.5, 2.5)

# Arrow annotations at key points
ann1 = ax.add_arrow_annotation(1, 1, 'minimum area', direction='down',
                                fill='#83C167', stroke='#83C167')
ann1.fadein(2.5, 3)

ann2 = ax.add_arrow_annotation(2, 4, 'f(2)=4', direction='left',
                                fill='#FF6B6B', stroke='#FF6B6B')
ann2.fadein(3, 3.5)

ann3 = ax.add_arrow_annotation(3, 9, 'peak', direction='up',
                                fill='#FFFF00', stroke='#FFFF00')
ann3.fadein(3.5, 4)

# Typewrite + untype demo
txt = Text(text='Hello, World!', x=1100, y=300, font_size=42,
           fill='#fff', stroke_width=0)
txt.typewrite(start=1, end=3, cursor='|')

untype_label = Text(text='(reverse typewriter)', x=1100, y=360, font_size=18,
                    fill='#aaa', stroke_width=0)
untype_label.fadein(4, 4.5)

txt.untype(start=5, end=7)

canvas.add_objects(ax, txt, untype_label, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
