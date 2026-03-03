"""Code syntax highlighting with animated line highlights."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

W, H = 1100, 400
canvas = VectorMathAnim(width=W, height=H, verbose=args.verbose,
                        save_dir='svgs/code_highlight')
canvas.set_background()

title = Text(text='Code Highlighting', x=W // 2, y=40, font_size=40,
             fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 0.5)

CODE_SRC = """def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for i in range(2, n + 1):
        a, b = b, a + b
    return b"""

# ── Static syntax-highlighted Code (left) ─────────────────────────────

lbl_static = Text(text='Code (syntax highlighting)', x=W // 4, y=90,
                  font_size=16, fill='#999', stroke_width=0, text_anchor='middle')

code_static = Code(CODE_SRC, language='python', font_size=20,
                   x=W // 4 - 180, y=120)

# ── Animated highlight_lines walkthrough (right) ──────────────────────

lbl_anim = Text(text='highlight_lines walkthrough', x=3 * W // 4, y=90,
                font_size=16, fill='#999', stroke_width=0, text_anchor='middle')

code_anim = Code(CODE_SRC, language='python', font_size=20,
                 x=3 * W // 4 - 180, y=120, line_height=1.6)

# Highlight base case (lines 2-3)
code_anim.highlight_lines([2, 3], start=2, end=3.5, color='#2d5a1e', opacity=0.9)
# Highlight loop (lines 5-6)
code_anim.highlight_lines([5, 6], start=4, end=5.5, color='#1a4a5c', opacity=0.9)
# Highlight return (line 7)
code_anim.highlight_lines(7, start=6, end=7.5, color='#5c5a0a', opacity=0.9)

# ── Output ────────────────────────────────────────────────────────────

canvas.add_objects(title, lbl_static, code_static, lbl_anim, code_anim)

if args.for_docs:
    canvas.export_video('docs/source/_static/videos/code_highlight.mp4', fps=30, end=8)
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=8)
