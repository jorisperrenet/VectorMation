import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/text_highlight')
canvas.set_background()

# Create some text lines
line1 = Text(text='The quick brown fox', x=960, y=300,
             font_size=48, fill='#fff', stroke_width=0, text_anchor='middle')
line2 = Text(text='jumps over the lazy dog', x=960, y=380,
             font_size=48, fill='#fff', stroke_width=0, text_anchor='middle')

line1.write(0, 1)
line2.write(0.5, 1.5)

# Highlight the first line with yellow
hl1 = line1.highlight(start=2, end=4, color='#FFFF00', opacity=0.3)

# Highlight the second line with green
hl2 = line2.highlight(start=3, end=5, color='#83C167', opacity=0.4)

title = Text(text='Text Highlighting', x=960, y=100,
             font_size=56, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

canvas.add_objects(hl1, hl2, line1, line2, title)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/text_highlight_example.mp4', fps=30, end=5)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
