"""VCollection.reveal: staggered reveal of children sliding into view."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

items = VCollection(*[
    Text(word, font_size=48, fill='#fff')
    for word in ['Hello', 'World', 'From', 'VectorMation']
])
items.arrange(direction='right', buff=30)
items.center_to_pos()
items.reveal(start=0, end=2, direction='left')

v.add(items)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_reveal.mp4', fps=30, end=2.5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2.5)
