import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/vector_field')
canvas.set_background()

# Create a vector field showing a rotation + source pattern
def field_func(x, y):
    return (-y + x * 0.3, x + y * 0.3)

vf = ArrowVectorField(
    field_func,
    x_range=(60, 1860, 120),
    y_range=(60, 1020, 120),
    max_length=80,
    stroke='#58C4DD',
    stroke_width=2,
)
vf.fadein(0, 1.5)

title = Text(text='Vector Field: Spiral Source', x=960, y=30,
             font_size=48, fill='#fff', stroke_width=0, text_anchor='middle')
title.write(0, 1)

canvas.add_objects(vf, title)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/vector_field_example.mp4', fps=30, end=2)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
