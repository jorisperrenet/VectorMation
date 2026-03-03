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

   .. py:method:: rotate_in(start=0, end=1, degrees=90, change_existence=True, easing=smooth)

      Fade in while rotating from an offset angle to 0.

   .. py:method:: grow_from_center(start=0, end=1, change_existence=True, easing=smooth)

      Scale from 0 to 1.

   .. py:method:: shrink_to_center(start=0, end=1, change_existence=True, easing=smooth)

      Scale from 1 to 0.

   .. py:method:: grow_from_edge(edge='bottom', start=0, end=1, change_existence=True, easing=smooth)

      Grow from a specified edge.

   .. py:method:: slide_in(direction='right', start=0, end=1, easing=smooth, change_existence=True)

      Slide in from off-screen.

   .. py:method:: slide_out(direction='right', start=0, end=1, easing=smooth, change_existence=True)

      Slide out to off-screen.

   .. py:method:: wipe(direction='right', start=0, end=1, easing=smooth, reverse=False)

      Clip-path wipe reveal (or hide if *reverse*).


   .. py:method:: pop_in(start=0, end=0.5, change_existence=True)

      Quick overshoot scale-in.

   .. py:method:: elastic_in(start=0, end=1, change_existence=True)

      Elastic bounce-in.

   .. py:method:: elastic_out(start=0, end=1, change_existence=True)

      Elastic bounce-out.

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

   .. py:method:: circumscribe(start=0, end=1, buff=14, color=None, easing=smooth, **styling)

      Draw then remove a tracing rectangle. Returns a :py:class:`Path`.

   .. py:method:: show_passing_flash(start=0, end=1, flash_width=0.15, color='#FFFF00', stroke_width=6, easing=linear)

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

   .. py:method:: swing(start=0, end=1, amplitude=15, cx=None, cy=None, easing=smooth)

      Single damped pendulum swing.

   .. py:method:: undulate(start=0, end=1, amplitude=0.15, waves=2, easing=smooth)

      Decaying scale wave.

   .. py:method:: glitch(start=0, end=1, intensity=10, flashes=5)

      Random offset glitch flickers.

   .. py:method:: highlight_border(start=0, duration=0.5, color='#FFFF00', width=4)

      Briefly flash the object's border.

   .. py:method:: flash_color(color='#FFFF00', start=0, duration=0.4, attr='fill')

      Briefly flash a fill color (uses ``duration``).

   .. py:method:: pulse_color(color='#FFFF00', start=0, end=1, pulses=3, attr='fill')

      Periodic color pulsing between current color and *color*.

   .. py:method:: pulse_outline(start=0, end=1, color='#FFFF00', max_width=8, cycles=2, easing=smooth)

      Pulsating outline glow.

   .. py:method:: emphasize(start=0, duration=0.8, color='#FFFF00', scale_factor=1.15, easing=there_and_back)

      Combined flash + scale emphasis (uses ``duration``).

   .. py:method:: breathe(start=0, end=1, amplitude=0.08, speed=1.0, easing=smooth)

      Gentle continuous breathing — steady scale oscillation.

   .. py:method:: heartbeat(start=0, end=1, beats=3, scale_factor=1.3, easing=smooth)

      Heartbeat-style double-pulse.

   .. py:method:: dim(start=0, end=None, opacity=0.3, easing=smooth)

      Dim the object to a lower opacity.

   .. py:method:: undim(start=0, end=None, easing=smooth)

      Restore full opacity after :py:meth:`dim`.

   .. py:method:: set_width(width, start=0, stretch=False)

      Set the object width at *start*.

   .. py:method:: set_height(height, start=0, stretch=False)

      Set the object height at *start*.

   .. py:method:: broadcast(start=0, duration=0.5, num_copies=3, max_scale=3, color=None)

      Emit expanding, fading copies from the object centre.
      Returns a :py:class:`VCollection` (must be added to canvas).

   .. py:method:: clone(offset_x=0, offset_y=0, *, count=None, dx=0, dy=0, start=0)

      Deep copy shifted by ``(offset_x, offset_y)``. When *count* is given,
      returns a :py:class:`VCollection` of *count* clones stepped by ``(dx, dy)``.

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

   .. rubric:: Combined Animations

   .. py:method:: create_then_fadeout(start=0, end=2, create_ratio=0.4, hold_ratio=0.2, easing=smooth)

      Create the object, hold, then fade out. Single-call convenience for
      objects that should appear briefly.

   .. py:method:: write_then_fadeout(start=0, end=2, write_ratio=0.4, hold_ratio=0.2, easing=smooth)

      Write the object (handwriting reveal), hold, then fade out.

   .. py:method:: fadein_then_fadeout(start=0, end=2, in_ratio=0.3, hold_ratio=0.4, easing=smooth)

      Fade in, hold, then fade out. Good for temporary annotations.

   .. py:method:: spin_in(start=0, end=1, degrees=360, change_existence=True, easing=smooth)

      Spin into existence by growing from center while rotating.

   .. py:method:: spin_out(start=0, end=1, degrees=360, change_existence=True, easing=smooth)

      Spin out of existence by shrinking to center while rotating.

   .. py:method:: draw_border_then_fill(start=0, end=1, change_existence=True, easing=smooth)

      First draw the outline, then fill the interior.

   .. py:method:: transform_from_copy(target, start=0, end=1, easing=smooth)

      Create a ghost copy of this object that morphs into *target*.
      Returns a :py:class:`MorphObject`.

      .. admonition:: Example: TransformFromCopy
         :class: example

         .. raw:: html

            <video src="../_static/videos/transform_from_copy_example.mp4" controls autoplay loop muted></video>

         ``transform_from_copy`` morphs a ghost duplicate while the original object stays in place.

         .. literalinclude:: ../../../examples/transform_from_copy_example.py
            :language: python
            :start-after: parse_args()
            :end-before: v.browser_display

   .. rubric:: Advanced Effects

   .. py:method:: apply_wave(start=0, end=1, amplitude=30, wave_func=None, direction='y', easing=smooth)

      Apply a sinusoidal wave distortion that travels across the object.
      Returns to original shape at both start and end.

   .. py:method:: scale_in_place(factor, start=0, end=1, easing=smooth)

      Scale the object without moving its center (anchored at current center).

   .. py:method:: telegraph(start=0, duration=0.4, scale_factor=1.4, shake_amplitude=8, easing=there_and_back)

      Quick attention-grabbing burst: scale spike + shake + opacity dip.

   .. py:method:: skate(tx, ty, start=0, end=1, degrees=360, easing=smooth)

      Slide to a target position while spinning.

   .. py:method:: slingshot(tx, ty, start=0, end=1, pullback=0.3, overshoot=0.15, easing=smooth)

      Pull back then launch toward target with overshoot.

   .. py:method:: elastic_bounce(start=0, end=1, height=100, bounces=3, squash_factor=1.4)

      Bounce with squash-and-stretch deformation.

   .. py:method:: morph_scale(target_scale=2.0, start=0, end=1, overshoot=0.3, oscillations=2)

      Scale to target with spring-like overshoot that settles.

   .. py:method:: unfold(start=0, end=1, direction='right', change_existence=True, easing=smooth)

      Unfold from zero width to full size along one axis.

   .. py:method:: stamp_trail(start=0, end=1, count=8, fade_duration=0.5, opacity=0.4)

      Leave ghostly fading copies along the path. Returns a list of ghost VObjects.

   .. py:method:: homotopy(func, start=0, end=1)

      Apply a continuous point-wise transformation ``func(x, y, t) -> (x', y')`` over time.

   .. py:method:: freeze(start, end=None)

      Freeze the object's appearance at time *start* until *end*.

   .. py:method:: bind_to(other, offset_x=0, offset_y=0, start=0, end=None)

      Keep this object at a fixed offset relative to another object's center.

   .. py:method:: pin_to(other, edge='center', offset_x=0, offset_y=0, start=0, end=None)

      Anchor this object to a specific edge/corner of *other*.

   .. py:method:: flicker(start=0, end=1, frequency=8, min_opacity=0.1, easing=smooth)

      Random-looking opacity flickering, like a failing light bulb.

   .. py:method:: strobe(start=0, end=1, flashes=5, duty=0.5)

      Rapid hard on/off blink effect like a strobe light.

   .. py:method:: wobble(start=0, end=1, intensity=5, frequency=3, easing=smooth)

      Organic wobbling motion combining small rotations and position shifts.

   .. py:method:: focus_zoom(start=0, end=1, zoom_factor=1.3, easing=smooth)

      Zoom in slightly then back to normal, like a camera focus.

   .. py:method:: match_style(other, time=0)

      Copy fill, stroke, opacity, and stroke_width from *other*.

   .. py:method:: match_position(other, time=0)

      Move so the center matches *other*'s center.

   .. py:method:: animate_to(target_obj, start=0, end=1, easing=smooth)

      Animate position, scale, and colors to match *target_obj*.

   .. py:method:: look_at(target, start=0, end=None, easing=smooth)

      Rotate so this object points toward *target*.

   .. py:method:: zoom_to(canvas, start=0, end=1, padding=100, easing=smooth)

      Animate the camera to zoom in and focus on this object.

   .. py:method:: set_gradient_fill(colors, direction='horizontal', start=0)

      Apply an SVG gradient fill to this object.

   .. py:method:: set_clip(clip_obj, start=0)

      Apply an SVG clip-path from another VObject's outline.

   .. py:method:: set_blend_mode(mode, start=0)

      Set the SVG mix-blend-mode. Supported: ``'normal'``, ``'multiply'``,
      ``'screen'``, ``'overlay'``, ``'darken'``, ``'lighten'``.

   .. py:method:: set_dash_pattern(pattern='dashes', start=0)

      Set stroke-dasharray. Presets: ``'solid'``, ``'dashes'``, ``'dots'``, ``'dash_dot'``.

   .. py:method:: set_lifetime(start, end)

      Visible only from *start* to *end*.

   .. py:method:: repeat_animation(method_name, count=2, start=0, end=1, **kwargs)

      Repeat an animation method *count* times within [start, end].

   .. py:method:: add_updater(func, start=0, end=None)

      Add a custom updater function ``func(obj, time)`` called each frame.

   .. rubric:: Measurement (continued)

   .. py:method:: get_center(time=0)

      Alias for :py:meth:`center`.

   .. py:method:: distance_to(other, time=0)

      Euclidean distance between centers.

   .. py:method:: point_from_proportion(t, time=0)

      Return the ``(x, y)`` point at proportion *t* (0-1) along this object's path outline.
