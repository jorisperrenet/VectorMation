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

   .. image:: ../_static/images/arrange.svg
      :width: 500
      :align: center

   .. py:method:: arrange(direction='right', buff=14, start=0)

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

   .. py:method:: distribute_radial(cx=960, cy=540, radius=300, start=0)

      Place children in a circle.

   .. py:method:: space_evenly(direction='right', total_span=None, start=0)

      Space children evenly along an axis.

   .. py:method:: spread(x1, y1, x2, y2, start=0)

      Distribute children evenly between two points.

   .. py:method:: align_submobjects(edge='left', start=0)

      Align all children's edges.

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

   .. py:method:: reveal(start=0, end=1, direction='left', easing=smooth)

      Staggered reveal of children sliding into view.

   .. py:method:: stagger_fadein(start=0, end=1, shift_dir=None, shift_amount=50, overlap=0.5, easing=smooth)

      Staggered fade-in of children with optional directional shift.

   .. py:method:: wave_anim(start=0, end=1, amplitude=20, waves=1)

      Wave animation through children.

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

   .. py:method:: fan_out(cx=960, cy=540, radius=300, start_angle=-45, end_angle=45, start=0)

      Spread children in a fan pattern.

   .. py:method:: cascade_fadein(start=0, delay=0.15, duration=0.5, easing=smooth)

      Staggered fade-in of children with delay.

   .. py:method:: connect_children(start=0, stroke='#fff', stroke_width=2)

      Draw lines connecting consecutive children.

   .. py:method:: batch_animate(method_name, args_list, start=0, delay=0.1)

      Call a method on each child with per-child arguments.

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

----

DoubleArrow
-----------

.. py:class:: DoubleArrow(x1=0, y1=0, x2=100, y2=100, tip_length=47, tip_width=47, **styling)

   Bases: :py:class:`Arrow`

   Arrow with heads on both ends.

----

CurvedArrow
------------

.. image:: ../_static/images/curved_arrow_params.svg
   :width: 440
   :align: center

.. py:class:: CurvedArrow(x1=0, y1=0, x2=100, y2=100, angle=0.4, tip_length=47, tip_width=47, **styling)

   Bases: :py:class:`VCollection`

   Arrow with a quadratic Bezier curve shaft.

   :param float angle: Curvature angle.

----

Brace
-----

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

----

Data Structures
---------------

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

NetworkGraph
~~~~~~~~~~~~

.. py:class:: NetworkGraph(nodes, edges, x=960, y=540, node_radius=25, **styling)

   Bases: :py:class:`VCollection`

   Graph/network diagram with automatic force-directed layout.

   :param list nodes: List of node labels.
   :param list edges: List of ``(from, to)`` or ``(from, to, label)`` tuples.

   .. py:method:: highlight_node(node, color='#E9C46A', start=0, end=0.5)

      Temporarily highlight a node.

   .. py:method:: highlight_edge(from_node, to_node, color='#E76F51', start=0, end=0.5)

      Temporarily highlight an edge.

NeuralNetwork
~~~~~~~~~~~~~

.. py:class:: NeuralNetwork(layers, x=960, y=540, node_radius=15, h_spacing=200, v_spacing=50, **styling)

   Bases: :py:class:`VCollection`

   Neural network diagram with layers of nodes and weighted connections.

   :param list layers: List of integers giving the number of nodes per layer.

   .. py:method:: activate(layer, node, start=0, end=0.5, color='#E9C46A')

      Highlight a specific neuron.

----

Circuit Components
~~~~~~~~~~~~~~~~~~

.. py:class:: Resistor(x1=860, y1=540, x2=1060, y2=540, **styling)

   Bases: :py:class:`VCollection`

   Resistor symbol (zigzag).

.. py:class:: Capacitor(x1=860, y1=540, x2=1060, y2=540, **styling)

   Bases: :py:class:`VCollection`

   Capacitor symbol (two parallel plates).

.. py:class:: Inductor(x1=860, y1=540, x2=1060, y2=540, **styling)

   Bases: :py:class:`VCollection`

   Inductor symbol (coil).

.. py:class:: Diode(x1=860, y1=540, x2=1060, y2=540, **styling)

   Bases: :py:class:`VCollection`

   Diode symbol (triangle + line).

.. py:class:: LED(x1=860, y1=540, x2=1060, y2=540, **styling)

   Bases: :py:class:`VCollection`

   LED symbol (diode with arrows).

----

Physics
~~~~~~~

.. py:class:: Pendulum(length=200, angle=30, x=960, y=200, start=0, end=5, damping=0.98, **styling)

   Bases: :py:class:`VCollection`

   Animated pendulum with damped oscillation.

.. py:class:: StandingWave(n=3, width=600, amplitude=80, x=660, y=540, start=0, end=3, frequency=1, **styling)

   Bases: :py:class:`VCollection`

   Animated standing wave with *n* antinodes.

.. py:class:: Molecule2D(atoms, bonds, x=960, y=540, scale=100, **styling)

   Bases: :py:class:`VCollection`

   2D molecular structure diagram.

   :param list atoms: List of ``(element, x, y)`` tuples.
   :param list bonds: List of ``(atom_idx1, atom_idx2)`` or ``(atom_idx1, atom_idx2, order)`` tuples.

.. py:class:: UnitInterval(x_range=(0, 1, 0.25), **kwargs)

   Bases: :py:class:`NumberLine`

   A NumberLine pre-configured for the unit interval [0, 1].

SampleSpace
~~~~~~~~~~~~

.. py:class:: SampleSpace(width=600, height=400, x=660, y=340, **styling)

   Bases: :py:class:`VCollection`

   Rectangular probability sample space diagram.

----

Legend
~~~~~~

.. py:class:: Legend(items, x=None, y=None, **styling)

   Bases: :py:class:`VCollection`

   Chart legend with coloured swatches and labels.

   :param list items: List of ``(color, label)`` tuples.

ProgressBar
~~~~~~~~~~~

.. py:class:: ProgressBar(width=600, height=40, progress=0, x=660, y=520, **styling)

   Bases: :py:class:`VCollection`

   Animated progress bar that fills from left to right.

   .. py:method:: animate_to(value, start=0, end=1)

      Animate progress to a target value (0–1).

FlowChart
~~~~~~~~~

.. py:class:: FlowChart(steps, x=None, y=540, direction='right', **styling)

   Bases: :py:class:`VCollection`

   Flow chart with labelled boxes connected by arrows.

   :param list steps: List of string labels for each box.

----

Annotations
-----------

Label
~~~~~

.. py:class:: Label(text, x=960, y=540, font_size=36, padding=10, **styling)

   Bases: :py:class:`VCollection`

   Text label with a surrounding box/frame.

Callout
~~~~~~~

.. py:class:: Callout(text, target, x=None, y=None, **styling)

   Bases: :py:class:`VCollection`

   Text callout with a pointer line to a target position.

DimensionLine
~~~~~~~~~~~~~

.. py:class:: DimensionLine(p1, p2, label='', **styling)

   Bases: :py:class:`VCollection`

   Technical dimension line between two points with measurement label.

   :param tuple p1: Start ``(x, y)`` point.
   :param tuple p2: End ``(x, y)`` point.
   :param str label: Measurement text.

Tooltip
~~~~~~~

.. py:class:: Tooltip(text, target, start=0, end=1, **styling)

   Bases: :py:class:`VCollection`

   Small animated tooltip that appears near a target.
