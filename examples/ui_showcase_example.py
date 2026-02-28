"""Showcase of UI components: Badge, TextBox, SpeechBubble, ProgressBar, Divider."""
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim(verbose=args.verbose, save_dir='svgs/ui_showcase')

title = Title("UI Components", x=960, y=50)
title.fadein(start=0, end=0.5)

# --- Badges ---
b1 = Badge("v2.0", x=200, y=180, fill='#3498DB')
b2 = Badge("NEW", x=350, y=180, fill='#E74C3C')
b3 = Badge("OK", x=480, y=180, fill='#2ECC71')
for i, b in enumerate([b1, b2, b3]):
    b.fadein(start=0.5 + i * 0.3, end=1.0 + i * 0.3)

# --- TextBox ---
tb = TextBox("Enter your name...", x=200, y=300, width=300, height=50,
             fill='#1e1e2e', stroke='#555', text_fill='#aaa')
tb.fadein(start=1.5, end=2.5)

# --- SpeechBubble ---
sb = SpeechBubble("Hello world!", x=700, y=250, width=200, height=80,
                  fill='#2C3E50', text_fill='#ECF0F1')
sb.fadein(start=2, end=3)

# --- Divider ---
div = Divider(x=200, y=450, width=600, stroke='#555')
div.fadein(start=2.5, end=3.5)

# --- Checklist ---
cl = Checklist(["Buy milk", "Write code", "Deploy app"], x=200, y=550,
               font_size=22, fill='#fff')
cl.fadein(start=3, end=4)
cl.check(0, start=4.5, end=5)
cl.check(1, start=5, end=5.5)

# --- ProgressBar ---
pb = ProgressBar(value=0.3, x=800, y=550, width=400, height=30,
                 fill='#3498DB', track_fill='#1e1e2e')
pb.fadein(start=3.5, end=4.5)
pb.set_value(0.9, start=5, end=6.5)

# Fade out
for obj in [title, b1, b2, b3, tb, sb, div, cl, pb]:
    obj.fadeout(start=7, end=7.8)

v.add(title, b1, b2, b3, tb, sb, div, cl, pb)
v.browser_display(end=args.duration or 8, fps=args.fps, port=args.port, hot_reload=args.hot_reload)
