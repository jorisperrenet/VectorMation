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

# Animate processing the string "aab"
fsm.highlight_state('q0', 1, 2, color='#FFFF00')  # start
fsm.highlight_state('q1', 2, 3, color='#FFFF00')  # read 'a'
fsm.highlight_state('q1', 3, 4, color='#FFFF00')  # read 'a'
fsm.highlight_state('q2', 4, 5, color='#58C4DD')  # read 'b' -> accept!

canvas.add_objects(fsm)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
