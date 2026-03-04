Attributes: Time-Varying Values
================================

VectorMation's core idea is that **every visual property is a function of time**. The attribute system provides a composable way to define and modify these functions.

Attribute Types
---------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Type
     - Holds
     - Example
   * - ``Real``
     - A single number
     - radius, opacity, x-coordinate
   * - ``Coor``
     - A 2D coordinate ``(x, y)``
     - centre of a circle
   * - ``Color``
     - An RGB/RGBA colour
     - fill colour
   * - ``String``
     - A string
     - SVG path data, text content
   * - ``Tup``
     - An arbitrary-length tuple
     - rotation ``(deg, cx, cy)``

.. note::

   Every shape exposes its properties as attributes. For example a ``Circle``
   has ``circle.r`` (radius) and ``circle.c`` (centre), a ``Rectangle`` has
   ``rect.width`` and ``rect.height``, and a ``Text`` has ``text.font_size``.
   You can animate any of these by calling methods like ``move_to`` on them.

Reading Values
--------------

Every attribute has ``.at_time(t)`` to get its value at time ``t``:

.. code-block:: python

   circle = Circle(r=100, cx=500, cy=500)
   print(circle.r.at_time(0))   # 100
   print(circle.c.at_time(0))   # (500, 500)

Setting Values
--------------

``set(start, end, func_inner)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Replace the attribute's value with ``func_inner(t)`` on the interval ``[start, end]``:

.. code-block:: python

   # Move the circle's radius from 100 to 200 over 2 seconds
   circle.r.set(0, 2, lambda t: 100 + 50 * t)

``set_onward(start, value)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Set the attribute to a constant (or function) from ``start`` onwards:

.. code-block:: python

   circle.r.set_onward(3, 50)  # radius becomes 50 at t=3 and stays
   circle.r.set_onward(3, lambda t: 50 + 10 * t)  # or a function

``add_onward(start, func_or_value)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add to the existing value from ``start`` onwards. Accepts a constant or a function:

.. code-block:: python

   circle.r.add_onward(2, 20)  # radius increases by 20 from t=2

   # With a function: oscillate the radius around its current value
   import math
   circle.r.add_onward(0, lambda t: 10 * math.sin(t * 4))

``move_to(start, end, end_val, easing=smooth)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Smoothly animate from the current value to ``end_val``:

.. code-block:: python

   circle.r.move_to(0, 2, 200)  # smoothly grow radius to 200

.. admonition:: Example: animating radius with move_to
   :class: example

   .. raw:: html

      <video src="_static/videos/attr_move_to.mp4" controls autoplay loop muted></video>

   Smoothly grow and shrink a circle's radius using ``move_to``.

   .. literalinclude:: ../../examples/reference/attr_move_to.py
      :language: python
      :start-after: parse_args()
      :end-before: v.browser_display

Composing Attribute Calls
-------------------------

Attribute methods compose naturally over time. You can chain ``move_to``,
``set_onward``, and other calls to build complex animations from simple
primitives:

.. admonition:: Example: chaining attribute calls
   :class: example

   .. raw:: html

      <video src="_static/videos/attr_composition.mp4" controls autoplay loop muted></video>

   A dot slides to the centre, jumps up instantly with ``set_onward``, then
   slides to the right with another ``move_to``.

   .. literalinclude:: ../../examples/reference/attr_composition.py
      :language: python
      :start-after: parse_args()
      :end-before: v.browser_display

Coordinate-Specific Methods
----------------------------

``Coor`` attributes have additional methods:

``rotate_around(start, end, pivot_point, degrees)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   dot.c.rotate_around(0, 5, pivot_point=(500, 500), degrees=360)

The coordinate rotates around the pivot point. ``pivot_point`` can be a tuple or a callable returning ``(x, y)``.

``move_to(start, end, end_pos, easing=smooth)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   dot.c.move_to(0, 2, (800, 200))  # smoothly move to (800, 200)

Easing Functions
----------------

Easing functions control the rate of change over a normalised ``[0, 1]`` interval.

.. image:: _static/images/easing_curves.svg
   :width: 520
   :align: center

Available easings (from ``vectormation.easings``):

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Function
     - Description
   * - ``linear``
     - Constant speed
   * - ``smooth``
     - Sigmoid-based smooth start/stop
   * - ``rush_into``
     - Fast start, smooth end
   * - ``rush_from``
     - Smooth start, fast end
   * - ``there_and_back``
     - Goes to 1 at midpoint, back to 0
   * - ``ease_in_quad``, ``ease_out_quad``, ``ease_in_out_quad``
     - Quadratic easings
   * - ``ease_in_cubic``, ``ease_out_cubic``, ``ease_in_out_cubic``
     - Cubic easings
   * - ``ease_in_elastic``, ``ease_out_elastic``
     - Spring-like bounce
   * - ``ease_in_bounce``, ``ease_out_bounce``
     - Bouncing effect

And many more -- see ``vectormation/easings.py`` for the full list.

.. admonition:: Example: comparing easings
   :class: example

   .. raw:: html

      <video src="_static/videos/attr_easing.mp4" controls autoplay loop muted></video>

   Three circles shift across the screen using ``linear``, ``smooth``, and
   ``ease_out_bounce`` easings.

   .. literalinclude:: ../../examples/reference/attr_easing.py
      :language: python
      :start-after: parse_args()
      :end-before: v.browser_display

Color Attributes
----------------

Colors can be specified as hex strings, colour names, or RGB tuples:

.. code-block:: python

   circle = Circle(fill='#58C4DD')         # hex
   circle = Circle(fill='RED')             # colour name
   circle = Circle(fill=(88, 196, 221))    # RGB tuple

Color attributes support ``set()``, ``set_onward()``, and ``interpolate()`` just like ``Real`` attributes.

HSL Interpolation
^^^^^^^^^^^^^^^^^

By default, colours interpolate in RGB space. For smoother hue transitions (e.g. rainbow effects), use HSL:

.. code-block:: python

   circle.set_color(start=0, end=2, fill='#FF0000', stroke='#0000FF', color_space='hsl')

The ``color_space`` parameter is available on ``set_color()`` and ``Color.interpolate()``.

.. admonition:: Example: RGB vs HSL interpolation
   :class: example

   .. raw:: html

      <video src="_static/videos/attr_color.mp4" controls autoplay loop muted></video>

   Top circle interpolates from red to blue in RGB (goes through purple).
   Bottom circle interpolates in HSL (sweeps through the hue spectrum).

   .. literalinclude:: ../../examples/reference/attr_color.py
      :language: python
      :start-after: parse_args()
      :end-before: v.browser_display
