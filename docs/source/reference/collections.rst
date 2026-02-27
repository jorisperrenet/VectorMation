Collections & Arrows
====================

VCollection
-----------

.. py:class:: VCollection(*objects, creation=0, z=0)

   Container that groups VObjects. Supports indexing (``collection[i]``),
   iteration, and ``len()``. Most :doc:`VObject <vobject>` methods are
   delegated to all children automatically.

   :param objects: VObject instances to group.

   .. rubric:: Management

   .. py:method:: add(*objs)

      Add objects to the collection.

   .. py:method:: remove(obj)

      Remove an object from the collection.

   .. py:method:: copy()

      Deep copy with independent animations.

   .. rubric:: Layout

   .. image:: ../_static/images/arrange.svg
      :width: 500
      :align: center

   .. py:method:: arrange(direction='right', buff=12, start=0)

      Lay out children in a row or column.

      :param str direction: ``'right'``, ``'left'``, ``'up'``, or ``'down'``.
      :param float buff: Spacing between children.

   .. py:method:: distribute(direction='right', buff=0, start=0)

      Distribute children evenly across the group's bounding box.

   .. py:method:: stagger(method_name, delay, **kwargs)

      Call a method on each child with staggered timing.

      .. code-block:: python

         group.stagger('fadein', delay=0.2, start=0, end=1)

   .. rubric:: Measurement

   .. py:method:: bbox(time, start_idx=0, end_idx=None)

      Bounding box (optionally for a sub-range of children).

   .. py:method:: brect(time, start_idx=0, end_idx=None, rx=0, ry=0, buff=12, follow=True)

      Bounding rectangle. Returns a :py:class:`Rectangle`.

   .. rubric:: Positioning

   .. py:method:: move_to(x, y, start=0, end=None, easing=smooth)

      Move the group's centre to ``(x, y)``.

   .. py:method:: center_to_pos(posx=960, posy=540, start=0, end=None, easing=smooth)

      Alias for :py:meth:`move_to`.

   .. py:method:: rotate_by(start, end, degrees, cx=None, cy=None, easing=smooth)

      Rotate all children by *degrees* around the group's centre.

   .. py:method:: rotate_to(start, end, degrees, cx=None, cy=None, easing=smooth)

      Rotate all children to an absolute angle.

   .. rubric:: Layout (additional)

   .. py:method:: arrange_in_grid(rows=None, cols=None, buff=12, start=0)

      Lay out children in a grid of *rows* x *cols*.

   .. py:method:: animated_arrange(direction='right', buff=12, start=0, end=1)

      Animated version of :py:meth:`arrange`: children slide to arranged positions.

   .. py:method:: animated_arrange_in_grid(rows=None, cols=None, buff=12, start=0, end=1)

      Animated version of :py:meth:`arrange_in_grid`.

   .. py:method:: distribute_radial(cx=960, cy=540, radius=300, start=0)

      Place children in a circle.

   .. rubric:: Animation

   .. py:method:: write(start, end, processing=10, max_stroke_width=2, change_existence=True)

      Staggered write animation across all children.

   .. py:method:: cascade(method_name, delay=0.2, **kwargs)

      Call *method_name* on each child with staggered timing.

   .. py:method:: sequential(method_name, **kwargs)

      Call *method_name* on children one after another, with no overlap.

   .. py:method:: swap_children(i, j, start=0, end=1, easing=smooth)

      Animate swapping positions of children *i* and *j* using arc paths.

   .. py:method:: shuffle_animate(start=0, end=1)

      Animated random shuffle of children.

   .. rubric:: Filtering & Iteration

   .. py:method:: filter(func)

      Return a new VCollection with only children where ``func(child)`` is true.

   .. py:method:: partition(func)

      Split into two VCollections based on a predicate.

   .. py:method:: for_each(func)

      Apply *func* to each child. Returns self.

   .. py:method:: sort_children(key, reverse=False)

      Sort children by a key function.

   .. rubric:: Color

   .. py:method:: set_color_by_gradient(colors, start=0)

      Assign a gradient of colours across children.

   .. py:method:: set_opacity_by_gradient(start_opacity, end_opacity, start=0)

      Assign a gradient of opacities across children.

----

MorphObject
-----------

.. py:class:: MorphObject(morph_from, morph_to, start=0, end=1, easing=smooth, change_existence=True, rotation_degrees=0)

   Bases: :py:class:`VCollection`

   Smoothly morph one shape (or collection) into another.

   :param morph_from: Source shape.
   :param morph_to: Target shape.
   :param float start: Start time.
   :param float end: End time.
   :param float rotation_degrees: Spiral morph rotation (0 = straight morph).

   .. code-block:: python

      morph = MorphObject(circle, square, start=1, end=3)
      canvas.add_objects(morph)

----

LabeledDot
----------

.. py:class:: LabeledDot(label='', r=24, cx=960, cy=540, font_size=None, **styling)

   Bases: :py:class:`VCollection`

   A dot with a centred text label.

   .. py:attribute:: dot
      :type: Dot

   .. py:attribute:: label
      :type: Text

----

Arrow
-----

.. image:: ../_static/images/arrow_params.svg
   :width: 440
   :align: center

.. py:class:: Arrow(x1=0, y1=0, x2=100, y2=100, tip_length=18, tip_width=12, **styling)

   Bases: :py:class:`VCollection`

   Line with a triangular arrowhead.

   :param float x1: Start x.
   :param float y1: Start y.
   :param float x2: End x.
   :param float y2: End y.
   :param float tip_length: Arrowhead length.
   :param float tip_width: Arrowhead width.

   .. py:attribute:: shaft
      :type: Line

   .. py:attribute:: tip
      :type: Polygon

----

DoubleArrow
-----------

.. py:class:: DoubleArrow(x1=0, y1=0, x2=100, y2=100, tip_length=18, tip_width=12, **styling)

   Bases: :py:class:`Arrow`

   Arrow with heads on both ends.

----

CurvedArrow
------------

.. image:: ../_static/images/curved_arrow_params.svg
   :width: 440
   :align: center

.. py:class:: CurvedArrow(x1=0, y1=0, x2=100, y2=100, angle=0.4, tip_length=18, tip_width=12, **styling)

   Bases: :py:class:`VCollection`

   Arrow with a quadratic Bezier curve shaft.

   :param float angle: Curvature angle.

----

Brace
-----

.. image:: ../_static/images/brace_params.svg
   :width: 400
   :align: center

.. py:class:: Brace(target, direction='down', label=None, buff=12, depth=18, **styling)

   Bases: :py:class:`VCollection`

   Curly brace annotation around a target object.

   :param target: The object to annotate.
   :param str direction: ``'up'``, ``'down'``, ``'left'``, or ``'right'``.
   :param str label: Optional text label.
   :param float buff: Distance from target.
   :param float depth: Brace depth.
