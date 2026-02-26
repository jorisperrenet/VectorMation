import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()


# Initialize the animation frame
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/morphing_example')
canvas.set_background()

# Draw the objects
text_from = TexObject('Who is the best?', font_size=70)
text_from.center_to_pos()
text_to = TexObject('You are the best!', font_size=70, fill='blue')
text_to.center_to_pos()

text_from.fadein(start=0, end=1)
obj = MorphObject(text_from, text_to, start=1, end=3)

# Add the objects to the canvas
canvas.add_objects(text_from, obj, text_to)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/morphing_example.mp4', fps=30, end_time=4)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
