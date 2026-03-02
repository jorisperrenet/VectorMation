import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/animations_counters')
canvas.set_background()

title = Text(text='Counter Animations', x=960, y=80,
             font_size=52, fill='#83C167', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Column x-positions (4 columns centered on 1920px canvas)
cx1, cx2, cx3, cx4 = 384, 768, 1152, 1536

# =====================================================================
# 1. CountAnimation — text-based counting with chained count_to()
# =====================================================================
label1 = Text(text='CountAnimation', x=cx1, y=180,
              font_size=32, fill='#888', stroke_width=0, text_anchor='middle')
label1.fadein(0.5, 1)

counter1 = CountAnimation(start_val=0, end_val=100, start=1, end=3,
                          x=cx1, y=260, font_size=64, fill='#58C4DD',
                          stroke_width=0, text_anchor='middle')
counter1.count_to(500, 3.5, 5)
counter1.count_to(42, 5.5, 7)

tex_counter1 = TexCountAnimation(start_val=0, end_val=100, start=1, end=3,
                                 x=cx1, y=370, font_size=64, fill='#58C4DD',
                                 text_anchor='middle')
tex_counter1.count_to(500, 3.5, 5)
tex_counter1.count_to(42, 5.5, 7)

# =====================================================================
# 2. DecimalNumber — dynamic numeric display (updates each frame)
# =====================================================================
label2 = Text(text='DecimalNumber', x=cx2, y=180,
              font_size=32, fill='#888', stroke_width=0, text_anchor='middle')
label2.fadein(0.5, 1)

dec = DecimalNumber(3.14, fmt='{:.2f}', x=cx2, y=260,
                    font_size=64, fill='#FFFF00', stroke_width=0,
                    text_anchor='middle')
dec.fadein(1, 1.5)
dec.animate_value(99.99, start=2, end=4)
dec.animate_value(2.72, start=5, end=7)

tex_dec = TexCountAnimation(start_val=3.14, end_val=99.99, start=2, end=4,
                            fmt='{:.2f}', x=cx2, y=370, font_size=64,
                            fill='#FFFF00', text_anchor='middle')
tex_dec.count_to(2.72, 5, 7)

# =====================================================================
# 3. Integer — whole-number variant of DecimalNumber
# =====================================================================
label3 = Text(text='Integer', x=cx3, y=180,
              font_size=32, fill='#888', stroke_width=0, text_anchor='middle')
label3.fadein(0.5, 1)

intnum = Integer(0, x=cx3, y=260, font_size=64,
                 fill='#A0E8AF', stroke_width=0, text_anchor='middle')
intnum.fadein(1, 1.5)
intnum.animate_value(1000, start=2, end=5)
intnum.animate_value(7, start=5.5, end=7)

tex_int = TexCountAnimation(start_val=0, end_val=1000, start=2, end=5,
                            x=cx3, y=370, font_size=64, fill='#A0E8AF',
                            text_anchor='middle')
tex_int.count_to(7, 5.5, 7)

# =====================================================================
# 4. ValueTracker — drives DecimalNumber and Integer from one source
# =====================================================================
label4 = Text(text='ValueTracker', x=cx4, y=180,
              font_size=32, fill='#888', stroke_width=0, text_anchor='middle')
label4.fadein(0.5, 1)

tracker = ValueTracker(0)
tracker.animate_value(360, start=1, end=4)
tracker.animate_value(180, start=5, end=7)

# Same tracker drives the display
vt_dec = DecimalNumber(tracker, fmt='{:.1f}\u00b0', x=cx4, y=260,
                       font_size=56, fill='#D4ADFC', stroke_width=0,
                       text_anchor='middle')
vt_dec.fadein(1, 1.5)

tex_vt = TexCountAnimation(start_val=0, end_val=360, start=1, end=4,
                           fmt='{:.1f}\\degree', x=cx4, y=370, font_size=56,
                           fill='#D4ADFC', text_anchor='middle')
tex_vt.count_to(180, 5, 7)

# =====================================================================
# 5. Variable — labeled "x = 3.14" display
# =====================================================================
label5 = Text(text='Variable', x=960, y=480,
              font_size=32, fill='#888', stroke_width=0, text_anchor='middle')
label5.fadein(0.5, 1)

var = Variable('x', 0, fmt='{:.1f}', x=960, y=560, font_size=48,
               text_anchor='middle')
var.fadein(1, 1.5)
var.animate_value(25.0, start=2, end=4)
var.animate_value(-3.5, start=5, end=7)

tex_var = TexCountAnimation(start_val=0, end_val=25.0, start=2, end=4,
                            fmt='x = {:.1f}', x=960, y=670, font_size=48,
                            fill='#fff', text_anchor='middle')
tex_var.count_to(-3.5, 5, 7)

# =====================================================================
canvas.add_objects(
    title,
    label1, counter1, tex_counter1,
    label2, dec, tex_dec,
    label3, intnum, tex_int,
    label4, vt_dec, tex_vt,
    label5, var, tex_var,
)

if args.for_docs:
    canvas.export_video('docs/source/_static/videos/animations_counters.mp4', fps=30, end=8)
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=8)
