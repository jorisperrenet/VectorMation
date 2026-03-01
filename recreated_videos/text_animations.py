"""Text Animations Demo — write, typewrite, reveal_by_word, highlight_substring,
set_text, scramble, Code, Paragraph, Variable, DecimalNumber, CountAnimation."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/text_animations')
canvas.set_background()

T = 12.0

# =============================================================================
# Phase 1 (0-3s): Basic Text Animations
# =============================================================================

# --- write() animation ---
phase1_label = Text(
    text='Phase 1: Basic Text', x=960, y=80, font_size=28,
    fill='#888888', stroke_width=0, text_anchor='middle',
)
phase1_label.fadein(0.0, 0.3)
phase1_label.fadeout(2.5, 3.0)
canvas.add(phase1_label)

write_label = Text(
    text='write()', x=300, y=230, font_size=22,
    fill='#666666', stroke_width=0, text_anchor='middle',
)
write_label.fadein(0.0, 0.3)
write_label.fadeout(2.5, 3.0)
canvas.add(write_label)

write_text = Text(
    text='Animated Write', x=300, y=300, font_size=44,
    fill='#58C4DD', stroke_width=0, text_anchor='middle',
)
write_text.write(0.2, 1.2)
write_text.fadeout(2.5, 3.0)
canvas.add(write_text)

# --- typewrite() animation ---
tw_label = Text(
    text='typewrite()', x=960, y=230, font_size=22,
    fill='#666666', stroke_width=0, text_anchor='middle',
)
tw_label.fadein(0.0, 0.3)
tw_label.fadeout(2.5, 3.0)
canvas.add(tw_label)

tw_text = Text(
    text='Character by character...', x=960, y=300, font_size=44,
    fill='#FC6255', stroke_width=0, text_anchor='middle',
)
tw_text.typewrite(start=0.3, end=1.8)
tw_text.fadeout(2.5, 3.0)
canvas.add(tw_text)

# --- reveal_by_word() animation ---
rbw_label = Text(
    text='reveal_by_word()', x=960, y=500, font_size=22,
    fill='#666666', stroke_width=0, text_anchor='middle',
)
rbw_label.fadein(0.5, 0.8)
rbw_label.fadeout(2.5, 3.0)
canvas.add(rbw_label)

rbw_text = Text(
    text='Each word appears one by one like subtitles', x=960, y=570, font_size=42,
    fill='#83C167', stroke_width=0, text_anchor='middle',
)
rbw_text.reveal_by_word(start=0.8, end=2.3)
rbw_text.fadeout(2.5, 3.0)
canvas.add(rbw_text)

# =============================================================================
# Phase 2 (3-6s): Text Effects
# =============================================================================

phase2_label = Text(
    text='Phase 2: Text Effects', x=960, y=80, font_size=28,
    fill='#888888', stroke_width=0, text_anchor='middle',
)
phase2_label.fadein(3.0, 3.3)
phase2_label.fadeout(5.5, 6.0)
canvas.add(phase2_label)

# --- highlight_substring() ---
hl_label = Text(
    text='highlight_substring()', x=960, y=200, font_size=22,
    fill='#666666', stroke_width=0, text_anchor='middle', creation=3.0,
)
hl_label.fadein(3.0, 3.3)
hl_label.fadeout(5.5, 6.0)
canvas.add(hl_label)

hl_text = Text(
    text='Highlight any important keyword in text', x=960, y=270, font_size=42,
    fill='#FFFFFF', stroke_width=0, text_anchor='middle', creation=3.0,
)
hl_text.fadein(3.1, 3.4)
hl_text.fadeout(5.5, 6.0)
canvas.add(hl_text)

hl_rect1 = hl_text.highlight_substring(
    'important', color='#FFFF00', start=3.5, end=4.5, opacity=0.35,
)
canvas.add(hl_rect1)

hl_rect2 = hl_text.highlight_substring(
    'keyword', color='#E84D60', start=3.8, end=4.8, opacity=0.35,
)
canvas.add(hl_rect2)

# --- set_text() ---
st_label = Text(
    text='set_text()', x=480, y=420, font_size=22,
    fill='#666666', stroke_width=0, text_anchor='middle', creation=3.0,
)
st_label.fadein(3.0, 3.3)
st_label.fadeout(5.5, 6.0)
canvas.add(st_label)

st_text = Text(
    text='Original text here', x=480, y=490, font_size=38,
    fill='#58C4DD', stroke_width=0, text_anchor='middle', creation=3.0,
)
st_text.fadein(3.1, 3.4)
st_text.set_text(3.8, 4.6, 'Text has changed!')
st_text.set_text(4.8, 5.4, 'And again!')
st_text.fadeout(5.5, 6.0)
canvas.add(st_text)

# --- scramble() ---
sc_label = Text(
    text='scramble()', x=1440, y=420, font_size=22,
    fill='#666666', stroke_width=0, text_anchor='middle', creation=3.0,
)
sc_label.fadein(3.0, 3.3)
sc_label.fadeout(5.5, 6.0)
canvas.add(sc_label)

sc_text = Text(
    text='DECODING MESSAGE', x=1440, y=490, font_size=38,
    fill='#F5A623', stroke_width=0, text_anchor='middle',
)
sc_text.scramble(start=3.5, end=5.2)
sc_text.fadeout(5.5, 6.0)
canvas.add(sc_text)

# =============================================================================
# Phase 3 (6-9s): Code, Paragraph, Variable
# =============================================================================

phase3_label = Text(
    text='Phase 3: Code, Paragraph, Variable', x=960, y=80, font_size=28,
    fill='#888888', stroke_width=0, text_anchor='middle',
)
phase3_label.fadein(6.0, 6.3)
phase3_label.fadeout(8.5, 9.0)
canvas.add(phase3_label)

# --- Code object ---
code_snippet = Code(
    text="""def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))""",
    language='python', x=120, y=180, font_size=20,
    line_height=1.4, creation=6.0,
)
code_snippet.fadein(6.1, 6.5)
code_snippet.fadeout(8.5, 9.0)
canvas.add(code_snippet)

# --- Paragraph object ---
para = Paragraph(
    'VectorMation is a Python library',
    'for creating animated SVG videos.',
    'It supports text, shapes, charts,',
    'and even 3D surfaces.',
    x=1050, y=220, font_size=30, alignment='left',
    creation=6.0, fill='#CCCCCC', stroke_width=0,
)
para.fadein(6.3, 6.7)
para.fadeout(8.5, 9.0)
canvas.add(para)

# --- Variable object ---
var_label_text = Text(
    text='Variable tracker:', x=960, y=600, font_size=22,
    fill='#666666', stroke_width=0, text_anchor='middle', creation=6.0,
)
var_label_text.fadein(6.5, 6.8)
var_label_text.fadeout(8.5, 9.0)
canvas.add(var_label_text)

var = Variable(
    label='x', value=0, fmt='{:.1f}', x=960, y=680,
    font_size=52, creation=6.0, fill='#58C4DD', stroke_width=0,
)
var.fadein(6.5, 6.8)
var.animate_value(3.14, start=7.0, end=8.0)
var.fadeout(8.5, 9.0)
canvas.add(var)

# =============================================================================
# Phase 4 (9-12s): DecimalNumber and CountAnimation
# =============================================================================

phase4_label = Text(
    text='Phase 4: DecimalNumber & CountAnimation', x=960, y=80, font_size=28,
    fill='#888888', stroke_width=0, text_anchor='middle',
)
phase4_label.fadein(9.0, 9.3)
phase4_label.fadeout(11.5, 12.0)
canvas.add(phase4_label)

# --- DecimalNumber ---
dn_label = Text(
    text='DecimalNumber', x=480, y=250, font_size=22,
    fill='#666666', stroke_width=0, text_anchor='middle', creation=9.0,
)
dn_label.fadein(9.0, 9.3)
dn_label.fadeout(11.5, 12.0)
canvas.add(dn_label)

decimal_num = DecimalNumber(
    value=0.0, fmt='{:.2f}', x=480, y=350, font_size=64,
    text_anchor='middle', creation=9.0, fill='#83C167', stroke_width=0,
)
decimal_num.fadein(9.1, 9.4)
decimal_num.animate_value(99.99, start=9.5, end=11.0)
decimal_num.fadeout(11.5, 12.0)
canvas.add(decimal_num)

dn_unit = Text(
    text='smoothly counting up', x=480, y=420, font_size=20,
    fill='#666666', stroke_width=0, text_anchor='middle', creation=9.0,
)
dn_unit.fadein(9.1, 9.4)
dn_unit.fadeout(11.5, 12.0)
canvas.add(dn_unit)

# --- CountAnimation ---
ca_label = Text(
    text='CountAnimation', x=1440, y=250, font_size=22,
    fill='#666666', stroke_width=0, text_anchor='middle', creation=9.0,
)
ca_label.fadein(9.0, 9.3)
ca_label.fadeout(11.5, 12.0)
canvas.add(ca_label)

counter = CountAnimation(
    start_val=0, end_val=10000, start=9.5, end=11.0,
    fmt='{:,.0f}', x=1440, y=350, font_size=64,
    text_anchor='middle', creation=9.0, fill='#FC6255', stroke_width=0,
)
counter.fadein(9.1, 9.4)
counter.fadeout(11.5, 12.0)
canvas.add(counter)

ca_desc = Text(
    text='integer counting animation', x=1440, y=420, font_size=20,
    fill='#666666', stroke_width=0, text_anchor='middle', creation=9.0,
)
ca_desc.fadein(9.1, 9.4)
ca_desc.fadeout(11.5, 12.0)
canvas.add(ca_desc)

# Center bottom: a second counter that counts to a different target
counter2_label = Text(
    text='count_to() chained:', x=960, y=600, font_size=22,
    fill='#666666', stroke_width=0, text_anchor='middle', creation=9.0,
)
counter2_label.fadein(9.3, 9.6)
counter2_label.fadeout(11.5, 12.0)
canvas.add(counter2_label)

counter2 = CountAnimation(
    start_val=0, end_val=50, start=9.5, end=10.2,
    fmt='{:.0f}%', x=960, y=700, font_size=56,
    text_anchor='middle', creation=9.0, fill='#9A72AC', stroke_width=0,
)
counter2.count_to(100, start=10.2, end=11.0)
counter2.fadein(9.3, 9.6)
counter2.fadeout(11.5, 12.0)
canvas.add(counter2)

# =============================================================================
# Display
# =============================================================================
if not args.no_display:
    canvas.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
    )
