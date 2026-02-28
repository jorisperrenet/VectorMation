Diagrams
========

Diagram and domain-specific visualization classes. All inherit from
:py:class:`VCollection` and support the full set of animation methods.

.. code-block:: python

   from vectormation.objects import *

----

ChessBoard
----------

.. py:class:: ChessBoard(fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR', cx=960, cy=540, size=600, show_coordinates=True, light_color='#f0d9b5', dark_color='#b58863', creation=0, z=0)

   Chess board visualization with pieces from a FEN string. The board is
   drawn as an 8x8 grid of alternating light and dark squares, with pieces
   rendered as Unicode chess symbols. White pieces are displayed in white
   (``#fff``), black pieces in dark grey (``#222``).

   :param str fen: Piece placement in FEN notation (rows separated by ``/``).
      Only the piece-placement portion of FEN is used. Digits represent
      empty squares. Default is the standard starting position.
   :param float cx: Center x-coordinate of the board.
   :param float cy: Center y-coordinate of the board.
   :param float size: Board side length in pixels. Each cell is ``size / 8``
      pixels.
   :param bool show_coordinates: Show file (a--h) and rank (1--8) labels
      around the board edges.
   :param str light_color: Fill color for light squares.
   :param str dark_color: Fill color for dark squares.
   :param float creation: Creation time.
   :param float z: Z-index for layering.

   .. py:method:: move_piece(from_sq, to_sq, start=0, end=1, easing=smooth)

      Animate moving a piece from one square to another using algebraic
      notation (e.g. ``'e2'`` to ``'e4'``). The piece is shifted in pixel
      space based on the difference in file and rank. The internal piece
      mapping is updated so subsequent moves reference the new square.

      :param str from_sq: Source square in algebraic notation (e.g. ``'e2'``).
      :param str to_sq: Target square in algebraic notation (e.g. ``'e4'``).
      :param float start: Animation start time.
      :param float end: Animation end time.
      :param easing: Easing function.

   .. code-block:: python

      board = ChessBoard()
      board.move_piece('e2', 'e4', start=0, end=1)
      board.move_piece('e7', 'e5', start=1, end=2)

   A custom position using FEN notation:

   .. code-block:: python

      # Fool's Mate final position
      board = ChessBoard(
          fen='rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR',
          size=500,
          show_coordinates=True,
      )

----

PeriodicTable
-------------

.. py:class:: PeriodicTable(cx=960, cy=540, cell_size=48, creation=0, z=0)

   Periodic table of elements (first 36 elements, hydrogen through krypton)
   with color-coded categories. Each element cell shows its atomic number and
   chemical symbol. Categories and their colors:

   ==================== ===========
   Category             Color
   ==================== ===========
   Nonmetal             ``#58C4DD``
   Noble gas            ``#9A72AC``
   Alkali metal         ``#FC6255``
   Alkaline earth metal ``#F0AC5F``
   Metalloid            ``#5CD0B3``
   Halogen              ``#FFFF00``
   Transition metal     ``#C55F73``
   Post-transition      ``#83C167``
   ==================== ===========

   :param float cx: Center x-coordinate of the table.
   :param float cy: Center y-coordinate of the table.
   :param float cell_size: Size of each element cell in pixels.
   :param float creation: Creation time.
   :param float z: Z-index for layering.

   .. py:method:: highlight(symbol, start=0, end=1, color='#FFFF00', easing=there_and_back)

      Highlight an element by its chemical symbol. The cell background is
      indicated (scale pulse) and the symbol text flashes in the given color.

      :param str symbol: Chemical symbol (e.g. ``'Fe'``, ``'O'``, ``'He'``).
      :param float start: Animation start time.
      :param float end: Animation end time.
      :param str color: Flash color for the symbol text.
      :param easing: Easing function.

   .. code-block:: python

      table = PeriodicTable()
      table.highlight('Fe', start=0, end=1.5)
      table.highlight('O', start=1, end=2.5)

----

BohrAtom
--------

.. py:class:: BohrAtom(protons=1, neutrons=0, electrons=None, cx=960, cy=540, nucleus_r=30, shell_spacing=40, creation=0, z=0)

   Bohr model of an atom with a nucleus and concentric electron shells.
   The nucleus shows the proton (and neutron) count. Electron shells are
   drawn as circles with evenly spaced electron dots. If *electrons* is
   ``None``, shells are auto-filled using the sequence 2, 8, 8, 18, 18, 32.

   :param int protons: Number of protons (shown in the nucleus label).
   :param int neutrons: Number of neutrons. When ``0``, the nucleus label
      shows only protons (e.g. ``6p+``); otherwise both are shown
      (e.g. ``6p 6n``).
   :param list electrons: List of electron counts per shell (e.g.
      ``[2, 4]`` for carbon), or ``None`` for automatic filling based on
      the proton count.
   :param float cx: Center x-coordinate.
   :param float cy: Center y-coordinate.
   :param float nucleus_r: Radius of the nucleus circle in pixels.
   :param float shell_spacing: Spacing between concentric orbit rings
      in pixels.
   :param float creation: Creation time.
   :param float z: Z-index for layering.

   .. py:method:: orbit(start=0, end=None, speed=45)

      Animate all electrons orbiting the nucleus. Each electron dot
      rotates continuously around the center using ``always_rotate``.

      :param float start: Animation start time.
      :param float end: Animation end time (``None`` for indefinite).
      :param float speed: Rotation speed in degrees per second.

   .. code-block:: python

      # Carbon atom with 6 protons, 6 neutrons
      carbon = BohrAtom(protons=6, neutrons=6)
      carbon.orbit(start=0, end=5)

   Custom electron configuration:

   .. code-block:: python

      # Sodium with explicit shell configuration
      sodium = BohrAtom(protons=11, neutrons=12, electrons=[2, 8, 1])
      sodium.orbit(start=0, end=8, speed=60)

----

Automaton
---------

.. py:class:: Automaton(states, transitions, accept_states=None, initial_state=None, cx=960, cy=540, radius=300, state_r=35, font_size=20, creation=0, z=0)

   Finite state machine / automaton visualization. States are arranged in a
   circle and drawn as labeled circles. Transitions are drawn as arrows
   between states; self-loops are rendered as arcs above the state. Accept
   states are shown with a double circle (inner ring). The initial state
   receives an entry arrow from the left.

   :param list states: List of state name strings (e.g. ``['q0', 'q1', 'q2']``).
   :param list transitions: List of ``(from_state, to_state, label)`` tuples.
      Each tuple describes a labeled directed edge in the automaton.
   :param set accept_states: Set of state names drawn with a double circle
      to indicate acceptance.
   :param str initial_state: Name of the starting state. An entry arrow is
      drawn pointing into this state.
   :param float cx: Center x-coordinate of the state circle layout.
   :param float cy: Center y-coordinate of the state circle layout.
   :param float radius: Radius of the circular layout (distance from center
      to states).
   :param float state_r: Radius of each state circle.
   :param float font_size: Font size for state labels and transition labels.
   :param float creation: Creation time.
   :param float z: Z-index for layering.

   .. py:method:: highlight_state(state_name, start=0, end=1, color='#FFFF00', easing=there_and_back)

      Flash-highlight a state by name.

      :param str state_name: Name of the state to highlight.
      :param float start: Animation start time.
      :param float end: Animation end time.
      :param str color: Flash color.
      :param easing: Easing function.

   .. py:method:: highlight_transition(from_state, to_state, start=0, end=1, color='#FFFF00')

      Highlight the arrow (or arc for self-loops) between two states by
      flashing its color. For normal arrows, both the shaft and tip are
      flashed. For self-loop arcs, the stroke color is flashed.

      :param str from_state: Source state name.
      :param str to_state: Target state name.
      :param float start: Animation start time.
      :param float end: Animation end time.
      :param str color: Flash color.

   .. py:method:: simulate_input(word, start=0, delay=0.5, color='#FFFF00', transitions=None)

      Animate stepping through the automaton one character at a time. For
      each character in *word*, the method highlights the current state,
      then the transition arrow, then the next state. If no transition
      exists for a character, the current state flashes red (rejected).
      At the end, the final state is highlighted green if it is an accept
      state, or red otherwise.

      :param str word: Input string to process character by character.
      :param float start: Animation start time.
      :param float delay: Duration of each highlight step in seconds.
      :param str color: Highlight color during traversal.
      :param list transitions: Optional override for the transition list.
         Defaults to the transitions passed at construction.

   .. code-block:: python

      dfa = Automaton(
          states=['q0', 'q1', 'q2'],
          transitions=[
              ('q0', 'q1', 'a'),
              ('q1', 'q2', 'b'),
              ('q2', 'q0', 'c'),
          ],
          accept_states={'q2'},
          initial_state='q0',
      )

   Simulating input on a DFA that accepts strings ending in ``'ab'``:

   .. code-block:: python

      dfa = Automaton(
          states=['q0', 'q1', 'q2'],
          transitions=[
              ('q0', 'q0', 'b'),
              ('q0', 'q1', 'a'),
              ('q1', 'q0', 'a'),
              ('q1', 'q2', 'b'),
              ('q2', 'q0', 'b'),
              ('q2', 'q1', 'a'),
          ],
          accept_states={'q2'},
          initial_state='q0',
      )
      dfa.simulate_input('aab', start=0, delay=0.4)

----

NetworkGraph
------------

.. py:class:: NetworkGraph(nodes, edges=None, cx=960, cy=540, radius=300, node_r=30, font_size=20, layout='circular', directed=False, creation=0, z=0)

   Network/graph visualization with labeled nodes and edges. Supports
   three layout algorithms and both directed (arrow) and undirected (line)
   edge rendering. Edge labels are displayed at the midpoint of each edge.

   :param nodes: A list of labels (indexed 0, 1, ...) or a ``{id: label}``
      dictionary. When a list is provided, each element's index becomes its ID.
   :param list edges: List of ``(from_id, to_id)`` or
      ``(from_id, to_id, label)`` tuples. Edge labels are optional.
   :param float cx: Center x-coordinate of the layout.
   :param float cy: Center y-coordinate of the layout.
   :param float radius: Layout radius for circular layout, or half-extent
      for grid and spring layouts.
   :param float node_r: Radius of each node circle.
   :param float font_size: Font size for node and edge labels.
   :param str layout: Layout algorithm:

      - ``'circular'`` -- nodes evenly spaced on a circle (default).
      - ``'grid'`` -- nodes arranged in a square grid.
      - ``'spring'`` -- force-directed layout (50 iterations of repulsion
        and edge attraction with a fixed random seed of 42).

   :param bool directed: Draw edges as arrows when ``True``, as plain lines
      when ``False``.
   :param float creation: Creation time.
   :param float z: Z-index for layering.

   .. py:method:: highlight_node(node_id, start=0, end=1, color='#FFFF00', easing=there_and_back)

      Flash-highlight a node by its ID.

      :param node_id: The node identifier (integer index or dict key).
      :param float start: Animation start time.
      :param float end: Animation end time.
      :param str color: Flash color.
      :param easing: Easing function.

   .. py:method:: get_node_position(node_id)

      Return the ``(x, y)`` pixel position of a node. Returns ``ORIGIN``
      if the node ID is not found.

      :param node_id: The node identifier.
      :rtype: tuple[float, float]

   .. code-block:: python

      graph = NetworkGraph(
          nodes=['A', 'B', 'C', 'D'],
          edges=[(0, 1), (1, 2), (2, 3), (3, 0)],
          layout='circular',
      )

   A directed graph with edge labels using spring layout:

   .. code-block:: python

      graph = NetworkGraph(
          nodes=['S', 'A', 'B', 'T'],
          edges=[
              (0, 1, '4'), (0, 2, '3'),
              (1, 2, '1'), (1, 3, '2'),
              (2, 3, '5'),
          ],
          layout='spring',
          directed=True,
      )
      graph.highlight_node(0, start=0, end=1)
      graph.highlight_node(3, start=1, end=2)

----

Tree
----

.. py:class:: Tree(data, cx=960, cy=100, h_spacing=120, v_spacing=100, node_r=20, font_size=18, layout='down', creation=0, z=0)

   Hierarchical tree layout visualization. Nodes are drawn as labeled
   circles connected by straight-line edges. The tree is automatically
   laid out using a width-accumulating algorithm that avoids overlapping
   subtrees.

   :param data: Tree structure in one of two formats:

      - **Tuple format**: ``(label, [child_tuples, ...])`` where each child
        is itself a ``(label, children)`` tuple. Leaf nodes use an empty
        list: ``('leaf', [])``.
      - **Dictionary format**: A nested dict ``{key: {child_key: ...}}``.
        Converted internally to tuple format.

   :param float cx: X-coordinate for the root node.
   :param float cy: Y-coordinate for the root node.
   :param float h_spacing: Minimum horizontal spacing between siblings
      in pixels.
   :param float v_spacing: Vertical spacing between levels in pixels.
   :param float node_r: Radius of each node circle.
   :param float font_size: Font size for node labels.
   :param str layout: ``'down'`` places the root at the top with children
      below; ``'right'`` places the root at the left with children to the
      right.
   :param float creation: Creation time.
   :param float z: Z-index for layering.

   .. py:method:: get_node_position(label)

      Return the ``(x, y)`` pixel position of a node by its label. If
      there are duplicate labels, returns the position of the first
      occurrence. Returns ``ORIGIN`` if the label is not found.

      :param str label: Node label.
      :rtype: tuple[float, float]

   .. py:method:: highlight_node(label, start=0, end=1, color='#FFFF00', easing=there_and_back)

      Flash-highlight a node by label.

      :param str label: Node label to highlight.
      :param float start: Animation start time.
      :param float end: Animation end time.
      :param str color: Flash color.
      :param easing: Easing function.

   .. code-block:: python

      tree = Tree(('root', [
          ('A', [('A1', []), ('A2', [])]),
          ('B', [('B1', [])]),
      ]))

   A binary search tree with highlighted search path:

   .. code-block:: python

      bst = Tree(('8', [
          ('3', [('1', []), ('6', [('4', []), ('7', [])])]),
          ('10', [('', []), ('14', [('13', [])])]),
      ]))
      # Highlight search path for value 4
      for i, label in enumerate(['8', '3', '6', '4']):
          bst.highlight_node(label, start=i * 0.5, end=i * 0.5 + 0.4)

   Horizontal layout (root at left):

   .. code-block:: python

      tree = Tree(
          ('CEO', [
              ('CTO', [('Eng', []), ('QA', [])]),
              ('CFO', [('Finance', [])]),
          ]),
          layout='right',
      )

----

Stamp
-----

.. py:class:: Stamp(template, points, creation=0, z=0)

   Place deep copies of a template object at specified positions. Each copy
   is shifted so its center aligns with the given point. Useful for
   repeating a shape or symbol at multiple locations.

   :param VObject template: Object to deep-copy and place. Can be any
      ``VObject`` or ``VCollection``.
   :param list points: List of ``(x, y)`` positions for each copy.
   :param float creation: Creation time.
   :param float z: Z-index for layering.

   .. code-block:: python

      from vectormation.objects import *

      star = Polygon.regular(5, r=20, fill='#FFFF00', fill_opacity=0.8)
      positions = [(300, 300), (600, 200), (900, 350), (1200, 250)]
      stamps = Stamp(star, positions)

   Stamping dots along a curve:

   .. code-block:: python

      import math

      dot = Dot(r=8, fill='#58C4DD')
      points = [
          (960 + 300 * math.cos(t), 540 + 200 * math.sin(t))
          for t in [i * math.pi / 6 for i in range(12)]
      ]
      ring = Stamp(dot, points)

----

TimelineBar
-----------

.. py:class:: TimelineBar(markers, total_duration=10, x=200, y=900, width=1520, height=6, marker_color='#FFFF00', font_size=14, creation=0, z=0)

   Horizontal timeline bar with labeled markers at specific times. A thin
   track rectangle is drawn along the full width, with circular dots and
   tick lines placed at each marker position. Labels appear above each
   marker.

   :param dict markers: ``{time_value: label_text}`` dictionary. Each key
      is a numeric time that determines the marker's horizontal position.
   :param float total_duration: Total timeline duration (determines the
      scale). A marker at ``time_value`` is placed at fraction
      ``time_value / total_duration`` along the bar.
   :param float x: Left edge x-coordinate of the bar.
   :param float y: Y-coordinate (vertical center) of the bar.
   :param float width: Total bar width in pixels.
   :param float height: Height of the track rectangle.
   :param str marker_color: Color for marker dots and tick lines.
   :param float font_size: Font size for marker labels.
   :param float creation: Creation time.
   :param float z: Z-index for layering.

   .. code-block:: python

      tl = TimelineBar(
          {0: 'Start', 3: 'Phase 1', 7: 'Phase 2', 10: 'End'},
          total_duration=10,
      )

   A video production timeline:

   .. code-block:: python

      tl = TimelineBar(
          {0: 'Intro', 2: 'Problem', 5: 'Solution', 8: 'Demo', 10: 'Outro'},
          total_duration=10,
          y=1000,
          marker_color='#58C4DD',
      )

----

FlowChart
---------

.. py:class:: FlowChart(steps, direction='right', x=200, y=400, box_width=200, box_height=60, spacing=80, box_color='#58C4DD', text_color='#fff', arrow_color='#999', font_size=20, corner_radius=8, creation=0, z=0)

   Simple flow chart with labeled rounded-rectangle boxes connected by
   arrows. Boxes are arranged in a linear sequence either horizontally
   or vertically.

   :param list steps: List of step label strings (e.g.
      ``['Input', 'Process', 'Output']``).
   :param str direction: ``'right'`` for horizontal layout or ``'down'``
      for vertical layout.
   :param float x: X-coordinate of the first box's top-left corner.
   :param float y: Y-coordinate of the first box's top-left corner.
   :param float box_width: Width of each box in pixels.
   :param float box_height: Height of each box in pixels.
   :param float spacing: Gap between consecutive boxes in pixels.
   :param str box_color: Fill and stroke color for boxes.
   :param str text_color: Text color for step labels.
   :param str arrow_color: Stroke color for connecting arrows.
   :param float font_size: Font size for step labels.
   :param float corner_radius: Corner radius for rounded rectangles.
   :param float creation: Creation time.
   :param float z: Z-index for layering.

   .. code-block:: python

      flow = FlowChart(['Input', 'Process', 'Output'])

   A vertical software development flow:

   .. code-block:: python

      flow = FlowChart(
          ['Requirements', 'Design', 'Implement', 'Test', 'Deploy'],
          direction='down',
          x=800,
          y=100,
          box_color='#83C167',
          spacing=60,
      )

----

VennDiagram
-----------

.. py:class:: VennDiagram(labels, sizes=None, x=960, y=540, radius=150, colors=None, font_size=24, creation=0, z=0)

   Venn diagram with 2 or 3 overlapping semi-transparent circles. Labels
   are positioned outside each circle. The circles overlap with 25% fill
   opacity so intersection regions are visible as blended colors.

   :param list labels: 2 or 3 set labels (e.g. ``['Set A', 'Set B']`` or
      ``['A', 'B', 'C']``).
   :param list sizes: Per-circle radii (e.g. ``[150, 200]``). Defaults to
      *radius* for all circles.
   :param float x: Center x-coordinate of the diagram.
   :param float y: Center y-coordinate of the diagram.
   :param float radius: Default radius for all circles when *sizes* is
      ``None``.
   :param list colors: List of circle colors. Defaults to
      ``['#58C4DD', '#FF6B6B', '#83C167']``.
   :param float font_size: Font size for labels.
   :param float creation: Creation time.
   :param float z: Z-index for layering.

   For 2-circle diagrams, circles are placed side by side with 70% radius
   separation. For 3-circle diagrams, circles are arranged in a triangular
   pattern with 65% radius separation.

   .. code-block:: python

      venn2 = VennDiagram(['Python', 'JavaScript'])

   A three-set Venn diagram:

   .. code-block:: python

      venn3 = VennDiagram(
          ['Math', 'CS', 'Art'],
          radius=180,
          colors=['#FC6255', '#58C4DD', '#83C167'],
      )

   With different circle sizes:

   .. code-block:: python

      venn = VennDiagram(
          ['Large Set', 'Small Set'],
          sizes=[200, 120],
      )

----

OrgChart
--------

.. py:class:: OrgChart(root, x=960, y=80, h_spacing=180, v_spacing=100, box_width=120, box_height=40, font_size=16, colors=None, creation=0, z=0)

   Organization chart from a tree structure. Nodes are rendered as
   color-coded rounded-rectangle boxes connected by L-shaped path
   connectors. Box colors vary by depth level, cycling through the
   provided color palette. Layout is computed using a breadth-first
   traversal to evenly distribute nodes at each level.

   :param root: Tree structure as ``(label, [children])`` tuples, where
      each child is itself a ``(label, children)`` tuple and leaf nodes
      use an empty list.
   :param float x: Center x-coordinate of the chart (root node position).
   :param float y: Y-coordinate of the top (root) level.
   :param float h_spacing: Horizontal spacing between boxes at the same
      level in pixels.
   :param float v_spacing: Vertical spacing between levels in pixels.
   :param float box_width: Width of each box in pixels.
   :param float box_height: Height of each box in pixels.
   :param float font_size: Font size for box labels.
   :param list colors: List of colors to cycle through by depth. Defaults
      to the built-in ``DEFAULT_CHART_COLORS`` palette.
   :param float creation: Creation time.
   :param float z: Z-index for layering.

   .. code-block:: python

      org = OrgChart(('CEO', [
          ('CTO', [('Dev Lead', []), ('QA Lead', [])]),
          ('CFO', [('Accounting', [])]),
      ]))

   A larger organization with custom colors:

   .. code-block:: python

      org = OrgChart(
          ('Director', [
              ('Manager A', [
                  ('Team 1', []),
                  ('Team 2', []),
                  ('Team 3', []),
              ]),
              ('Manager B', [
                  ('Team 4', []),
                  ('Team 5', []),
              ]),
              ('Manager C', [
                  ('Team 6', []),
              ]),
          ]),
          h_spacing=160,
          v_spacing=120,
          colors=['#FC6255', '#58C4DD', '#83C167'],
      )

----

MindMap
-------

.. py:class:: MindMap(root, cx=960, cy=540, radius=250, font_size=18, colors=None, creation=0, z=0)

   Radial mind map diagram with a central node, branches, and
   grandchildren spread outward. The central topic is drawn as a large
   circle in the center, with first-level branches distributed evenly
   around it. Grandchildren (second-level nodes) fan out from their
   parent branch within a 60-degree arc.

   :param root: Tree structure as
      ``(label, [(child_label, [grandchildren]), ...])`` tuples.
      Grandchildren follow the same ``(label, children)`` format but
      only two levels of depth are rendered.
   :param float cx: Center x-coordinate.
   :param float cy: Center y-coordinate.
   :param float radius: Distance from center to branch nodes in pixels.
      Grandchildren are placed at ``radius * 0.5`` beyond their parent.
   :param float font_size: Font size for the central node and branches.
      Grandchild labels use ``font_size * 0.65``.
   :param list colors: List of colors to cycle through for branches.
      The first color is used for the central node. Defaults to the
      built-in ``DEFAULT_CHART_COLORS`` palette.
   :param float creation: Creation time.
   :param float z: Z-index for layering.

   .. code-block:: python

      mindmap = MindMap(('Project', [
          ('Design', [('UI', []), ('UX', [])]),
          ('Dev', [('Frontend', []), ('Backend', []), ('DB', [])]),
          ('Test', [('Unit', []), ('E2E', [])]),
          ('Deploy', []),
      ]))

   A study notes mind map with custom colors:

   .. code-block:: python

      mindmap = MindMap(
          ('Physics', [
              ('Mechanics', [
                  ('Kinematics', []),
                  ('Dynamics', []),
                  ('Energy', []),
              ]),
              ('Waves', [
                  ('Sound', []),
                  ('Light', []),
              ]),
              ('Thermo', [
                  ('Heat', []),
                  ('Entropy', []),
              ]),
              ('E&M', []),
          ]),
          radius=280,
          colors=['#FC6255', '#58C4DD', '#83C167', '#FFFF00', '#9A72AC'],
      )

----

Examples
--------

Chess game animation
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from vectormation.objects import *

   canvas = VectorMathAnim()
   canvas.set_background()

   board = ChessBoard()
   board.move_piece('e2', 'e4', start=0, end=1)
   board.move_piece('e7', 'e5', start=1, end=2)
   board.move_piece('g1', 'f3', start=2, end=3)
   board.move_piece('b8', 'c6', start=3, end=4)

   canvas.add_objects(board)
   canvas.browser_display()

DFA simulation
^^^^^^^^^^^^^^

.. code-block:: python

   from vectormation.objects import *

   canvas = VectorMathAnim()
   canvas.set_background()

   # DFA that accepts binary strings divisible by 3
   dfa = Automaton(
       states=['q0', 'q1', 'q2'],
       transitions=[
           ('q0', 'q0', '0'), ('q0', 'q1', '1'),
           ('q1', 'q2', '0'), ('q1', 'q0', '1'),
           ('q2', 'q1', '0'), ('q2', 'q2', '1'),
       ],
       accept_states={'q0'},
       initial_state='q0',
   )
   dfa.simulate_input('110', start=0, delay=0.5)

   canvas.add_objects(dfa)
   canvas.browser_display()

Graph with spring layout
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from vectormation.objects import *

   canvas = VectorMathAnim()
   canvas.set_background()

   graph = NetworkGraph(
       nodes={0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E'},
       edges=[(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (1, 4)],
       layout='spring',
       directed=True,
   )
   graph.highlight_node(0, start=0, end=1)
   graph.highlight_node(4, start=1, end=2)

   canvas.add_objects(graph)
   canvas.browser_display()

Atomic model animation
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from vectormation.objects import *

   canvas = VectorMathAnim()
   canvas.set_background()

   oxygen = BohrAtom(protons=8, neutrons=8, shell_spacing=50)
   oxygen.orbit(start=0, end=10, speed=30)

   canvas.add_objects(oxygen)
   canvas.browser_display()

Mind map with animation
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from vectormation.objects import *

   canvas = VectorMathAnim()
   canvas.set_background()

   mm = MindMap(('ML', [
       ('Supervised', [('Classification', []), ('Regression', [])]),
       ('Unsupervised', [('Clustering', []), ('PCA', [])]),
       ('RL', [('Q-Learning', []), ('Policy Grad', [])]),
   ]))
   mm.write(start=0, end=2)

   canvas.add_objects(mm)
   canvas.browser_display()
