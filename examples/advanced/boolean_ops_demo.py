"""Boolean Operations Demo — Union, Intersection, Difference, Exclusion."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/boolean_ops')
canvas.set_background()

title = TexObject(r'Boolean Operations', x=960, y=70, font_size=52,
                  fill='#FFFFFF', stroke_width=0, anchor='center')
title.fadein(0.0, 0.5)
canvas.add(title)

# --- Reference circles (faded, shown briefly at center) ---
ref_a = Circle(r=80, cx=910, cy=320, fill='#58C4DD', fill_opacity=0.25,
               stroke='#58C4DD', stroke_width=1.5, stroke_dasharray='6 4')
ref_b = Circle(r=80, cx=1000, cy=320, fill='#E84D60', fill_opacity=0.25,
               stroke='#E84D60', stroke_width=1.5, stroke_dasharray='6 4')
for obj in [ref_a, ref_b]:
    obj.fadein(0.2, 0.6)
    canvas.add(obj)

# Column positions for the four operations
cols = [270, 690, 1110, 1530]
row_y = 550
label_y = 730

ops = [
    ('Union',        cols[0], '#4ECDC4', Union),
    ('Intersection', cols[1], '#9B59B6', Intersection),
    ('Difference',   cols[2], '#F5A623', Difference),
    ('Exclusion',    cols[3], '#E84D60', Exclusion),
]

for i, (name, cx, color, OpClass) in enumerate(ops):
    t0 = 0.8 + i * 0.5

    shape = OpClass(
        Circle(r=80, cx=cx - 45, cy=row_y),
        Circle(r=80, cx=cx + 45, cy=row_y),
        fill=color, fill_opacity=0.75, stroke='#FFFFFF', stroke_width=2,
    )
    shape.grow_from_center(start=t0, end=t0 + 0.5)
    canvas.add(shape)

    # Dashed reference circles
    for dx in [-45, 45]:
        ref = Circle(r=80, cx=cx + dx, cy=row_y, fill_opacity=0,
                     stroke=color, stroke_width=1, stroke_dasharray='5 3')
        ref.fadein(t0, t0 + 0.5)
        canvas.add(ref)

    label = TexObject(name, x=cx, y=label_y, font_size=30,
                      fill=color, stroke_width=0, anchor='center')
    label.fadein(t0 + 0.2, t0 + 0.6)
    canvas.add(label)

T = 5.0
if args.for_docs:
    canvas.export_video('docs/source/_static/videos/boolean_ops_demo.mp4', fps=30, end=T)
if not args.for_docs:
    canvas.browser_display(start=args.start or 0, end=args.end or T, fps=args.fps, port=args.port)
