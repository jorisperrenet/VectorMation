from vectormation.objects import *

canvas = VectorMathAnim()
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

canvas.show(end=6)
