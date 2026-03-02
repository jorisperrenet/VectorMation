import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/speech_badge_divider')
canvas.set_background()

title = Text(text='SpeechBubble, Badge, NumberedList & Divider', x=960, y=40,
             font_size=28, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# --- SpeechBubble examples ---
sb1 = SpeechBubble('Hello world!', x=50, y=120, font_size=18, tail_direction='down')
sb1.fadein(1, 2)

sb2 = SpeechBubble('Important!', x=50, y=220, font_size=20,
                    box_fill='#6b2a2a', tail_direction='right', tail_height=25)
sb2.fadein(1.3, 2.3)

sb3 = SpeechBubble('Tip', x=300, y=120, font_size=16,
                    box_fill='#2a6b3a', tail_direction='up')
sb3.fadein(1.6, 2.6)

# --- Badge examples ---
b1 = Badge('v2.1.0', x=550, y=120, bg_color='#58C4DD')
b1.fadein(1, 2)

b2 = Badge('Passed', x=550, y=160, bg_color='#83C167')
b2.fadein(1.2, 2.2)

b3 = Badge('Critical', x=550, y=200, bg_color='#FF6B6B', text_color='#fff')
b3.fadein(1.4, 2.4)

b4 = Badge('Beta', x=550, y=240, bg_color='#FFFF00', text_color='#000')
b4.fadein(1.6, 2.6)

# --- NumberedList ---
nl = NumberedList('Set up environment', 'Install dependencies',
                  'Run tests', 'Deploy to production',
                  x=50, y=420, font_size=22)
nl.fadein(1, 2)

# --- Divider examples ---
d1 = Divider(x=50, y=370, length=400)
d1.fadein(0.8, 1.5)

d2 = Divider(x=550, y=320, length=350, label='OR', stroke='#888')
d2.fadein(1, 2)

d3 = Divider(x=550, y=400, length=350, label='Section 2', font_size=14, stroke='#58C4DD')
d3.fadein(1.5, 2.5)

canvas.add_objects(title, sb1, sb2, sb3,
                   b1, b2, b3, b4,
                   nl, d1, d2, d3)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/speech_badge_divider_example.mp4', fps=30, end=3)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
