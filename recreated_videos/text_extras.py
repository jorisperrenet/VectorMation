"""Text Extra Methods Demo — untype, bold, italic, typing, set_font_family,
set_font_size, update_text, reverse_text, split_chars, split_into_words."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from vectormation.objects import *

args = parse_args()
v = VectorMathAnim(verbose=args.verbose, save_dir='svgs/text_extras')
v.set_background()
T = 24.0

WHITE = '#FFFFFF'
BLUE  = '#58C4DD'
RED   = '#FC6255'
GREEN = '#83C167'
GREY  = '#888888'

# =============================================================================
# Phase 1 (0-6s): untype + typing
# =============================================================================
title1 = Text(text='Typewriter Variants', x=960, y=60, font_size=48,
              fill=WHITE, stroke_width=0, text_anchor='middle')
title1.write(0, 0.5)
title1.fadeout(5.0, 5.5)
v.add(title1)

# --- typewrite then untype ---
lbl1 = Text(text='typewrite() + untype()', x=960, y=180, font_size=22,
            fill=GREY, stroke_width=0, text_anchor='middle', creation=0.3)
lbl1.fadeout(5.0, 5.5)
v.add(lbl1)

tw = Text(text='Hello, World! This is typewrite.', x=400, y=280,
          font_size=36, fill=BLUE, stroke_width=0, creation=0)
tw.typewrite(start=0.5, end=2.5)
tw.untype(start=3.5, end=5.0)
v.add(tw)

# --- typing (animated input) ---
lbl2 = Text(text='typing()', x=960, y=420, font_size=22,
            fill=GREY, stroke_width=0, text_anchor='middle', creation=0.3)
lbl2.fadeout(5.0, 5.5)
v.add(lbl2)

ty = Text(text='Typed character by character!', x=400, y=520, font_size=36, fill=GREEN, stroke_width=0, creation=0)
ty.typing(start=1.0, end=4.0)
ty.fadeout(5.0, 5.5)
v.add(ty)

# =============================================================================
# Phase 2 (6-12s): Styling Methods
# =============================================================================
title2 = Text(text='Text Styling', x=960, y=60, font_size=48,
              fill=WHITE, stroke_width=0, text_anchor='middle')
title2.write(6, 6.5)
title2.fadeout(11.0, 11.5)
v.add(title2)

# --- bold ---
lbl3 = Text(text='bold()', x=350, y=180, font_size=22,
            fill=GREY, stroke_width=0, text_anchor='middle', creation=6.3)
lbl3.fadeout(11.0, 11.5)
v.add(lbl3)

bold_text = Text(text='Bold Text', x=350, y=280, font_size=40,
                 fill=WHITE, stroke_width=0, text_anchor='middle', creation=6.5)
bold_text.bold()
bold_text.fadein(6.5, 7.0)
bold_text.fadeout(11.0, 11.5)
v.add(bold_text)

# --- italic ---
lbl4 = Text(text='italic()', x=960, y=180, font_size=22,
            fill=GREY, stroke_width=0, text_anchor='middle', creation=6.3)
lbl4.fadeout(11.0, 11.5)
v.add(lbl4)

italic_text = Text(text='Italic Text', x=960, y=280, font_size=40,
                   fill=WHITE, stroke_width=0, text_anchor='middle', creation=6.5)
italic_text.italic()
italic_text.fadein(6.5, 7.0)
italic_text.fadeout(11.0, 11.5)
v.add(italic_text)

# --- set_font_family ---
lbl5 = Text(text='set_font_family()', x=1570, y=180, font_size=22,
            fill=GREY, stroke_width=0, text_anchor='middle', creation=6.3)
lbl5.fadeout(11.0, 11.5)
v.add(lbl5)

ff_text = Text(text='Courier New', x=1570, y=280, font_size=36,
               fill=WHITE, stroke_width=0, text_anchor='middle', creation=6.5)
ff_text.set_font_family('Courier New')
ff_text.fadein(6.5, 7.0)
ff_text.fadeout(11.0, 11.5)
v.add(ff_text)

# --- set_font_size (animated) ---
lbl6 = Text(text='set_font_size()', x=350, y=420, font_size=22,
            fill=GREY, stroke_width=0, text_anchor='middle', creation=6.3)
lbl6.fadeout(11.0, 11.5)
v.add(lbl6)

fs_text = Text(text='Growing', x=350, y=560, font_size=20,
               fill=BLUE, stroke_width=0, text_anchor='middle', creation=6.5)
fs_text.fadein(6.5, 7.0)
fs_text.set_font_size(60, start=7.5, end=9.5)
fs_text.fadeout(11.0, 11.5)
v.add(fs_text)

# --- update_text ---
lbl7 = Text(text='update_text()', x=960, y=420, font_size=22,
            fill=GREY, stroke_width=0, text_anchor='middle', creation=6.3)
lbl7.fadeout(11.0, 11.5)
v.add(lbl7)

ut_text = Text(text='Original', x=960, y=560, font_size=36,
               fill=RED, stroke_width=0, text_anchor='middle', creation=6.5)
ut_text.fadein(6.5, 7.0)
ut_text.update_text('Changed!', start=8.0)
ut_text.update_text('Again!', start=9.0)
ut_text.update_text('Done.', start=10.0)
ut_text.fadeout(11.0, 11.5)
v.add(ut_text)

# --- reverse_text ---
lbl8 = Text(text='reverse_text()', x=1570, y=420, font_size=22,
            fill=GREY, stroke_width=0, text_anchor='middle', creation=6.3)
lbl8.fadeout(11.0, 11.5)
v.add(lbl8)

rv_text = Text(text='REVERSED', x=1570, y=560, font_size=36,
               fill=GREEN, stroke_width=0, text_anchor='middle', creation=6.5)
rv_text.fadein(6.5, 7.0)
rv_text.reverse_text(time=8.5)
rv_text.fadeout(11.0, 11.5)
v.add(rv_text)

# =============================================================================
# Phase 3 (12-18s): Splitting Methods
# =============================================================================
title3 = Text(text='Text Splitting', x=960, y=60, font_size=48,
              fill=WHITE, stroke_width=0, text_anchor='middle')
title3.write(12, 12.5)
title3.fadeout(17.0, 17.5)
v.add(title3)

# --- split_chars ---
lbl9 = Text(text='split_chars() + stagger', x=960, y=180, font_size=22,
            fill=GREY, stroke_width=0, text_anchor='middle', creation=12.3)
lbl9.fadeout(17.0, 17.5)
v.add(lbl9)

src_chars = Text(text='HELLO', x=960, y=300, font_size=60,
                 fill=BLUE, stroke_width=0, text_anchor='middle', creation=12)
chars = src_chars.split_chars(time=12)
chars.center_to_pos(960, 300, start=12)
chars.set_color_by_gradient('#58C4DD', '#FF6B6B')
chars.stagger('fadein', delay=0.15, start=12.5, end=14)
chars.stagger('wiggle', delay=0.15, start=14.5, end=16)
chars.fadeout(17.0, 17.5)
v.add(chars)

# --- split_into_words ---
lbl10 = Text(text='split_into_words() + wave_anim', x=960, y=500, font_size=22,
             fill=GREY, stroke_width=0, text_anchor='middle', creation=12.3)
lbl10.fadeout(17.0, 17.5)
v.add(lbl10)

src_words = Text(text='Hello beautiful world', x=960, y=620, font_size=48,
                 fill=GREEN, stroke_width=0, text_anchor='middle', creation=12)
words = src_words.split_into_words(time=12)
words.arrange(direction=(1, 0), buff=20)
words.center_to_pos(960, 620, start=12)
words.stagger('fadein', delay=0.3, start=12.5, end=14)
words.wave_anim(start=14.5, end=16.5, amplitude=30, n_waves=2)
words.fadeout(17.0, 17.5)
v.add(words)

# =============================================================================
# Phase 4 (18-24s): Combined Animations
# =============================================================================
title4 = Text(text='Combined Text Effects', x=960, y=60, font_size=48,
              fill=WHITE, stroke_width=0, text_anchor='middle')
title4.write(18, 18.5)
title4.fadeout(23.0, 23.5)
v.add(title4)

# Typewrite, highlight, then untype
combo = Text(text='Typewrite then highlight!', x=960, y=300,
             font_size=44, fill=WHITE, stroke_width=0,
             text_anchor='middle', creation=18)
combo.typewrite(start=18.5, end=20.0)
combo.highlight(start=20.5, end=21.5, color='#FFFF00')
combo.untype(start=22.0, end=23.0)
v.add(combo)

# Bold + italic combined
combo2 = Text(text='Bold & Italic', x=960, y=500,
              font_size=52, fill=BLUE, stroke_width=0,
              text_anchor='middle', creation=18)
combo2.bold()
combo2.italic()
combo2.fadein(18.5, 19.0)
combo2.pulsate(start=19.5, end=21.5, scale_factor=1.3, n_pulses=3)
combo2.fadeout(23.0, 23.5)
v.add(combo2)

# Scramble with custom charset
lbl_scr = Text(text='scramble(charset="01")', x=960, y=680, font_size=22,
               fill=GREY, stroke_width=0, text_anchor='middle', creation=18.3)
lbl_scr.fadeout(23.0, 23.5)
v.add(lbl_scr)

scr = Text(text='DECODED', x=960, y=780, font_size=48,
           fill=GREEN, stroke_width=0, text_anchor='middle', creation=18)
scr.scramble(start=18.5, end=21.0, charset='01')
scr.fadeout(23.0, 23.5)
v.add(scr)

# =============================================================================
# Display
# =============================================================================
if not args.no_display:
    v.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
    )
