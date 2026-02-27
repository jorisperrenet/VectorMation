VObject
=======

Coordinate System
-----------------

All positions use SVG pixel coordinates on a 1920 x 1080 canvas. ``ORIGIN`` is
the centre at ``(960, 540)``. Direction constants use screen conventions where
**Y increases downward**.

.. image:: ../_static/images/coordinate_system.svg
   :width: 520
   :align: center

.. py:class:: VObject(creation=0, z=0)

   Abstract base class for all visual objects. Every VObject has a
   :py:attr:`styling` instance controlling fill, stroke, opacity, and transforms,
   plus time-varying :py:attr:`show` and :py:attr:`z` attributes.

   .. rubric:: Measurement

   .. py:method:: bbox(time)

      Bounding box at *time*.

      :returns: ``(xmin, ymin, width, height)``

   .. py:method:: center(time=0)

      Centre of the bounding box.

      :returns: ``(cx, cy)``

   .. py:method:: get_width(time=0)

      Width of the bounding box.

   .. py:method:: get_height(time=0)

      Height of the bounding box.

   .. py:method:: get_edge(edge, time=0)

      Coordinate of a named edge.

      :param str edge: One of ``'top'``, ``'bottom'``, ``'left'``, ``'right'``,
         ``'center'``, ``'top_left'``, ``'top_right'``, ``'bottom_left'``,
         ``'bottom_right'``.
      :returns: ``(x, y)``

   .. image:: ../_static/images/edges.svg
      :width: 440
      :align: center

   .. py:method:: path(time)

      SVG path string (``d`` attribute) for this object at *time*.

   .. rubric:: Movement

   .. py:method:: shift(dx=0, dy=0, start=0, end=None, easing=smooth)

      Translate by ``(dx, dy)``. If *end* is given, the shift is animated.

   .. py:method:: move_to(x, y, start=0, end=None, easing=smooth)

      Move the object's centre to ``(x, y)``.

   .. py:method:: center_to_pos(posx=960, posy=540, start=0, end=None, easing=smooth)

      Alias for :py:meth:`move_to`.

   .. py:method:: along_path(start, end, path_d, easing=smooth)

      Move the object's centre along an SVG path string over ``[start, end]``.

   .. py:method:: next_to(other, direction='right', buff=12, start=0)

      Position adjacent to *other*. ``direction`` can be ``'right'``, ``'left'``,
      ``'up'``, or ``'down'``.

   .. image:: ../_static/images/next_to.svg
      :width: 440
      :align: center

   .. py:method:: align_to(other, edge='left', start=0)

      Align the given edge with the same edge of *other*.

   .. rubric:: Rotation

   .. py:method:: rotate_by(start, end, degrees, cx=None, cy=None, easing=smooth)

      Rotate by *degrees* (counterclockwise) over ``[start, end]``.
      Rotates around the object's centre unless ``cx, cy`` are given.

   .. py:method:: rotate_to(start, end, degrees, cx=None, cy=None, easing=smooth)

      Rotate to an absolute angle.

   .. py:method:: spin(start=0, end=1, degrees=360, cx=None, cy=None, easing=linear)

      Full rotation (default 360 degrees).

   .. py:method:: always_rotate(start=0, end=None, degrees_per_second=90, cx=None, cy=None)

      Continuous rotation at a constant speed.

   .. rubric:: Scale

   .. py:method:: scale(factor, start=0, end=None, easing=smooth)

      Uniform scale. Animated if *end* is given.

   .. py:method:: scale_by(start, end, factor, easing=smooth)

      Animate scale by a relative factor over ``[start, end]``.

   .. py:method:: scale_to(start, end, factor, easing=smooth)

      Animate to an absolute scale factor.

   .. py:method:: stretch(x_factor=1, y_factor=1, start=0, end=None, easing=smooth)

      Non-uniform scale.

   .. py:method:: match_width(other, time=0)

      Scale uniformly to match *other*'s width.

   .. py:method:: match_height(other, time=0)

      Scale uniformly to match *other*'s height.

   .. rubric:: Creation & Visibility

   .. py:method:: fadein(start=0, end=1, change_existence=True, easing=smooth)

      Fade opacity from 0 to current value.

   .. py:method:: fadeout(start=0, end=1, change_existence=True, easing=smooth)

      Fade opacity to 0.

   .. py:method:: write(start=0, end=1, max_stroke_width=2, change_existence=True)

      Handwriting reveal: strokes the outline then fills.

   .. py:method:: create(start=0, end=1, change_existence=True, easing=smooth)

      Draw the path progressively from nothing. Returns a new :py:class:`Path`.

   .. py:method:: draw_along(start=0, end=1, easing=smooth, change_existence=True)

      Reveal stroke via animated dashoffset.

   .. py:method:: grow_from_center(start=0, end=1, change_existence=True, easing=smooth)

      Scale from 0 to 1.

   .. py:method:: shrink_to_center(start=0, end=1, change_existence=True, easing=smooth)

      Scale from 1 to 0.

   .. py:method:: grow_from_edge(edge='bottom', start=0, end=1, change_existence=True, easing=smooth)

      Grow from a specified edge.

   .. rubric:: Colour & Styling

   .. py:method:: set_color(start, end, fill=None, stroke=None, easing=smooth, color_space='rgb')

      Animate a colour change over ``[start, end]``.

   .. py:method:: set_fill(color, start=0, end=None, easing=smooth, color_space='rgb')

      Set the fill colour.

   .. py:method:: set_stroke(color=None, width=None, start=0, end=None, easing=smooth)

      Set stroke colour and/or width.

   .. py:method:: set_opacity(value, start=0, end=None, easing=smooth)

      Set overall opacity.

   .. rubric:: Effects

   .. py:method:: indicate(start=0, end=1, scale_factor=1.2, easing=there_and_back)

      Brief scale-up highlight.

   .. py:method:: flash(start=0, end=1, color='#FFFF00', easing=there_and_back)

      Flash the fill colour then return to original.

   .. py:method:: pulse(start=0, end=1, scale_factor=1.5, easing=there_and_back)

      Scale-with-fade pulse.

   .. py:method:: blink(start=0, duration=0.3, easing=smooth)

      Opacity blink.

   .. py:method:: wiggle(start=0, end=1, amplitude=12, n_wiggles=4, easing=there_and_back)

      Horizontal shake.

   .. py:method:: wave(start=0, end=1, amplitude=20, n_waves=2, direction='up', easing=there_and_back)

      Wave distortion.

   .. py:method:: circumscribe(start=0, end=1, buff=12, color='#FFFF00', stroke_width=4, easing=smooth)

      Draw then remove a tracing rectangle. Returns a :py:class:`Path`.

   .. py:method:: show_passing_flash(start=0, end=1, flash_width=0.2, easing=linear)

      Travelling highlight along stroke.

   .. py:method:: spiral_in(start=0, end=1, n_turns=1, change_existence=True, easing=smooth)

      Spiral in with rotation.

   .. rubric:: Transform

   .. py:method:: become(other, time=0)

      Copy *other*'s styling from *time* onward.

   .. py:method:: fade_transform(source, target, start=0, end=1)
      :staticmethod:

      Cross-fade between *source* and *target*.

   .. py:method:: swap(a, b, start=0, end=1, easing=smooth)
      :staticmethod:

      Swap positions of two objects.

   .. py:method:: surround(other, buff=12, rx=6, ry=6, start=0, follow=True)
      :staticmethod:

      Create a surrounding rectangle around *other*.

   .. py:method:: brect(time=0, rx=0, ry=0, buff=12, follow=True)

      Bounding rectangle. Returns a :py:class:`Rectangle`.

   .. py:method:: copy()

      Deep copy with independent animations.

   .. rubric:: Z-Order

   .. py:method:: set_z(value, start=0)

      Set z-order value.

   .. py:method:: to_front(start=0)

      Bring to front (z = 999).

   .. py:method:: to_back(start=0)

      Send to back (z = -999).
