"""Text Effects — showcase of text animation methods.

Demonstrates typewrite, scramble, reveal_by_word, highlight,
set_text, and styling transitions.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/text_effects_demo')
canvas.set_background()

# ── Title ────────────────────────────────────────────────────────────────
title = Text(text='Text Animation Effects', x=960, y=55,
             font_size=44, fill='#fff', stroke_width=0,
             text_anchor='middle', creation=0)
title.fadein(0, 0.5)
canvas.add(title)

# ── 1. Typewrite ─────────────────────────────────────────────────────────
t = 0.5
label1 = Text(text='typewrite()', x=150, y=140, font_size=20,
              fill='#888', stroke_width=0, creation=t)
label1.fadein(t, t + 0.3)
canvas.add(label1)

txt1 = Text(text='Hello, World! This text types in character by character.',
            x=150, y=180, font_size=28, fill='#58C4DD', stroke_width=0,
            creation=t)
txt1.typewrite(start=t + 0.2, end=t + 2.0)
canvas.add(txt1)

# ── 2. Scramble ──────────────────────────────────────────────────────────
t = 2.8
label2 = Text(text='scramble()', x=150, y=280, font_size=20,
              fill='#888', stroke_width=0, creation=t)
label2.fadein(t, t + 0.3)
canvas.add(label2)

txt2 = Text(text='Decoding secret message...', x=150, y=320,
            font_size=28, fill='#83C167', stroke_width=0, creation=t)
txt2.scramble(start=t + 0.2, end=t + 1.8)
canvas.add(txt2)

# ── 3. Word by word ─────────────────────────────────────────────────────
t = 5.0
label3 = Text(text='reveal_by_word()', x=150, y=420, font_size=20,
              fill='#888', stroke_width=0, creation=t)
label3.fadein(t, t + 0.3)
canvas.add(label3)

txt3 = Text(text='Each word appears one at a time', x=150, y=460,
            font_size=28, fill='#FFB86C', stroke_width=0, creation=t)
txt3.reveal_by_word(start=t + 0.2, end=t + 2.0)
canvas.add(txt3)

# ── 4. Highlight ─────────────────────────────────────────────────────────
t = 7.5
label4 = Text(text='highlight()', x=150, y=560, font_size=20,
              fill='#888', stroke_width=0, creation=t)
label4.fadein(t, t + 0.3)
canvas.add(label4)

txt4 = Text(text='This text gets highlighted!', x=150, y=600,
            font_size=28, fill='#fff', stroke_width=0, creation=0)
txt4.fadein(0, 0.5)
txt4.highlight(start=t + 0.2, end=t + 1.5, color='#FFFF00')
canvas.add(txt4)

# ── 5. set_text ──────────────────────────────────────────────────────────
t = 9.5
label5 = Text(text='set_text()', x=150, y=700, font_size=20,
              fill='#888', stroke_width=0, creation=t)
label5.fadein(t, t + 0.3)
canvas.add(label5)

txt5 = Text(text='Watch this text change!', x=150, y=740,
            font_size=28, fill='#BD93F9', stroke_width=0, creation=0)
txt5.fadein(0, 0.5)
txt5.set_text(t + 0.3, t + 1.0, 'It morphed into something new!')
canvas.add(txt5)

# ── 6. Color cycling ────────────────────────────────────────────────────
t = 11.5
label6 = Text(text='color_cycle()', x=150, y=840, font_size=20,
              fill='#888', stroke_width=0, creation=t)
label6.fadein(t, t + 0.3)
canvas.add(label6)

txt6 = Text(text='Colors cycle through the rainbow', x=150, y=880,
            font_size=28, fill='#FF6B6B', stroke_width=0, creation=0)
txt6.fadein(0, 0.5)
txt6.color_cycle(['#FF6B6B', '#FFB86C', '#FFFF00', '#83C167', '#58C4DD', '#BD93F9'],
                 start=t + 0.2, end=t + 2.5)
canvas.add(txt6)

# ── 7. Count animation ──────────────────────────────────────────────────
t = 0.5
label7 = Text(text='CountAnimation()', x=1200, y=140, font_size=20,
              fill='#888', stroke_width=0, creation=t)
label7.fadein(t, t + 0.3)
canvas.add(label7)

counter = CountAnimation(0, 1000, start=t + 0.3, end=t + 3.0,
                         x=1400, y=220, font_size=48,
                         fill='#FF6B6B', stroke_width=0, creation=t)
counter.fadein(t, t + 0.3)
canvas.add(counter)

canvas.browser_display(start=args.start or 0, end=args.end or 14,
                           fps=args.fps, port=args.port)
