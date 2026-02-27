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

   .. py:method:: next_to(other, direction='right', buff=14, start=0)

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

   .. py:method:: pulsate(start=0, end=1, scale_factor=1.3, pulses=3, easing=smooth)

      Repeated scale pulses.

   .. py:method:: blink(start=0, end=None, count=1, duration=0.3, easing=smooth, num_blinks=None)

      Opacity blink. *count* (or *num_blinks*) sets repetitions.

   .. py:method:: wiggle(start=0, end=1, amplitude=12, n_wiggles=4, easing=there_and_back)

      Horizontal shake.

   .. py:method:: wave(start=0, end=1, amplitude=20, n_waves=2, direction='up', easing=there_and_back)

      Wave distortion.

   .. py:method:: circumscribe(start=0, end=1, buff=14, color='#FFFF00', stroke_width=4, easing=smooth)

      Draw then remove a tracing rectangle. Returns a :py:class:`Path`.

   .. py:method:: show_passing_flash(start=0, end=1, flash_width=0.15, easing=linear)

      Travelling highlight along stroke.

   .. py:method:: spiral_in(start=0, end=1, n_turns=1, change_existence=True, easing=smooth)

      Spiral in with rotation.

   .. py:method:: spiral_out(start=0, end=1, n_turns=1, change_existence=True, easing=smooth)

      Spiral out with rotation.

   .. py:method:: bounce(start=0, end=1, height=50, bounces=3, easing=smooth)

      Bouncing ball effect.

   .. py:method:: orbit(cx, cy, radius=None, start=0, end=1, degrees=360, easing=linear)

      Orbit around a centre point.

   .. py:method:: ripple(start=0, count=3, duration=0.5, max_radius=100, color='#58C4DD', stroke_width=2)

      Expanding rings from the object.

   .. py:method:: spring(start=0, end=1, amplitude=30, damping=5, frequency=4, axis='y')

      Damped spring oscillation.

   .. py:method:: shake(start=0, end=0.5, amplitude=5, frequency=20, easing=there_and_back)

      Random jitter.

   .. py:method:: rubber_band(start=0, end=1, easing=smooth)

      Rubber-band stretch and snap.

   .. py:method:: float_anim(start=0, end=1, amplitude=10, speed=1.0)

      Gentle floating up/down animation.

   .. py:method:: trail(start=0, end=1, num_copies=5, fade=True)

      Ghostly trail of fading copies following the object.

   .. py:method:: cross_out(start=0, end=0.5, color='#FC6255', stroke_width=4)

      Draw an X through the object.

   .. py:method:: shimmer(start=0, end=1, passes=2, easing=smooth)

      Shimmer the fill — briefly tints toward white and back.

   .. py:method:: swing(start=0, end=1, amplitude=15, damping=3, easing=smooth)

      Single damped pendulum swing.

   .. py:method:: undulate(start=0, end=1, amplitude=0.15, waves=2, easing=smooth)

      Decaying scale wave.

   .. py:method:: glitch(start=0, end=1, intensity=10, flashes=5)

      Random offset glitch flickers.

   .. py:method:: highlight_border(start=0, duration=0.5, color='#FFFF00', width=4)

      Briefly flash the object's border.

   .. py:method:: flash_color(start=0, duration=0.4, color='#FFFF00')

      Briefly flash a fill color (uses ``duration``).

   .. py:method:: pulse_outline(start=0, end=1, color='#FFFF00', stroke_width=4, easing=smooth)

      Pulsating outline glow.

   .. py:method:: emphasize(start=0, duration=0.8, color='#FFFF00', scale_factor=1.15, easing=there_and_back)

      Combined flash + scale emphasis (uses ``duration``).

   .. py:method:: breathe(start=0, end=1, amplitude=0.08, speed=1.0, easing=smooth)

      Gentle continuous breathing — steady scale oscillation.

   .. py:method:: heartbeat(start=0, end=1, speed=1.5, scale=1.1, easing=smooth)

      Heartbeat-style double-pulse.

   .. py:method:: dim(start=0, end=None, opacity=0.3, easing=smooth)

      Dim the object to a lower opacity.

   .. py:method:: undim(start=0, end=None, easing=smooth)

      Restore full opacity after :py:meth:`dim`.

   .. py:method:: set_width(width, start=0, stretch=False)

      Set the object width at *start*.

   .. py:method:: set_height(height, start=0, stretch=False)

      Set the object height at *start*.

   .. py:method:: broadcast(start=0, duration=0.5, color=None, max_radius=200)

      Expanding ring broadcast from the object centre.

   .. py:method:: clone(n=1, direction='right', buff=SMALL_BUFF, start=0)

      Create *n* fading clones positioned next to self.

   .. py:method:: add_label(text, direction='up', buff=20, font_size=None, start=0)

      Attach a text label next to the object.

   .. py:method:: place_between(a, b, alpha=0.5, start=0)

      Position self on the line between objects *a* and *b*.

   .. py:method:: show_if(predicate, start=0, end=None)

      Show the object only when *predicate(t)* is true.

   .. py:method:: always_next_to(other, direction='right', buff=14, start=0, end=None)

      Updater that continuously positions self next to *other*.

   .. py:method:: attach_to(other, direction=None, buff=None, start=0, end=None)

      Updater that attaches self to *other*.

   .. rubric:: State

   .. py:method:: save_state(time=0)

      Snapshot current position, scale, and styling.

   .. py:method:: restore(start=0, end=None, easing=smooth)

      Animate back to the saved state.

   .. py:method:: trace_path(start=0, end=1, stroke='#fff')

      Returns a :py:class:`Path` tracing this object's centre over time.

   .. rubric:: Transform

   .. py:method:: become(other, time=0)

      Copy *other*'s styling from *time* onward.

   .. py:method:: fade_transform(source, target, start=0, end=1)
      :staticmethod:

      Cross-fade between *source* and *target*.

   .. py:method:: swap(a, b, start=0, end=1, easing=smooth)
      :staticmethod:

      Swap positions of two objects.

   .. py:method:: surround(other, buff=14, rx=6, ry=6, start=0, follow=True)
      :staticmethod:

      Create a surrounding rectangle around *other*.

   .. py:method:: brect(time=0, rx=0, ry=0, buff=14, follow=True)

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
