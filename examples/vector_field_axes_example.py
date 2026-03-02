import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/vector_field_axes')
canvas.set_background()

title = Text(text='Vector Field & Set Width/Height', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Vector field on axes
ax = Axes(x_range=(-3, 3), y_range=(-3, 3),
          plot_width=600, plot_height=500,
          x=80, y=130)
ax.add_coordinates()
ax_title = ax.add_title('Rotation Field', font_size=24, fill='#aaa')
ax.fadein(0.5, 1.5)

# Rotation vector field: F(x,y) = (-y, x)
vf = ax.plot_vector_field(lambda x, y: (-y, x), x_step=0.7, y_step=0.7,
                           max_length=50, stroke='#83C167', fill='#83C167')
vf.fadein(1.5, 3)

# Set width/height demo
r1 = Rectangle(width=200, height=100, x=850, y=200, fill='#FF6B6B',
               fill_opacity=0.7, stroke_width=2, stroke='#fff')
r1.fadein(0.5, 1)

label1 = Text(text='set_width(400)', x=1050, y=340, font_size=20,
              fill='#aaa', stroke_width=0, text_anchor='middle')
label1.fadein(1.5, 2)
r1.set_width(400, start=2)

r2 = Rectangle(width=200, height=100, x=850, y=400, fill='#58C4DD',
               fill_opacity=0.7, stroke_width=2, stroke='#fff')
r2.fadein(0.5, 1)

label2 = Text(text='set_height(200, stretch)', x=1050, y=540, font_size=20,
              fill='#aaa', stroke_width=0, text_anchor='middle')
label2.fadein(2.5, 3)
r2.set_height(200, start=3, stretch=True)

canvas.add_objects(ax, r1, r2, label1, label2, title)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/vector_field_axes_example.mp4', fps=30, end=4)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
