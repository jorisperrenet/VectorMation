"""Typewriter effect with cursor."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

title = Text('$ pip install vectormation', x=200, y=400,
             font_size=40, font_family='monospace', fill='#0f0')
title.typewrite(start=0, end=2, cursor='_')

subtitle = Text('Installation complete.', x=200, y=480,
                font_size=32, font_family='monospace', fill='#0f0')
subtitle.typewrite(start=2.5, end=3.5, cursor='_')

v.add(title, subtitle)
if args.for_docs:
    v.export_video('docs/source/_static/videos/typewrite.mp4', fps=30, end=4)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=4)
