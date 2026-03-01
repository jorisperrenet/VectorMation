"""Text Animation Features — typewrite, scramble, reveal_by_word, CountAnimation,
BulletedList, and highlight_substring."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/text_animations')
canvas.set_background()

# -- Colors -------------------------------------------------------------------
ACCENT = '#58C4DD'
HIGHLIGHT = '#FFFF00'
GREEN = '#2ECC71'
ORANGE = '#F5A623'
PINK = '#E84D60'

# =============================================================================
# Phase 1: Typewrite effect (0 – 2s)
# =============================================================================
section_label_1 = Text(
    text='typewrite()', x=960, y=100, font_size=28,
    fill='#888', stroke_width=0, text_anchor='middle',
)
section_label_1.fadein(0.0, 0.3)
section_label_1.fadeout(1.7, 2.0)
canvas.add(section_label_1)

typewrite_text = Text(
    text='Hello, World! Welcome to VectorMation.', x=960, y=480,
    font_size=52, fill=ACCENT, stroke_width=0, text_anchor='middle',
)
typewrite_text.typewrite(start=0.2, end=1.6)
typewrite_text.fadeout(1.8, 2.1)
canvas.add(typewrite_text)

# =============================================================================
# Phase 2: Scramble effect (2 – 4s)
# =============================================================================
section_label_2 = Text(
    text='scramble()', x=960, y=100, font_size=28,
    fill='#888', stroke_width=0, text_anchor='middle',
)
section_label_2.fadein(2.0, 2.3)
section_label_2.fadeout(3.7, 4.0)
canvas.add(section_label_2)

scramble_text = Text(
    text='DECRYPTING SECRET MESSAGE', x=960, y=480,
    font_size=52, fill=GREEN, stroke_width=0, text_anchor='middle',
)
scramble_text.scramble(start=2.2, end=3.6)
scramble_text.fadeout(3.8, 4.1)
canvas.add(scramble_text)

# =============================================================================
# Phase 3: Reveal by word (4 – 6s)
# =============================================================================
section_label_3 = Text(
    text='reveal_by_word()', x=960, y=100, font_size=28,
    fill='#888', stroke_width=0, text_anchor='middle',
)
section_label_3.fadein(4.0, 4.3)
section_label_3.fadeout(5.7, 6.0)
canvas.add(section_label_3)

word_text = Text(
    text='Each word appears one at a time like subtitles', x=960, y=480,
    font_size=46, fill=ORANGE, stroke_width=0, text_anchor='middle',
)
word_text.reveal_by_word(start=4.2, end=5.6)
word_text.fadeout(5.8, 6.1)
canvas.add(word_text)

# =============================================================================
# Phase 4: CountAnimation (6 – 8s)
# =============================================================================
section_label_4 = Text(
    text='CountAnimation', x=960, y=100, font_size=28,
    fill='#888', stroke_width=0, text_anchor='middle',
)
section_label_4.fadein(6.0, 6.3)
section_label_4.fadeout(7.7, 8.0)
canvas.add(section_label_4)

count_label = Text(
    text='Downloads:', x=760, y=460, font_size=42,
    fill='#ccc', stroke_width=0, text_anchor='end',
)
count_label.fadein(6.1, 6.4)
count_label.fadeout(7.8, 8.1)
canvas.add(count_label)

counter = CountAnimation(
    start_val=0, end_val=10000, start=6.3, end=7.5,
    fmt='{:,.0f}', x=790, y=460, font_size=60,
    fill=ACCENT, stroke_width=0, creation=6.1,
)
counter.fadein(6.1, 6.3)
counter.fadeout(7.8, 8.1)
canvas.add(counter)

# =============================================================================
# Phase 5: BulletedList (8 – 10s)
# =============================================================================
section_label_5 = Text(
    text='BulletedList', x=960, y=100, font_size=28,
    fill='#888', stroke_width=0, text_anchor='middle',
)
section_label_5.fadein(8.0, 8.3)
section_label_5.fadeout(9.7, 10.0)
canvas.add(section_label_5)

bullets = BulletedList(
    'Shapes & Paths',
    'Animations & Easings',
    'Mathematical Graphs',
    '3D Surfaces & Camera',
    'SVG Export & Browser Preview',
    x=520, y=300, font_size=38, creation=8.0,
    fill='#fff', stroke_width=0,
)
bullets.fadein(8.1, 8.5)
bullets.fadeout(9.8, 10.1)
canvas.add(bullets)

# =============================================================================
# Phase 6: highlight_substring (10 – 12s)
# =============================================================================
section_label_6 = Text(
    text='highlight_substring()', x=960, y=100, font_size=28,
    fill='#888', stroke_width=0, text_anchor='middle',
)
section_label_6.fadein(10.0, 10.3)
section_label_6.fadeout(11.7, 12.0)
canvas.add(section_label_6)

hl_text = Text(
    text='Highlight any keyword in a sentence easily', x=960, y=440,
    font_size=44, fill='#fff', stroke_width=0, text_anchor='middle',
    creation=10.0,
)
hl_text.fadein(10.1, 10.4)
hl_text.fadeout(11.8, 12.0)
canvas.add(hl_text)

# Highlight "keyword" in yellow
hl_rect1 = hl_text.highlight_substring(
    'keyword', color=HIGHLIGHT, start=10.5, end=11.2, opacity=0.35,
)
canvas.add(hl_rect1)

# Highlight "easily" in pink
hl_rect2 = hl_text.highlight_substring(
    'easily', color=PINK, start=10.8, end=11.5, opacity=0.35,
)
canvas.add(hl_rect2)

# -- Render -------------------------------------------------------------------
if not args.no_display:
    canvas.browser_display(
        start=args.start or 0, end=args.end or 12,
        fps=args.fps, port=args.port,
    )
