"""Manim equivalent: OpeningManim -- text, transforms, and grid."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/manim/opening_manim')
canvas.set_background()

# Step 1: Title and formula arranged vertically, write + fadein
title = TexObject(r'This is some \LaTeX', font_size=50)
title.center_to_pos(posx=960, posy=370)
title.write(0, 1.5)

formula = TexObject(r'$$\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}$$',
                    font_size=140)
formula.center_to_pos(posx=960, posy=600)
formula.fadein(0.5, 1.5)

# Step 2: Transform title -> "That was a transform" and move to UL corner,
#          while formula fades out downward
transform_title = TexObject('That was a transform', font_size=50)
transform_title.center_to_pos(posx=250, posy=100)
transform_title.fadein(2.5, 3.5, change_existence=True)

morph = MorphObject(title, transform_title, start=2.5, end=3.5)

formula.shift(dy=100, start=2.5, end=3.5)
formula.fadeout(2.5, 3.5)

# Step 3: Fade out transform_title, fade in "This is a grid" at same position,
#          create the grid
grid_title = Text('This is a grid', x=250, y=100, font_size=72,
                  fill='#fff', stroke_width=0)
VObject.fade_transform(transform_title, grid_title, start=4, end=5)

grid = NumberPlane(creation=4)
grid.fadein(4, 6)

canvas.add_objects(grid, morph, formula, grid_title)
if args.verbose:
    canvas.export_video('docs/source/_static/videos/opening_manim.mp4', fps=30)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
