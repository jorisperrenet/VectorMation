Tutorial: Your First Animation
==============================

This tutorial walks through building animations step by step, starting from
the very basics.

The Coordinate System
---------------------

VectorMation uses an SVG canvas of **1920 x 1080** pixels. The origin
(``ORIGIN``) is at the **centre** of the canvas: ``(960, 540)``.

- **X** increases to the right
- **Y** increases downward (standard SVG convention)
- One abstract unit (``UNIT``) equals 135 pixels

Direction constants like ``UP``, ``DOWN``, ``LEFT``, ``RIGHT`` are available
for convenience. Note that ``UP = (0, -1)`` because Y points down.

Hello Shapes
------------

Every VectorMation script starts by creating a canvas:

.. code-block:: python

   from vectormation.objects import *

   canvas = VectorMathAnim()
   canvas.set_background()

Create some shapes, add entrance animations, and display them:

.. admonition:: Example: basic shapes
   :class: example

   .. raw:: html

      <video src="_static/videos/tutorial_shapes.mp4" controls autoplay loop muted></video>

   Create a circle, rectangle, and text. Fade them in one at a time,
   then shift them all upward together.

   .. literalinclude:: ../../examples/reference/tutorial_shapes.py
      :language: python

The Timing Model
----------------

Animations are scheduled with ``start=`` and ``end=`` parameters. Every
animation method accepts these two values (in seconds):

.. code-block:: python

   dot.fadein(start=0, end=1)        # fade in during t=0..1
   dot.shift(dx=300, start=1, end=2) # slide right during t=1..2
   dot.shift(dy=-200, start=2, end=3) # slide up during t=2..3

Animations at different times happen sequentially; animations at the same
time happen simultaneously.

.. admonition:: Example: timing model
   :class: example

   .. raw:: html

      <video src="_static/videos/tutorial_timing.mp4" controls autoplay loop muted></video>

   Sequential ``shift`` calls with consecutive ``start``/``end`` values
   create a step-by-step path.

   .. literalinclude:: ../../examples/reference/tutorial_timing.py
      :language: python

Building a Spiral
-----------------

Now let's build something more interesting. Create a dot at the centre and
make it move rightward:

.. code-block:: python

   point = Dot(cx=960, cy=540)
   point.c.set(0, 5, lambda t: (t * 80 + 960, 540))

Add rotation around the canvas centre -- combined with the linear motion this
creates a spiral:

.. code-block:: python

   point.c.rotate_around(0, 5, (960, 540), 360 * 4)

A ``Trace`` follows a coordinate over time, drawing a polyline trail:

.. code-block:: python

   trace = Trace(point.c)

Register objects and open the browser viewer:

.. code-block:: python

   canvas.add(trace, point)
   canvas.show(end=6)

.. admonition:: Example: spiral animation
   :class: example

   .. raw:: html

      <video src="_static/videos/tutorial_spiral.mp4" controls autoplay loop muted></video>

   A dot spirals outward for 4 revolutions while leaving a trace trail.

   .. literalinclude:: ../../examples/reference/tutorial_spiral.py
      :language: python

Next Steps
----------

- Browse the :doc:`Reference Manual <reference>` for all available objects and methods
- Understand the :doc:`time-varying attribute system <attributes>`
- Explore :doc:`browser controls and animation playback <animation>`
