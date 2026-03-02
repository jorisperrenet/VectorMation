import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/typewrite')
canvas.set_background()

# Typewriter effect
msg = Text(text='Hello, World! Welcome to VectorMation.',
           x=200, y=300, font_size=40, fill='#fff', stroke_width=0)
msg.typewrite(0, 3, cursor='_')

# Count animation with count_to
counter = CountAnimation(start_val=0, end_val=100, start=0, end=2,
                         x=960, y=500, font_size=64, fill='#58C4DD',
                         stroke_width=0, text_anchor='middle')
counter.count_to(250, 2.5, 4)
counter.count_to(42, 4.5, 5.5)

title = Text(text='Typewriter & Count Animations', x=960, y=100,
             font_size=48, fill='#83C167', stroke_width=0, text_anchor='middle')
title.write(0, 1)

canvas.add_objects(msg, counter, title)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/typewrite_example.mp4', fps=30, end=6)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
