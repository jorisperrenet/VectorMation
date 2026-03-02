"""1x2 grid showcasing Code syntax highlighting (static + animated)."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

COLS = 2
COL_W = 1920 // COLS
TITLE_Y = 50
FIRST_ROW = 120

canvas = VectorMathAnim(width=1920, height=900, verbose=args.verbose,
                        save_dir='svgs/code_highlight')
canvas.set_background()

def col_x(c): return COL_W // 2 + c * COL_W

title = Text(text='Code Highlighting', x=960, y=TITLE_Y, font_size=44,
             fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 0.5)
objs = [title]

CODE_SRC = """def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for i in range(2, n + 1):
        a, b = b, a + b
    return b"""

# ── (0) Static syntax-highlighted Code ───────────────────────────────────

lbl = Text(text='Code (syntax highlighting)', x=col_x(0), y=FIRST_ROW - 10,
           font_size=18, fill='#999', stroke_width=0, text_anchor='middle')
objs.append(lbl)

code_static = Code(CODE_SRC, language='python', font_size=24,
                   x=col_x(0) - 220, y=FIRST_ROW + 40)
objs.append(code_static)

# ── (1) Animated highlight_lines walkthrough ─────────────────────────────

lbl = Text(text='highlight_lines walkthrough', x=col_x(1), y=FIRST_ROW - 10,
           font_size=18, fill='#999', stroke_width=0, text_anchor='middle')

code_anim = Code(CODE_SRC, language='python', font_size=24,
                 x=col_x(1) - 220, y=FIRST_ROW + 40, line_height=1.6)

# Highlight base case (lines 2-3)
hl1 = code_anim.highlight_lines([2, 3], start=2, end=3.5, color='#83C167', opacity=0.2)
# Highlight loop (lines 5-6)
hl2 = code_anim.highlight_lines([5, 6], start=4, end=5.5, color='#58C4DD', opacity=0.2)
# Highlight return (line 7)
hl3 = code_anim.highlight_lines(7, start=6, end=7.5, color='#FFFF00', opacity=0.2)

objs.extend([lbl, hl1, hl2, hl3, code_anim])

# ── Output ────────────────────────────────────────────────────────────────

canvas.add_objects(*objs)

if args.for_docs:
    canvas.export_video('docs/source/_static/videos/code_highlight.mp4', fps=30, end=8)
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=8)
