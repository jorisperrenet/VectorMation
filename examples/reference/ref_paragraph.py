"""Paragraph example."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

p = Paragraph(
    'First line of text.',
    'Second line continues here.',
    'Third and final line.',
    alignment='center', font_size=44, fill='#fff', stroke_width=0,
)
p.center_to_pos()
v.add(p)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_paragraph.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
