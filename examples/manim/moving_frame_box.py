"""Manim equivalent: MovingFrameBox -- LaTeX with animated bounding rectangles."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(width=1920, height=540, verbose=args.verbose, save_dir='svgs/manim/moving_frame_box')
canvas.set_background()
text = TexObject(r'$$\frac{d}{dx}f(x)g(x)=f(x)\frac{d}{dx}g(x)+g(x)\frac{d}{dx}f(x)$$', font_size=120)
text.center_to_pos(posx=960, posy=270)
text.write(0, 1)
rect1 = text.brect(0, 13, 25, follow=False, buff=12)
rect2 = text.brect(0, 26, 38, follow=False, buff=12)
obj = MorphObject(rect1, rect2, start=2, end=4)

canvas.add_objects(text, obj, rect1, rect2)
if args.for_docs:
    canvas.export_video('docs/source/_static/videos/moving_frame_box.mp4', fps=30)
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
