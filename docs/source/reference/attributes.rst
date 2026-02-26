Attributes
==========

*Module:* ``vectormation.attributes``

All VObject properties (positions, sizes, colours) are **time-varying attributes**.
Instead of holding a single value, each attribute stores a function of time and
can be animated with ``move_to``, ``set_onward``, ``set``, etc.

----

Real
----

.. py:class:: Real(creation, start_val=0)

   Time-varying float. The fundamental attribute type.

   :param float creation: Creation time.
   :param float start_val: Initial value.

   .. py:attribute:: time_func
      :type: callable

      Internal function ``f(t) -> float``.

   .. py:attribute:: last_change
      :type: float

      Time of the most recent modification.

   .. rubric:: Reading

   .. py:method:: at_time(time)

      Get the value at *time*.

      :returns: ``float``

   .. rubric:: Setting Values

   .. py:method:: set_onward(start, value)

      Set a constant or callable from *start* onward. If *value* is callable,
      it receives ``t`` and should return a float.

      .. code-block:: python

         r.set_onward(0, 5.0)               # constant
         r.set_onward(0, lambda t: t * 2)    # function of time

   .. py:method:: add_onward(start, func)

      Add a constant or callable to the current value from *start* onward.

   .. py:method:: set(start, end, func_inner, stay=False)

      Override with a custom function on ``[start, end]``.
      If ``stay=True``, the end value persists after *end*.

      :param callable func_inner: ``f(t) -> float``

   .. py:method:: add(start, end, func_inner, stay=False)

      Add a function's output on ``[start, end]``.

   .. py:method:: set_at(time, value)

      Set value at a single point in time.

   .. py:method:: set_to(other)

      Copy another Real's time function.

   .. rubric:: Animation

   .. py:method:: move_to(start, end, end_val, stay=True, easing=smooth)

      Animate from current value to *end_val* over ``[start, end]``.

      .. code-block:: python

         circle.r.move_to(0, 2, 3.0)  # radius grows to 3 over 2 seconds

   .. py:method:: interpolate(other, start, end, easing=linear)

      Create a new Real that interpolates between ``self`` and *other*.

----

Coor
----

.. py:class:: Coor(creation, start_val=(0, 0))

   Bases: :py:class:`Real`

   Time-varying 2D coordinate ``(x, y)``. Inherits all Real methods.

   :param tuple start_val: Initial ``(x, y)`` position.

   .. py:method:: at_time(time)

      :returns: ``(float, float)``

   .. py:method:: move_to(start, end, end_val, stay=True, easing=smooth)

      Animate position to *end_val*.

      :param tuple end_val: Target ``(x, y)``.

      .. code-block:: python

         dot.c.move_to(0, 2, (12, 3))  # move to (12, 3) over 2 seconds

   .. py:method:: rotate_around(start, end, pivot_point, degrees, clockwise=False, stay=True)

      Rotate around a pivot point over ``[start, end]``.

      :param pivot_point: ``(x, y)`` tuple or Coor.
      :param float degrees: Rotation angle (counterclockwise by default).
      :param bool clockwise: Reverse direction.

      .. code-block:: python

         dot.c.rotate_around(0, 2, (960, 540), 360)  # full orbit

   .. py:method:: along_path(start, end, path_d, easing=smooth, stay=True)

      Move along an SVG path string over ``[start, end]``.

      :param str path_d: SVG path data.

----

Color
-----

.. py:class:: Color(creation=0, start_color='#000', use=None)

   Time-varying colour. Supports hex strings (``'#ff0000'``), RGB tuples
   (``(255, 0, 0)``), RGBA tuples, named colours, and gradients.

   .. py:method:: at_time(time)

      :returns: SVG colour string (e.g. ``'rgb(255,0,0)'``)

   .. py:method:: set_onward(start, value)

      Set colour from *start* onward. Accepts hex, RGB tuple, or callable.

   .. py:method:: interpolate(other, start, end, easing=linear, color_space='rgb')

      Interpolate to another colour.

      :param str color_space: ``'rgb'`` or ``'hsl'``.

   .. py:method:: interpolate_hsl(other, start, end, easing=linear)

      Interpolate through HSL colour space (smoother for hue transitions).

----

String
------

.. py:class:: String(creation, start_val='')

   Time-varying string attribute. Same interface as :py:class:`Real`.

----

Tup
---

.. py:class:: Tup(creation, start_val=())

   Bases: :py:class:`Real`

   Time-varying tuple. Used internally for rotation ``(degrees, cx, cy)``
   and matrix transforms. Interpolation is element-wise.
