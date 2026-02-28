Utilities
=========

Easings
-------

*Module:* ``vectormation.easings``

Easing functions control the pace of animations. Each accepts ``t`` in [0, 1]
and returns a value in [0, 1].

.. code-block:: python

   import vectormation.easings as easings
   circle.shift(dx=2, start=0, end=1, easing=easings.ease_out_bounce)

.. rubric:: Basic

.. py:function:: linear(t)

   Constant speed. No acceleration.

.. py:function:: smooth(t, inflection=10.0)

   Sigmoid-based smooth curve. Default for most animations.

.. py:function:: rush_into(t, inflection=10.0)

   Fast start, gradual stop.

.. py:function:: rush_from(t, inflection=10.0)

   Gradual start, fast end.

.. py:function:: there_and_back(t, inflection=10.0)

   Go out and come back. Used for effects like ``indicate`` and ``flash``.

.. py:function:: there_and_back_with_pause(t, pause_ratio=1.0/3)

   Out, pause, then back.

.. py:function:: wiggle(t, wiggles=2)

   Oscillating ease-out.

.. py:function:: lingering(t)

   Slow start, fast end.

.. py:function:: exponential_decay(t, half_life=0.1)

   Exponential decay.

.. rubric:: Sine

.. py:function:: ease_in_sine(t)
.. py:function:: ease_out_sine(t)
.. py:function:: ease_in_out_sine(t)

.. rubric:: Power (quad, cubic, quart, quint)

.. py:function:: ease_in_quad(t)
.. py:function:: ease_out_quad(t)
.. py:function:: ease_in_out_quad(t)
.. py:function:: ease_in_cubic(t)
.. py:function:: ease_out_cubic(t)
.. py:function:: ease_in_out_cubic(t)
.. py:function:: ease_in_quart(t)
.. py:function:: ease_out_quart(t)
.. py:function:: ease_in_out_quart(t)
.. py:function:: ease_in_quint(t)
.. py:function:: ease_out_quint(t)
.. py:function:: ease_in_out_quint(t)

.. rubric:: Exponential

.. py:function:: ease_in_expo(t)
.. py:function:: ease_out_expo(t)
.. py:function:: ease_in_out_expo(t)

.. rubric:: Circular

.. py:function:: ease_in_circ(t)
.. py:function:: ease_out_circ(t)
.. py:function:: ease_in_out_circ(t)

.. rubric:: Back (overshoot)

.. py:function:: ease_in_back(t)
.. py:function:: ease_out_back(t)
.. py:function:: ease_in_out_back(t)

.. rubric:: Elastic (oscillation)

.. py:function:: ease_in_elastic(t)
.. py:function:: ease_out_elastic(t)
.. py:function:: ease_in_out_elastic(t)

.. rubric:: Bounce

.. py:function:: ease_in_bounce(t)
.. py:function:: ease_out_bounce(t)
.. py:function:: ease_in_out_bounce(t)

.. rubric:: Combinators

.. py:function:: not_quite_there(func=smooth, proportion=0.7)

   Scale an easing's output to a proportion of the full range.

.. py:function:: squish_rate_func(func, a=0.4, b=0.6)

   Compress an easing into the interval ``[a, b]`` within [0, 1].

----

Colours & Gradients
-------------------

*Module:* ``vectormation.colors``

.. py:class:: LinearGradient(stops, x1='0%', y1='0%', x2='100%', y2='0%')

   SVG linear gradient. Register with ``canvas.add_def(lg)`` before use.

   :param list stops: List of ``(offset, color)`` or ``(offset, color, opacity)`` tuples.

   .. code-block:: python

      from vectormation.colors import LinearGradient
      lg = LinearGradient([('0%', '#ff0000'), ('100%', '#0000ff')])
      canvas.add_def(lg)
      circle = Circle(fill=lg, fill_opacity=1)

   .. py:method:: fill_ref()

      Returns the URL reference for use in fill attributes.

.. py:class:: RadialGradient(stops, cx='50%', cy='50%', r='50%', fx=None, fy=None)

   SVG radial gradient.

   :param list stops: List of ``(offset, color)`` or ``(offset, color, opacity)`` tuples.

   .. py:method:: fill_ref()

      Returns the URL reference for use in fill attributes.

.. rubric:: Utility Functions

.. py:function:: color_from_name(name)

   Get hex code from a named colour (e.g. ``'RED'``, ``'BLUE'``).

.. py:function:: color_gradient(color1, color2, n=5)

   Generate *n* interpolated hex colours between *color1* and *color2*.

.. py:function:: interpolate_color(color1, color2, t)

   Interpolate between two colours at ``t`` (0--1).

----

Filters & Definitions
---------------------

.. py:class:: ClipPath(*objects)

   SVG clip path definition. Pass one or more shape objects.

   .. code-block:: python

      clip = ClipPath(Circle(r=120, cx=960, cy=540))
      canvas.add_def(clip)
      rect = Rectangle(3, 3, clip_path=clip.clip_ref())

   .. py:method:: clip_ref()

      Returns the ``url(#...)`` reference string.

.. py:class:: BlurFilter(std_deviation=4)

   Gaussian blur filter.

   .. py:method:: filter_ref()

      Returns the ``url(#...)`` reference string.

.. py:class:: DropShadowFilter(dx=4, dy=4, std_deviation=4, color='#000', opacity=0.5)

   Drop shadow filter.

   .. py:method:: filter_ref()

      Returns the ``url(#...)`` reference string.

----

Styling Attributes
------------------

Every VObject has a ``styling`` attribute with these time-varying properties:

.. rubric:: Visual (SVG presentation attributes)

.. py:attribute:: styling.opacity
   :type: Real
   :value: 1

.. py:attribute:: styling.fill
   :type: Color
   :value: '#000'

.. py:attribute:: styling.fill_opacity
   :type: Real
   :value: 1

.. py:attribute:: styling.stroke
   :type: Color
   :value: '#000'

.. py:attribute:: styling.stroke_width
   :type: Real
   :value: 4

.. py:attribute:: styling.stroke_opacity
   :type: Real
   :value: 1

.. py:attribute:: styling.fill_rule
   :type: String
   :value: 'nonzero'

.. py:attribute:: styling.stroke_dasharray
   :type: String
   :value: ''

   Dash pattern (e.g. ``'10,5'``).

.. py:attribute:: styling.stroke_dashoffset
   :type: Real
   :value: 0

.. py:attribute:: styling.stroke_linecap
   :type: String
   :value: 'butt'

   ``'butt'``, ``'round'``, or ``'square'``.

.. py:attribute:: styling.stroke_linejoin
   :type: String
   :value: 'miter'

   ``'miter'``, ``'round'``, or ``'bevel'``.

.. py:attribute:: styling.clip_path
   :type: String
   :value: ''

.. rubric:: Transform attributes

.. py:attribute:: styling.dx
   :type: Real
   :value: 0

   Translation x offset.

.. py:attribute:: styling.dy
   :type: Real
   :value: 0

   Translation y offset.

.. py:attribute:: styling.scale_x
   :type: Real
   :value: 1

.. py:attribute:: styling.scale_y
   :type: Real
   :value: 1

.. py:attribute:: styling.rotation
   :type: Tup
   :value: (0, 0, 0)

   ``(degrees, cx, cy)`` -- counterclockwise positive.

.. py:attribute:: styling.skew_x
   :type: Real
   :value: 0

.. py:attribute:: styling.skew_y
   :type: Real
   :value: 0

.. py:attribute:: styling.matrix
   :type: Tup
   :value: (0, 0, 0, 0, 0, 0)

   SVG matrix transform ``(a, b, c, d, e, f)``.

----

Helper Functions
----------------

.. py:function:: parse_args()

   Common CLI argument parser. Returns an object with:
   ``verbose``, ``port``, ``fps``, ``no_display``, ``output``,
   ``duration``, ``start``, ``end``, ``hot_reload``.

.. py:function:: path_bbox(d)

   Bounding box of an SVG path string.

   :returns: ``(xmin, xmax, ymin, ymax)``

.. py:function:: path_length(d)

   Length of an SVG path string.

.. py:function:: from_svg(soup_element)

   Parse a single BeautifulSoup element into a VObject.

.. py:function:: from_svg_file(filename)

   Load an entire SVG file into a :py:class:`VCollection`.

.. py:function:: succession(*steps, start=0, lag_ratio=0.0)

   Chain multiple animation steps in sequence. Each step is a tuple
   ``(obj, method_name)`` or ``(obj, method_name, kwargs)``. Steps share the
   total time equally; ``lag_ratio`` controls overlap between consecutive steps.

   :param tuple steps: ``(vobject, method_name[, kwargs])`` tuples.
   :param float start: Start time.
   :param float lag_ratio: Overlap fraction (0 = sequential, 0.5 = 50% overlap).

   .. code-block:: python

      succession(
          (circle, 'fadein'),
          (square, 'write'),
          (text, 'fadein', {'shift_dir': 'up'}),
          start=0, lag_ratio=0.2,
      )

.. py:function:: transform_matching_shapes(source, target, start=0, end=1, key=None)

   Animate morphing between two VCollections by matching sub-objects.
   Unmatched source objects are faded out; unmatched target objects are faded in.

   :param source: Source VCollection or list of VObjects.
   :param target: Target VCollection or list of VObjects.
   :param float start: Start time.
   :param float end: End time.
   :param key: Optional function ``key(obj) -> hashable`` for matching.

.. py:function:: counterclockwise_morph(source, target, start=0, end=1, z=0, easing=smooth)

   Convenience wrapper: morph with a 180-degree counterclockwise rotation.
   Equivalent to ``MorphObject(source, target, rotation_degrees=-180, ...)``.

   :param VObject source: Source object.
   :param VObject target: Target object.

.. py:function:: transform_matching_tex(source, target, start=0, end=1)

   Animate morphing between two TexObjects by matching character content.
   Matched glyph paths are morphed; unmatched ones are faded out/in.

   :param TexObject source: The TexObject to morph from.
   :param TexObject target: The TexObject to morph to.

.. py:function:: interpolate_value(a, b, alpha)

   Linearly interpolate between two scalar values.

   :param float a: Start value.
   :param float b: End value.
   :param float alpha: Interpolation factor (0 = *a*, 1 = *b*).

.. py:function:: smooth_index(lst, real_index)

   Smoothly index into a list with a float index in [0, 1].
   Returns the linearly interpolated value between adjacent items.

   :param list lst: List of numeric values or coordinate tuples.
   :param float real_index: Index in [0, 1].
