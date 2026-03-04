"""Automaton (finite state machine)."""
from vectormation.objects import *

v = VectorMathAnim()
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

v.show(end=0)
