import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/array_viz')
canvas.set_background()

# Create an array with values
arr = ArrayViz([3, 1, 4, 1, 5, 9, 2, 6], cell_size=90)
arr.fadein(0, 1)

title = Text(text='Bubble Sort Visualization', x=960, y=80,
             font_size=48, fill='#fff', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Bubble sort steps — highlight, compare, swap
arr.highlight(0, start=1, end=1.5, color='#FC6255')
arr.highlight(1, start=1, end=1.5, color='#FC6255')
arr.swap(0, 1, start=1.5, end=2.5)

arr.highlight(1, start=3, end=3.5, color='#FC6255')
arr.highlight(2, start=3, end=3.5, color='#FC6255')

arr.highlight(2, start=4, end=4.5, color='#FC6255')
arr.highlight(3, start=4, end=4.5, color='#FC6255')
arr.swap(2, 3, start=4.5, end=5.5)

canvas.add_objects(arr, title)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/array_viz_example.mp4', fps=30, end=6)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
