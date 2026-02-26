Tutorial: Your First Animation
==============================

This tutorial walks through building a spiral animation step by step.

Every VectorMation script starts by creating a canvas:

.. code-block:: python

   from vectormation.objects import *

   canvas = VectorMathAnim(save_dir='svgs/tutorial')
   canvas.set_background()

Create a dot at the centre of the canvas and make it move rightward:

.. code-block:: python

   point = Dot(cx=960, cy=540)
   point.c.set(start=0, end=5, func_inner=lambda t: (t * 80 + 960, 540))

Add rotation around the canvas centre -- combined with the linear motion this creates a spiral:

.. code-block:: python

   point.c.rotate_around(0, 5, pivot_point=(960, 540), degrees=360 * 4)

A ``Trace`` follows a coordinate over time, drawing a polyline trail:

.. code-block:: python

   trace = Trace(point.c, stroke_width=4)

Register objects and open the browser viewer:

.. code-block:: python

   canvas.add_objects(trace, point)
   canvas.browser_display(fps=60)

Complete script:

.. code-block:: python

   from vectormation.objects import *

   canvas = VectorMathAnim(save_dir='svgs/tutorial')
   canvas.set_background()

   point = Dot(cx=960, cy=540)
   trace = Trace(point.c, stroke_width=4)
   point.c.set(start=0, end=5, func_inner=lambda t: (t * 80 + 960, 540))
   point.c.rotate_around(0, 5, pivot_point=(960, 540), degrees=360 * 4)

   canvas.add_objects(trace, point)
   canvas.browser_display(fps=60)

Next Steps
----------

- Browse the :doc:`Reference Manual <reference>` for all available objects and methods
- Understand the :doc:`time-varying attribute system <attributes>`
- Explore :doc:`browser controls and animation playback <animation>`
