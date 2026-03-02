import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/automaton')
canvas.set_background()

# Build a simple DFA that accepts strings ending in "ab"
fsm = Automaton(
    states=['q0', 'q1', 'q2'],
    transitions=[
        ('q0', 'q1', 'a'),
        ('q1', 'q2', 'b'),
        ('q1', 'q1', 'a'),
        ('q0', 'q0', 'b'),
        ('q2', 'q1', 'a'),
        ('q2', 'q0', 'b'),
    ],
    initial_state='q0',
    accept_states={'q2'},
    radius=200,
)
fsm.fadein(0, 1)

# Simulate processing the string "aab" (auto-stepping through states)
fsm.simulate_input('aab', start=1.5, delay=1.0, color='#FFFF00')

title = Text(text='DFA: Accepts strings ending with "ab"', x=960, y=80,
             font_size=36, fill='#fff', stroke_width=0, text_anchor='middle')
title.fadein(0, 0.5)

canvas.add_objects(fsm, title)

if args.for_docs:
    canvas.export_video('docs/source/_static/videos/automaton_example.mp4', fps=30, end=6)
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=6)
