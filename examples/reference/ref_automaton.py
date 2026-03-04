"""Automaton (finite state machine)."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

fsm = Automaton(
    states=['q0', 'q1', 'q2'],
    transitions=[
        ('q0', 'q1', 'a'),
        ('q1', 'q2', 'b'),
        ('q2', 'q0', 'c'),
        ('q1', 'q1', 'a'),
    ],
    accept_states={'q2'},
    initial_state='q0',
    radius=200,
)

v.add(fsm)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_automaton.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
