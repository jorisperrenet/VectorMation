Collections, Arrows & Data Structures
======================================

Collections
-----------

VCollection
~~~~~~~~~~~

.. py:class:: VCollection(*objects, creation=0, z=0)

   Container that groups VObjects. Supports indexing (``collection[i]``),
   iteration, and ``len()``. Most :doc:`VObject <vobject>` methods are
   delegated to all children automatically. ``VGroup`` is an alias.

   :param objects: VObject instances to group.

   .. rubric:: Management

   .. py:method:: add(*objs)

      Add objects to the collection.

   .. py:method:: remove(obj)

      Remove an object from the collection.

   .. py:method:: insert_at(index, *objs)

      Insert objects at a specific index.

   .. py:method:: remove_at(index)

      Remove the child at *index*.

   .. py:method:: clear()

      Remove all children.

   .. py:method:: copy()

      Deep copy with independent animations.

   .. rubric:: Child access

   .. py:method:: first()

      Return the first child.

   .. py:method:: last()

      Return the last child.

   .. py:method:: nth(n)

      Return the *n*-th child.

   .. py:method:: get_child(index)

      Return child at *index*.

   .. py:method:: select(start=0, end=None)

      Return a new VCollection with a slice of children.

   .. rubric:: Z-order

   .. py:method:: send_to_back(child)

      Move *child* to the back (lowest z-order).

   .. py:method:: bring_to_front(child)

      Move *child* to the front (highest z-order).

   .. rubric:: Layout

   .. py:method:: arrange(direction='right', buff=14, start=0)

      Lay out children in a row or column.

      :param str direction: ``'right'``, ``'left'``, ``'up'``, or ``'down'``.
      :param float buff: Spacing between children.

   .. admonition:: Example: arrange
      :class: example

      .. raw:: html

         <video src="../_static/videos/arrange.mp4" controls autoplay loop muted></video>

      Arrange and distribute shapes in a row.

      .. literalinclude:: ../../../examples/reference/arrange.py
         :language: python

   .. image:: ../_static/images/arrange.svg
      :width: 500
      :align: center

   .. py:method:: distribute(direction='right', buff=0, start=0)

      Distribute children evenly across the group's bounding box.

   .. py:method:: stagger(method_name, start=0, end=1, overlap=0.5, **kwargs)

      Call an animation method on children with overlapping timing.
      ``overlap``: 0 = sequential, 1 = all simultaneous.

      .. admonition:: Example: Staggered animation across children
         :class: example

         .. code-block:: python

            group.stagger('fadein', start=0, end=1, overlap=0.5)

   .. admonition:: Example: stagger
      :class: example

      .. raw:: html

         <video src="../_static/videos/stagger.mp4" controls autoplay loop muted></video>

      Staggered fade-in across children.

      .. literalinclude:: ../../../examples/reference/stagger.py
         :language: python

   .. admonition:: Example: ref_stagger
      :class: example

      .. raw:: html

         <video src="../_static/videos/ref_stagger.mp4" controls autoplay loop muted style="width:100%;max-width:800px;display:block;margin:auto;"></video>

      .. literalinclude:: ../../../examples/reference/ref_stagger.py
         :language: python

   .. rubric:: Measurement

   .. py:method:: bbox(time, start_idx=0, end_idx=None)

      Bounding box (optionally for a sub-range of children).

   .. py:method:: brect(time, start_idx=0, end_idx=None, rx=0, ry=0, buff=14, follow=True)

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

   .. py:method:: arrange_in_grid(rows=None, cols=None, buff=14, start=0)

      Lay out children in a grid of *rows* x *cols*.

   .. py:method:: animated_arrange(direction='right', buff=14, start=0, end=1)

      Animated version of :py:meth:`arrange`: children slide to arranged positions.

   .. py:method:: animated_arrange_in_grid(rows=None, cols=None, buff=14, start=0, end=1)

      Animated version of :py:meth:`arrange_in_grid`.

   .. py:method:: space_evenly(direction='right', total_span=None, start=0)

      Space children evenly along an axis.

   .. py:method:: spread(x1, y1, x2, y2, start=0)

      Distribute children evenly between two points.

   .. admonition:: Example: spread
      :class: example

      .. raw:: html

         <img src="../_static/videos/ref_spread.svg" style="width:100%; max-width:800px;" />

      .. literalinclude:: ../../../examples/reference/ref_spread.py
         :language: python

   .. py:method:: align_submobjects(edge='left', start=0)

      Align all children's edges.

   .. rubric:: Animation

   .. py:method:: write(start, end, processing=10, max_stroke_width=2, change_existence=True)

      Staggered write animation across all children.

   .. admonition:: Example: write (collection)
      :class: example

      .. raw:: html

         <video src="../_static/videos/ref_write_collection.mp4" controls autoplay loop muted style="width:100%;max-width:800px;display:block;margin:auto;"></video>

      .. literalinclude:: ../../../examples/reference/ref_write_collection.py
         :language: python

   .. py:method:: stagger_fadein_sorted(start=0, end=1, direction='left_to_right', easing=smooth)

      Fade in children based on spatial ordering.
      Directions: ``'left_to_right'``, ``'top_to_bottom'``, ``'center_out'``.

   .. py:method:: swap_children(i, j, start=0, end=1, easing=smooth)

      Animate swapping positions of children *i* and *j* using arc paths.

   .. admonition:: Example: swap_children
      :class: example

      .. raw:: html

         <video src="../_static/videos/ref_swap_children.mp4" controls autoplay loop muted></video>

      .. literalinclude:: ../../../examples/reference/ref_swap_children.py
         :language: python

   .. py:method:: shuffle_animate(start=0, end=1)

      Animated random shuffle of children.

   .. admonition:: Example: shuffle_animate
      :class: example

      .. raw:: html

         <video src="../_static/videos/ref_shuffle_animate.mp4" controls autoplay loop muted></video>

      .. literalinclude:: ../../../examples/reference/ref_shuffle_animate.py
         :language: python

   .. py:method:: reveal(start=0, end=1, direction='left', easing=smooth)

      Staggered reveal of children sliding into view.

   .. admonition:: Example: reveal
      :class: example

      .. raw:: html

         <video src="../_static/videos/ref_reveal.mp4" controls autoplay loop muted style="width:100%;max-width:800px;display:block;margin:auto;"></video>

      .. literalinclude:: ../../../examples/reference/ref_reveal.py
         :language: python

   .. py:method:: stagger_fadein(start=0, end=1, shift_dir=None, shift_amount=50, overlap=0.5, easing=smooth)

      Staggered fade-in of children with optional directional shift.

   .. admonition:: Example: stagger_fadein
      :class: example

      .. raw:: html

         <video src="../_static/videos/ref_stagger_fadein.mp4" controls autoplay loop muted style="width:100%;max-width:800px;display:block;margin:auto;"></video>

      .. literalinclude:: ../../../examples/reference/ref_stagger_fadein.py
         :language: python

   .. py:method:: wave_anim(start=0, end=1, amplitude=20, waves=1)

      Wave animation through children.

   .. admonition:: Example: wave_anim
      :class: example

      .. raw:: html

         <video src="../_static/videos/ref_wave_anim.mp4" controls autoplay loop muted style="width:100%;max-width:800px;display:block;margin:auto;"></video>

      .. literalinclude:: ../../../examples/reference/ref_wave_anim.py
         :language: python

   .. py:method:: highlight_child(index, start=0, end=1, dim_opacity=0.2, easing=smooth)

      Emphasize child at *index* by dimming all others.

   .. py:method:: wave_effect(start=0, end=1, amplitude=20, axis='y', easing=smooth)

      Wave displacement through children.

   .. py:method:: stagger_along_path(method_name, path_d, start=0, end=1, **kwargs)

      Stagger method calls along an SVG path.

   .. py:method:: stagger_random(method_name, start=0, end=1, seed=None, **kwargs)

      Stagger method calls with random timing.

   .. py:method:: label_children(labels, direction=UP, buff=20, font_size=None, creation=0)

      Add text labels above (or beside) each child.

   .. rubric:: Filtering & Iteration

   .. py:method:: filter(func)

      Return a new VCollection with only children where ``func(child)`` is true.

   .. py:method:: partition(func)

      Split into two VCollections based on a predicate.

   .. py:method:: for_each(func)

      Apply *func* to each child. Returns self.

   .. py:method:: sort_children(key, reverse=False)

      Sort children by a key function.

   .. py:method:: sort_objects(key=None, reverse=False, time=0)

      Sort children in-place. Default key: x position.

   .. py:method:: shuffle()

      Randomly shuffle children order.

   .. py:method:: rotate_children(degrees=90, start=0, end=None, easing=smooth)

      Rotate all children around the group's centre.

   .. rubric:: Color

   .. py:method:: set_color_by_gradient(colors, start=0)

      Assign a gradient of colours across children.

   .. py:method:: set_opacity_by_gradient(start_opacity, end_opacity, start=0)

      Assign a gradient of opacities across children.

   .. rubric:: Advanced

   .. py:method:: distribute_along_arc(cx=960, cy=540, radius=300, start_angle=0, end_angle=360, start=0)

      Place children along an arc.

   .. py:method:: distribute_radial(cx=None, cy=None, radius=200, start_angle=0, start=0, end=None, easing=smooth)

      Arrange children in a circle around (cx, cy). Defaults to group center. With end, animates.

   .. admonition:: Example: distribute_radial
      :class: example

      .. raw:: html

         <img src="../_static/videos/ref_distribute_radial.svg" style="width:100%;max-width:800px;display:block;margin:auto;" />

      .. literalinclude:: ../../../examples/reference/ref_distribute_radial.py
         :language: python

   .. py:method:: stagger_scale(start=0, end=1, scale_factor=1.5, delay=0.2, easing=smooth)

      Scale each child up then back down with stagger delay (popping wave).

   .. py:method:: connect_children(arrow=False, buff=0, start=0, **kwargs)

      Draw connecting lines (or arrows) between consecutive children.

   .. py:method:: batch_animate(method_name, args_list, start=0, delay=0.1)

      Call a method on each child with per-child arguments.

----

MorphObject
~~~~~~~~~~~

.. py:class:: MorphObject(morph_from, morph_to, start=0, end=1, easing=smooth, change_existence=True, rotation_degrees=0)

   Bases: :py:class:`VCollection`

   Smoothly morph one shape (or collection) into another.

   :param morph_from: Source shape.
   :param morph_to: Target shape.
   :param float start: Start time.
   :param float end: End time.
   :param float rotation_degrees: Spiral morph rotation (0 = straight morph).

   .. admonition:: Example: MorphObject
      :class: example

      .. raw:: html

         <video src="../_static/videos/ref_morph.mp4" controls autoplay loop muted></video>

      .. literalinclude:: ../../../examples/reference/ref_morph.py
         :language: python

   .. admonition:: Example: MorphObject (collection to collection)
      :class: example

      .. raw:: html

         <video src="../_static/videos/ref_morph2.mp4" controls autoplay loop muted style="width:100%;max-width:800px;display:block;margin:auto;"></video>

      .. literalinclude:: ../../../examples/reference/ref_morph2.py
         :language: python

   .. admonition:: Example: MorphObject with scale
      :class: example

      .. raw:: html

         <video src="../_static/videos/ref_morph_scale.mp4" controls autoplay loop muted style="width:100%;max-width:800px;display:block;margin:auto;"></video>

      .. literalinclude:: ../../../examples/reference/ref_morph_scale.py
         :language: python

----

LabeledDot
~~~~~~~~~~~

.. py:class:: LabeledDot(label='', r=24, cx=960, cy=540, font_size=None, **styling)

   Bases: :py:class:`VCollection`

   A dot with a centred text label.

   .. py:attribute:: dot
      :type: Dot

   .. py:attribute:: label
      :type: Text

----

Arrows
------

Arrow
~~~~~

.. image:: ../_static/images/arrow_params.svg
   :width: 440
   :align: center

.. py:class:: Arrow(x1=0, y1=0, x2=100, y2=100, tip_length=47, tip_width=47, **styling)

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

   .. admonition:: Example: Arrow
      :class: example

      .. raw:: html

         <img src="../_static/videos/ref_arrow.svg" style="width:100%; max-width:800px;" />

      .. literalinclude:: ../../../examples/reference/ref_arrow.py
         :language: python

----

Vector
~~~~~~

.. py:class:: Vector(x=100, y=0, origin_x=960, origin_y=540, **styling)

   Bases: :py:class:`Arrow`

   Arrow originating from a point (default: canvas origin). Commonly used in
   coordinate systems to represent mathematical vectors.

   :param float x: Horizontal component (pixels from origin).
   :param float y: Vertical component (pixels from origin).
   :param float origin_x: Starting x position (default ``960``).
   :param float origin_y: Starting y position (default ``540``).

   .. py:method:: get_vector(time=0)

      Return the vector components ``(dx, dy)`` from start to end.

   .. admonition:: Example: Creating a vector on axes
      :class: example

      .. code-block:: python

         from vectormation.objects import *

         axes = Axes(x_range=(-3, 3), y_range=(-3, 3))
         v = Vector(x=2 * 135, y=-1 * 135)   # 2 units right, 1 unit down
         v.fadein(0, 1)

   .. admonition:: Example: Vector on Axes
      :class: example

      .. raw:: html

         <img src="../_static/videos/ref_vector_on_axes.svg" style="width:100%;max-width:800px;display:block;margin:auto;" />

      .. literalinclude:: ../../../examples/reference/ref_vector_on_axes.py
         :language: python

----

DoubleArrow
~~~~~~~~~~~

.. py:class:: DoubleArrow(x1=0, y1=0, x2=100, y2=100, tip_length=47, tip_width=47, **styling)

   Bases: :py:class:`Arrow`

   Arrow with heads on both ends.

   .. admonition:: Example: DoubleArrow
      :class: example

      .. raw:: html

         <img src="../_static/videos/ref_double_arrow.svg" style="width:100%; max-width:800px;" />

      .. literalinclude:: ../../../examples/reference/ref_double_arrow.py
         :language: python

----

CurvedArrow
~~~~~~~~~~~

.. image:: ../_static/images/curved_arrow_params.svg
   :width: 440
   :align: center

.. py:class:: CurvedArrow(x1=0, y1=0, x2=100, y2=100, angle=0.4, tip_length=47, tip_width=47, **styling)

   Bases: :py:class:`VCollection`

   Arrow with a quadratic Bezier curve shaft.

   :param float angle: Curvature angle.

   .. admonition:: Example: CurvedArrow
      :class: example

      .. raw:: html

         <img src="../_static/videos/ref_curved_arrow.svg" style="width:100%; max-width:800px;" />

      .. literalinclude:: ../../../examples/reference/ref_curved_arrow.py
         :language: python

----

Brace
~~~~~

.. image:: ../_static/images/brace_params.svg
   :width: 400
   :align: center

.. py:class:: Brace(target, direction='down', label=None, buff=14, depth=18, **styling)

   Bases: :py:class:`VCollection`

   Curly brace annotation around a target object.

   :param target: The object to annotate.
   :param str direction: ``'up'``, ``'down'``, ``'left'``, or ``'right'``.
   :param str label: Optional text label.
   :param float buff: Distance from target.
   :param float depth: Brace depth.

   .. py:classmethod:: for_range(axes, axis, start_val, end_val, direction=None, label=None, **kwargs)

      Create a Brace spanning a range on an Axes object.

      :param axes: The Axes object.
      :param str axis: ``'x'`` or ``'y'``.
      :param float start_val: Start of the range.
      :param float end_val: End of the range.

   .. admonition:: Example: Brace
      :class: example

      .. raw:: html

         <img src="../_static/videos/ref_brace.svg" style="width:100%; max-width:800px;" />

      .. literalinclude:: ../../../examples/reference/ref_brace.py
         :language: python

----

BraceBetweenPoints
~~~~~~~~~~~~~~~~~~

.. py:class:: BraceBetweenPoints(x1, y1, x2, y2, label=None, buff=14, depth=18, **styling)

   Bases: :py:class:`Brace`

   Curly brace between two arbitrary points. The brace spans the line
   segment from ``(x1, y1)`` to ``(x2, y2)``, with the tip pointing
   perpendicular to the segment.

   :param float x1: Start x-coordinate.
   :param float y1: Start y-coordinate.
   :param float x2: End x-coordinate.
   :param float y2: End y-coordinate.
   :param str label: Optional text label.
   :param float buff: Distance from segment.
   :param float depth: Brace depth.

   .. admonition:: Example: Brace spanning two points
      :class: example

      .. code-block:: python

         brace = BraceBetweenPoints(300, 400, 800, 400, label='500px')

----

LabeledLine
~~~~~~~~~~~

.. py:class:: LabeledLine(x1, y1, x2, y2, label='', **styling)
   :no-index:

   Bases: :py:class:`VCollection`

   A line with a text label positioned at its midpoint.

   .. admonition:: Example: LabeledLine
      :class: example

      .. raw:: html

         <img src="../_static/videos/ref_labeled_line.svg" style="width:100%;max-width:800px;display:block;margin:auto;" />

      .. literalinclude:: ../../../examples/reference/ref_labeled_line.py
         :language: python

----

LabeledArrow
~~~~~~~~~~~~~

.. py:class:: LabeledArrow(x1, y1, x2, y2, label='', **styling)
   :no-index:

   Bases: :py:class:`VCollection`

   An arrow with a text label positioned at its midpoint.

   .. admonition:: Example: LabeledArrow
      :class: example

      .. raw:: html

         <img src="../_static/videos/ref_labeled_arrow.svg" style="width:100%;max-width:800px;display:block;margin:auto;" />

      .. literalinclude:: ../../../examples/reference/ref_labeled_arrow.py
         :language: python

----

Data Structures
---------------

Array
~~~~~

.. py:class:: Array(values, x=360, y=440, cell_width=80, cell_height=60, font_size=24, show_indices=True, **styling)

   Bases: :py:class:`VCollection`

   Array visualization with cells, index labels, and animation methods.

   .. py:method:: highlight_cell(index, start=0, end=1, color='#58C4DD', easing=there_and_back)

      Flash-highlight a cell by index.

   .. py:method:: swap_cells(i, j, start=0, end=1, easing=smooth)

      Animate swapping the values at indices *i* and *j*.

   .. py:method:: set_value(index, value, start=0, end=0.5)

      Animate changing a cell's displayed value.

   .. py:method:: sort(start=0, end=2, easing=smooth, delay=0.15)

      Animate a bubble sort, staggering swaps over ``[start, end]``.

   .. py:method:: reverse(start=0, end=2, easing=smooth, delay=0.15)

      Animate reversing the array by swapping from outside in.

   .. py:method:: add_pointer(index, label='', color='#FF6B6B', creation=0)

      Add a pointer arrow above a cell.

   .. admonition:: Example: Array
      :class: example

      .. raw:: html

         <video src="../_static/videos/array.mp4" controls autoplay loop muted></video>

      Array highlight and swap operations.

      .. literalinclude:: ../../../examples/reference/array_example.py
         :language: python

Stack
~~~~~

.. py:class:: Stack(values=None, x=860, y=600, cell_width=100, cell_height=50, **styling)

   Bases: :py:class:`VCollection`

   Visual stack (LIFO) with push/pop animations.

   .. py:method:: push(value, start=0, end=0.5)

      Animate pushing a value onto the stack.

   .. py:method:: pop(start=0, end=0.5)

      Animate popping the top value.

   .. py:method:: peek()

      Return the top value without removing it.

Queue
~~~~~

.. py:class:: Queue(values=None, x=360, y=440, cell_width=80, cell_height=60, **styling)

   Bases: :py:class:`VCollection`

   Visual queue (FIFO) with enqueue/dequeue animations.

   .. py:method:: enqueue(value, start=0, end=0.5)

      Animate adding a value to the back.

   .. py:method:: dequeue(start=0, end=0.5)

      Animate removing the front value.

LinkedList
~~~~~~~~~~

.. py:class:: LinkedList(values, x=200, y=440, node_width=80, node_height=50, gap=40, font_size=22, fill='#1e1e2e', text_color='#fff', border_color='#58C4DD', arrow_color='#fff')

   Bases: :py:class:`VCollection`

   Visual singly linked list with node and arrow animations.

   :param list values: Initial node values (required).
   :param float node_width: Width of each node box.
   :param float node_height: Height of each node box.
   :param float gap: Horizontal gap between nodes.

   .. py:method:: append_node(value, start=0, end=0.5)

      Animate appending a new node at the end of the list.

   .. py:method:: remove_node(index, start=0, end=0.5)

      Animate removing the node at *index*.

   .. py:method:: highlight_node(index, start=0, end=1, color='#FF6B6B')

      Flash-highlight a node by index.

ArrayViz
~~~~~~~~

.. py:class:: ArrayViz(values, cell_size=80, x=None, y=None, colors=None, default_fill='#264653', show_indices=True, font_size=32, **styling)

   Bases: :py:class:`VCollection`

   Visualise an array as a row of labeled cells. Supports animated swaps,
   highlights, and value changes.

   :param list values: Initial values to display.
   :param float cell_size: Width and height of each cell.

   .. py:method:: highlight(index, color='#E9C46A', start=0, end=0.5)

      Temporarily highlight a cell.

   .. py:method:: swap(i, j, start=0, end=0.5)

      Animate swapping two cells.

   .. py:method:: set_value(index, value, start=0, end=0.5)

      Animate changing a cell's value.

   .. py:method:: pointer(index, label='', start=0, color='#FC6255')

      Add a labelled pointer arrow above a cell.

LinkedListViz
~~~~~~~~~~~~~

.. py:class:: LinkedListViz(values, cell_width=80, cell_height=50, x=None, y=None, **styling)

   Bases: :py:class:`VCollection`

   Visualise a singly linked list with boxes and arrows.

   :param list values: Initial node values.

   .. py:method:: highlight(index, color='#E9C46A', start=0, end=0.5)

      Temporarily highlight a node.

   .. py:method:: traverse(start=0, delay=0.3, color='#E9C46A')

      Animate traversal through all nodes sequentially.

StackViz
~~~~~~~~

.. py:class:: StackViz(values, cell_width=120, cell_height=50, x=None, y=None, **styling)

   Bases: :py:class:`VCollection`

   Visualise a stack (LIFO) as vertically stacked cells with a TOP pointer.

   :param list values: Initial values (bottom to top).

   .. py:method:: push(value, start=0, end=0.5)

      Animate pushing a value onto the stack.

   .. py:method:: pop(start=0, end=0.5)

      Animate popping the top value.

QueueViz
~~~~~~~~

.. py:class:: QueueViz(values, cell_width=80, cell_height=60, x=None, y=None, **styling)

   Bases: :py:class:`VCollection`

   Visualise a queue (FIFO) as a horizontal row of cells with FRONT/BACK labels.

   :param list values: Initial values (front on the left).

   .. py:method:: enqueue(value, start=0, end=0.5)

      Animate adding a value to the back of the queue.

   .. py:method:: dequeue(start=0, end=0.5)

      Animate removing the front value.

   .. py:method:: highlight(index, color='#E9C46A', start=0, end=0.5)

      Temporarily highlight a cell.

BinaryTree
~~~~~~~~~~

.. py:class:: BinaryTree(tree, x=960, y=120, h_spacing=200, v_spacing=100, **styling)

   Bases: :py:class:`VCollection`

   Visual binary tree with automatic layout.

   :param tuple tree: Nested tuple ``(value, left_subtree, right_subtree)``.

   .. py:method:: highlight_node(index, color='#E9C46A', start=0, end=0.5)

      Temporarily highlight a node by depth-first index.

----

Table
~~~~~

.. py:class:: Table(data, row_labels=None, col_labels=None, x=120, y=60, cell_width=160, cell_height=60, font_size=24, **styling)

   Bases: :py:class:`VCollection`

   Tabular data display with optional row/column labels.

   :param list data: 2D list of values ``data[row][col]``.

   .. py:method:: get_entry(row, col)

      Return the Text object at ``(row, col)``.

   .. py:method:: get_row(row)

      Return a VCollection of all Text objects in a row.

   .. py:method:: get_column(col)

      Return a VCollection of all Text objects in a column.

   .. py:method:: highlight_cell(row, col, start=0, end=1, color='#FFFF00')

      Flash-highlight a single cell.

   .. py:method:: highlight_row(row_idx, start=0, end=1, color='#FFFF00', opacity=0.3)

      Highlight all cells in a row.

   .. admonition:: Example: Table
      :class: example

      .. raw:: html

         <img src="../_static/videos/ref_table.svg" style="width:100%; max-width:800px;" />

      .. literalinclude:: ../../../examples/reference/ref_table.py
         :language: python

Matrix
~~~~~~

.. py:class:: Matrix(data, x=960, y=540, font_size=36, h_spacing=80, v_spacing=50, **styling)

   Bases: :py:class:`VCollection`

   Mathematical matrix with bracket delimiters.

   :param list data: 2D list of values.

   .. py:method:: get_entry(row, col)

      Return the Text object at ``(row, col)``.

   .. py:method:: get_row(row)

      Return a VCollection of all entries in a row.

   .. py:method:: get_column(col)

      Return a VCollection of all entries in a column.

   .. py:method:: highlight_row(row, start=0, end=1, color='#FFD700')

      Flash-highlight all entries in a row.

   .. py:method:: highlight_column(col, start=0, end=1, color='#FFD700')

      Flash-highlight all entries in a column.

   .. admonition:: Example: Matrix
      :class: example

      .. raw:: html

         <img src="../_static/videos/ref_matrix.svg" style="width:100%; max-width:800px;" />

      .. literalinclude:: ../../../examples/reference/ref_matrix.py
         :language: python

DecimalMatrix
~~~~~~~~~~~~~

.. py:class:: DecimalMatrix(data, decimals=1, **kwargs)

   Bases: :py:class:`Matrix`

   Matrix that formats entries as decimals with a fixed number of places.

   :param list data: 2D list of numeric values.
   :param int decimals: Number of decimal places (default ``1``).

   .. admonition:: Example: Matrix with fixed decimal places
      :class: example

      .. code-block:: python

         m = DecimalMatrix([[1.234, 5.678], [9.012, 3.456]], decimals=2)

IntegerMatrix
~~~~~~~~~~~~~

.. py:class:: IntegerMatrix(data, **kwargs)

   Bases: :py:class:`Matrix`

   Matrix that formats entries as integers (values are rounded).

   :param list data: 2D list of numeric values.

   .. admonition:: Example: Matrix with integer-rounded entries
      :class: example

      .. code-block:: python

         m = IntegerMatrix([[1.7, 2.3], [3.9, 4.1]])
         # Displays: [[2, 2], [4, 4]]

Code
~~~~

.. py:class:: Code(text, language='python', x=100, y=80, font_size=24, **styling)

   Bases: :py:class:`VCollection`

   Syntax-highlighted code display.

   :param str text: Source code string.
   :param str language: Programming language for highlighting.

   .. py:method:: highlight_lines(line_numbers, color='#FFFF00', opacity=0.3, start=0, end=1)

      Highlight specific line numbers with a background colour.

   .. py:method:: reveal_lines(start=0, end=1, overlap=0.5)

      Reveal code lines sequentially with staggered fadein.

Title
~~~~~

.. py:class:: Title(text, **styling)

   Bases: :py:class:`VCollection`

   Centered title text at the top of the canvas with an underline.

Variable
~~~~~~~~

.. py:class:: Variable(label, value=0, fmt='{:.2f}', x=960, y=540, font_size=48, **styling)

   Bases: :py:class:`VCollection`

   A labelled numeric value display (e.g. ``x = 3.14``).

   .. py:method:: set_value(val, start=0)

      Set the value instantly.

   .. py:method:: animate_value(target, start, end, easing=smooth)

      Animate to a target value.

   .. py:attribute:: tracker

      The underlying Real attribute for the displayed value.

DynamicObject
~~~~~~~~~~~~~

.. py:class:: DynamicObject(func, creation=0, z=0)

   Bases: :py:class:`VObject`

   VObject whose SVG is regenerated every frame by calling ``func(time)``.
   The function should return a VObject.

   .. admonition:: Example: Rebuilding SVG every frame
      :class: example

      .. code-block:: python

         def my_clock(time):
             angle = time * 360
             hand = Line(960, 540, 960 + 100 * math.cos(math.radians(angle)),
                         540 + 100 * math.sin(math.radians(angle)))
             return hand

         clock = DynamicObject(my_clock)

.. py:function:: always_redraw(func, creation=0, z=0)

   Convenience wrapper: create a :py:class:`DynamicObject` from a callable.
   ``func(time)`` should return a VObject.

   .. admonition:: Example: Line that follows a moving dot
      :class: example

      .. code-block:: python

         dot = Dot()
         dot.shift(dx=200, start=0, end=2)

         line = always_redraw(lambda t: Line(960, 540, *dot.center(t)))

.. seealso::

   Additional VCollection-based classes are documented in their dedicated
   reference pages:

   - :doc:`graphing` — Axes, Graph, NumberPlane, ComplexPlane, PolarAxes, NumberLine
   - :doc:`charts` — PieChart, BarChart, DonutChart, RadarChart, Legend, ProgressBar, and more
   - :doc:`diagrams` — NetworkGraph, FlowChart, Tree, Automaton, and more
   - :doc:`ui` — Label, Callout, DimensionLine, Tooltip, Code, Title, Variable, and more
   - :doc:`science` — NeuralNetwork, Pendulum, StandingWave, Molecule2D, Lens, Ray
