"""Simple flowchart."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

flow = FlowChart(['Input', 'Validate', 'Process', 'Output'],
                 direction='right', box_color='#58C4DD', spacing=100)
flow.center_to_pos()

v.add(flow)

v.show(end=2)
