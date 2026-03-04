"""SpeechBubble with tail."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

bubble = SpeechBubble(text='Hello there!', x=860, y=480, font_size=24,
                      tail_direction='down', box_fill='#1e1e2e', text_color='#fff')

v.add(bubble)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_speech_bubble.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
