Diagrams
========

Diagram and domain-specific visualization classes. All inherit from
:py:class:`VCollection` and support the full set of animation methods.

----

ChessBoard
----------

.. py:class:: ChessBoard(fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR', cx=960, cy=540, size=600, show_coordinates=True, light_color='#f0d9b5', dark_color='#b58863', creation=0, z=0)

   Chess board visualization with pieces from a FEN string. Pieces are
   rendered as Unicode symbols.

   :param str fen: Piece placement in FEN notation (rows separated by ``/``).
   :param float size: Board side length in pixels.
   :param bool show_coordinates: Show file (a--h) and rank (1--8) labels.

   .. py:method:: move_piece(from_sq, to_sq, start=0, end=1, easing=smooth)

      Animate moving a piece from one square to another using algebraic
      notation (e.g. ``'e2'`` to ``'e4'``).

   .. code-block:: python

      board = ChessBoard()
      board.move_piece('e2', 'e4', start=0, end=1)
      board.move_piece('e7', 'e5', start=1, end=2)

----

PeriodicTable
-------------

.. py:class:: PeriodicTable(cx=960, cy=540, cell_size=48, creation=0, z=0)

   Periodic table of elements (first 36 elements) with color-coded
   categories (nonmetal, noble gas, alkali, alkaline earth, metalloid,
   halogen, transition metal, post-transition metal).

   :param float cell_size: Size of each element cell.

   .. py:method:: highlight(symbol, start=0, end=1, color='#FFFF00', easing=there_and_back)

      Highlight an element by its chemical symbol (e.g. ``'Fe'``).

----

BohrAtom
--------

.. py:class:: BohrAtom(protons=1, neutrons=0, electrons=None, cx=960, cy=540, nucleus_r=30, shell_spacing=40, creation=0, z=0)

   Bohr model of an atom with a nucleus and electron shells. If *electrons*
   is ``None``, shells are auto-filled (2, 8, 8, 18, ...).

   :param int protons: Number of protons (shown in the nucleus).
   :param int neutrons: Number of neutrons.
   :param list electrons: List of electron counts per shell, or ``None`` for auto.
   :param float nucleus_r: Radius of the nucleus circle.
   :param float shell_spacing: Spacing between concentric orbit rings.

   .. py:method:: orbit(start=0, end=None, speed=45)

      Animate all electrons orbiting the nucleus.

   .. code-block:: python

      carbon = BohrAtom(protons=6, neutrons=6)
      carbon.orbit(start=0, end=5)

----

Automaton
---------

.. py:class:: Automaton(states, transitions, accept_states=None, initial_state=None, cx=960, cy=540, radius=300, state_r=35, font_size=20, creation=0, z=0)

   Finite state machine / automaton visualization. States are arranged in a
   circle; transitions are drawn as arrows (or arcs for self-loops).

   :param list states: List of state name strings.
   :param list transitions: List of ``(from_state, to_state, label)`` tuples.
   :param set accept_states: Set of state names drawn with a double circle.
   :param str initial_state: State that receives an entry arrow.

   .. py:method:: highlight_state(state_name, start=0, end=1, color='#FFFF00', easing=there_and_back)

      Flash-highlight a state by name.

   .. code-block:: python

      dfa = Automaton(
          states=['q0', 'q1', 'q2'],
          transitions=[('q0', 'q1', 'a'), ('q1', 'q2', 'b'), ('q2', 'q0', 'c')],
          accept_states={'q2'},
          initial_state='q0',
      )

----

NetworkGraph
------------

.. py:class:: NetworkGraph(nodes, edges=None, cx=960, cy=540, radius=300, node_r=30, font_size=20, layout='circular', directed=False, creation=0, z=0)

   Network/graph visualization with labeled nodes and edges.

   :param nodes: A list of labels (indexed 0, 1, ...) or a ``{id: label}`` dict.
   :param list edges: List of ``(from_id, to_id)`` or ``(from_id, to_id, label)`` tuples.
   :param str layout: ``'circular'``, ``'grid'``, or ``'spring'`` (force-directed).
   :param bool directed: Draw edges as arrows when ``True``.

   .. py:method:: highlight_node(node_id, start=0, end=1, color='#FFFF00', easing=there_and_back)

      Flash-highlight a node by ID.

   .. py:method:: get_node_position(node_id)

      Return the ``(x, y)`` position of a node.

   .. code-block:: python

      graph = NetworkGraph(
          nodes=['A', 'B', 'C', 'D'],
          edges=[(0, 1), (1, 2), (2, 3), (3, 0)],
          layout='spring',
      )

----

Tree
----

.. py:class:: Tree(data, cx=960, cy=100, h_spacing=120, v_spacing=100, node_r=20, font_size=18, layout='down', creation=0, z=0)

   Hierarchical tree layout visualization. Data is a nested tuple
   ``(label, [children])`` or a dictionary.

   :param data: Tree structure as ``(label, [child_tuples, ...])`` or a nested dict.
   :param float h_spacing: Minimum horizontal spacing between siblings.
   :param float v_spacing: Vertical spacing between levels.
   :param str layout: ``'down'`` (root at top) or ``'right'`` (root at left).

   .. py:method:: get_node_position(label)

      Return the ``(x, y)`` position of a node by label.

   .. py:method:: highlight_node(label, start=0, end=1, color='#FFFF00', easing=there_and_back)

      Flash-highlight a node by label.

   .. code-block:: python

      tree = Tree(('root', [
          ('A', [('A1', []), ('A2', [])]),
          ('B', [('B1', [])]),
      ]))

----

Stamp
-----

.. py:class:: Stamp(template, points, creation=0, z=0)

   Place deep copies of a template object at specified positions.

   :param VObject template: Object to copy.
   :param list points: List of ``(x, y)`` positions for each copy.

----

TimelineBar
-----------

.. py:class:: TimelineBar(markers, total_duration=10, x=200, y=900, width=1520, height=6, marker_color='#FFFF00', font_size=14, creation=0, z=0)

   Horizontal timeline bar with labeled markers at specific times.

   :param dict markers: ``{time_value: label_text}`` dictionary.
   :param float total_duration: Total timeline duration (determines scale).

   .. code-block:: python

      tl = TimelineBar({0: 'Start', 3: 'Midpoint', 10: 'End'},
                       total_duration=10)

----

FlowChart
---------

.. py:class:: FlowChart(steps, direction='right', x=200, y=400, box_width=200, box_height=60, spacing=80, box_color='#58C4DD', text_color='#fff', arrow_color='#999', font_size=20, corner_radius=8, creation=0, z=0)

   Simple flow chart with labeled boxes connected by arrows.

   :param list steps: List of step label strings.
   :param str direction: ``'right'`` (horizontal) or ``'down'`` (vertical).

   .. code-block:: python

      flow = FlowChart(['Input', 'Process', 'Output'])

----

VennDiagram
-----------

.. py:class:: VennDiagram(labels, sizes=None, x=960, y=540, radius=150, colors=None, font_size=24, creation=0, z=0)

   Venn diagram with 2 or 3 overlapping semi-transparent circles.

   :param list labels: 2 or 3 set labels.
   :param list sizes: Per-circle radii (defaults to *radius* for all).

----

OrgChart
--------

.. py:class:: OrgChart(root, x=960, y=80, h_spacing=180, v_spacing=100, box_width=120, box_height=40, font_size=16, colors=None, creation=0, z=0)

   Organization chart from a tree structure. Nodes are styled boxes
   connected by L-shaped connectors, with colors varying by depth level.

   :param root: Tree structure as ``(label, [children])`` tuples.
   :param float h_spacing: Horizontal spacing between boxes.
   :param float v_spacing: Vertical spacing between levels.

   .. code-block:: python

      org = OrgChart(('CEO', [
          ('CTO', [('Dev Lead', []), ('QA Lead', [])]),
          ('CFO', [('Accounting', [])]),
      ]))

----

MindMap
-------

.. py:class:: MindMap(root, cx=960, cy=540, radius=250, font_size=18, colors=None, creation=0, z=0)

   Radial mind map diagram with a central node, branches, and
   grandchildren spread outward.

   :param root: Tree structure as ``(label, [(child_label, [grandchildren]), ...])`` tuples.
   :param float radius: Distance from center to branch nodes.
