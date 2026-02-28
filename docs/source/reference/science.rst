Science & Electronics
=====================

Scientific visualization and electronic component classes. Circuit components
(Resistor, Capacitor, etc.) draw standard schematic symbols between two
endpoints and support arbitrary rotation via the ``(x1, y1) -> (x2, y2)``
convention. Higher-level classes such as :py:class:`NeuralNetwork`,
:py:class:`Pendulum`, and :py:class:`StandingWave` combine geometry with
time-varying animation.

.. code-block:: python

   from vectormation.objects import *

----

Resistor
--------

.. py:class:: Resistor(x1=400, y1=540, x2=600, y2=540, label='R', creation=0, z=0, **styling_kwargs)

   Electrical resistor schematic symbol drawn as a zigzag line between two
   endpoints, with optional lead wires on each side.

   :param float x1: Start x-coordinate.
   :param float y1: Start y-coordinate.
   :param float x2: End x-coordinate.
   :param float y2: End y-coordinate.
   :param str label: Text label placed beside the symbol. Pass ``''`` to hide.
   :param float creation: Creation time.
   :param float z: Z-index for layering.
   :param styling_kwargs: Additional SVG styling (default ``stroke='#fff'``,
      ``stroke_width=2``).

   .. code-block:: python

      r = Resistor(x1=400, y1=540, x2=700, y2=540, label='R1')

   The component can be placed at any angle by choosing different endpoints:

   .. code-block:: python

      # Vertical resistor
      r_vert = Resistor(x1=960, y1=300, x2=960, y2=600, label='R2')

----

Capacitor
---------

.. py:class:: Capacitor(x1=400, y1=540, x2=600, y2=540, label='C', creation=0, z=0, **styling_kwargs)

   Electrical capacitor symbol: two parallel plates with lead wires.

   :param float x1: Start x-coordinate.
   :param float y1: Start y-coordinate.
   :param float x2: End x-coordinate.
   :param float y2: End y-coordinate.
   :param str label: Text label placed beside the symbol. Pass ``''`` to hide.
   :param float creation: Creation time.
   :param float z: Z-index for layering.
   :param styling_kwargs: Additional SVG styling (default ``stroke='#fff'``,
      ``stroke_width=2``).

   .. code-block:: python

      c = Capacitor(x1=400, y1=540, x2=600, y2=540, label='C1')

----

Inductor
--------

.. py:class:: Inductor(x1=400, y1=540, x2=600, y2=540, label='L', n_loops=4, creation=0, z=0, **styling_kwargs)

   Electrical inductor symbol drawn as a series of semicircular arcs
   (coil / solenoid) between two endpoints.

   :param float x1: Start x-coordinate.
   :param float y1: Start y-coordinate.
   :param float x2: End x-coordinate.
   :param float y2: End y-coordinate.
   :param str label: Text label placed beside the symbol. Pass ``''`` to hide.
   :param int n_loops: Number of coil loops.
   :param float creation: Creation time.
   :param float z: Z-index for layering.
   :param styling_kwargs: Additional SVG styling (default ``stroke='#fff'``,
      ``stroke_width=2``).

   .. code-block:: python

      ind = Inductor(x1=400, y1=540, x2=700, y2=540, n_loops=6, label='L1')

----

Diode
-----

.. py:class:: Diode(x1=400, y1=540, x2=600, y2=540, label='D', creation=0, z=0, **styling_kwargs)

   Electrical diode symbol: a triangle pointing in the direction of current
   flow with a bar at the tip, plus lead wires.

   :param float x1: Start (anode side) x-coordinate.
   :param float y1: Start (anode side) y-coordinate.
   :param float x2: End (cathode side) x-coordinate.
   :param float y2: End (cathode side) y-coordinate.
   :param str label: Text label placed beside the symbol. Pass ``''`` to hide.
   :param float creation: Creation time.
   :param float z: Z-index for layering.
   :param styling_kwargs: Additional SVG styling (default ``stroke='#fff'``,
      ``stroke_width=2``).

   .. code-block:: python

      d = Diode(x1=400, y1=540, x2=600, y2=540, label='D1')

----

LED
---

.. py:class:: LED(x1=400, y1=540, x2=600, y2=540, label='LED', color='#FF0000', creation=0, z=0, **styling_kwargs)

   Light-emitting diode symbol: a :py:class:`Diode` with two small rays
   emanating from the junction to indicate light emission.

   :param float x1: Start (anode side) x-coordinate.
   :param float y1: Start (anode side) y-coordinate.
   :param float x2: End (cathode side) x-coordinate.
   :param float y2: End (cathode side) y-coordinate.
   :param str label: Text label placed beside the symbol. Pass ``''`` to hide.
   :param str color: Stroke color for the light rays (e.g. ``'#FF0000'``
      for red, ``'#00FF00'`` for green).
   :param float creation: Creation time.
   :param float z: Z-index for layering.
   :param styling_kwargs: Passed through to the underlying :py:class:`Diode`.

   .. code-block:: python

      led = LED(x1=400, y1=540, x2=600, y2=540, color='#00FF00', label='LED1')

----

Circuit example
^^^^^^^^^^^^^^^

All five electronic components can be chained to form a schematic:

.. code-block:: python

   from vectormation.objects import *

   canvas = VectorMathAnim()
   canvas.set_background()

   r = Resistor(x1=200, y1=400, x2=500, y2=400, label='R')
   c = Capacitor(x1=500, y1=400, x2=800, y2=400, label='C')
   ind = Inductor(x1=800, y1=400, x2=1100, y2=400, label='L')
   d = Diode(x1=1100, y1=400, x2=1400, y2=400, label='D')
   led = LED(x1=1400, y1=400, x2=1700, y2=400, label='LED', color='#FF0000')

   canvas.add_objects(r, c, ind, d, led)
   canvas.browser_display()

----

UnitInterval
------------

.. py:class:: UnitInterval(x=360, y=540, length=600, tick_step=0.1, show_labels=True, font_size=18, creation=0, z=0, **styling_kwargs)

   Convenience wrapper that returns a :py:class:`NumberLine` pre-configured
   for the ``[0, 1]`` range -- commonly used for probabilities and
   normalized parameters.

   :param float x: Left edge x-position.
   :param float y: Y-position.
   :param float length: Line length in pixels.
   :param float tick_step: Spacing between ticks (in the 0--1 range).
   :param bool show_labels: Show numeric tick labels.
   :param float font_size: Font size for tick labels.
   :param float creation: Creation time.
   :param float z: Z-index for layering.
   :param styling_kwargs: Passed through to :py:class:`NumberLine`.

   .. note::

      ``UnitInterval`` uses ``__new__`` and returns a ``NumberLine`` instance
      directly, so ``isinstance(UnitInterval(), NumberLine)`` is ``True``.

   .. code-block:: python

      ui = UnitInterval(x=360, y=540, tick_step=0.25)

----

Molecule2D
----------

.. py:class:: Molecule2D(atoms, bonds=None, scale=80, cx=960, cy=540, atom_radius=20, font_size=16, creation=0, z=0)

   Simple 2D molecule visualization built from atom positions and bond
   connectivity. Atoms are drawn as colored circles (element-specific
   palette) with text labels, and bonds are rendered as single, double,
   or triple parallel lines.

   :param list atoms: List of ``(element_symbol, x, y)`` tuples where *x*
      and *y* are in abstract units (scaled by *scale*).
   :param list bonds: List of ``(i, j)`` or ``(i, j, order)`` tuples.
      *i* and *j* are zero-based atom indices; *order* defaults to 1
      (single bond). Use 2 for double bonds and 3 for triple bonds.
   :param float scale: Pixels per abstract unit.
   :param float cx: Center x-position of the molecule on canvas.
   :param float cy: Center y-position of the molecule on canvas.
   :param float atom_radius: Radius of each atom circle.
   :param float font_size: Font size for element labels.
   :param float creation: Creation time.
   :param float z: Z-index for layering.

   Built-in atom color palette:

   ======= ========= ============
   Symbol  Color     Description
   ======= ========= ============
   C       ``#555``  Carbon
   H       ``#fff``  Hydrogen
   O       ``#FF4444`` Oxygen
   N       ``#4444FF`` Nitrogen
   S       ``#FFFF00`` Sulfur
   P       ``#FF8800`` Phosphorus
   F       ``#00FF00`` Fluorine
   Cl      ``#00FF00`` Chlorine
   Br      ``#882200`` Bromine
   I       ``#8800FF`` Iodine
   ======= ========= ============

   .. code-block:: python

      # Water molecule (H2O)
      water = Molecule2D(
          atoms=[('O', 0, 0), ('H', -0.8, 0.6), ('H', 0.8, 0.6)],
          bonds=[(0, 1), (0, 2)],
      )

   .. code-block:: python

      # Carbon dioxide with double bonds
      co2 = Molecule2D(
          atoms=[('O', -1.2, 0), ('C', 0, 0), ('O', 1.2, 0)],
          bonds=[(0, 1, 2), (1, 2, 2)],
      )

----

NeuralNetwork
-------------

.. py:class:: NeuralNetwork(layer_sizes, cx=960, cy=540, width=800, height=500, neuron_radius=16, neuron_fill='#58C4DD', edge_color='#888', edge_width=1, creation=0, z=0)

   Neural network diagram with layers of neurons connected by fully-connected
   edges. Supports labeling input/output layers, activating individual neurons,
   animating forward propagation, and highlighting specific paths.

   :param list[int] layer_sizes: Number of neurons per layer
      (e.g. ``[3, 5, 2]`` for a 3-layer network).
   :param float cx: Center x-position.
   :param float cy: Center y-position.
   :param float width: Total diagram width in pixels.
   :param float height: Total diagram height in pixels.
   :param float neuron_radius: Radius of each neuron circle.
   :param str neuron_fill: Fill color for neurons.
   :param str edge_color: Stroke color for connecting lines.
   :param float edge_width: Stroke width for connecting lines.
   :param float creation: Creation time.
   :param float z: Z-index for layering.

   .. py:method:: label_input(labels, font_size=20, buff=30, **kwargs) -> NeuralNetwork

      Add text labels to the left of each input-layer neuron.

      :param list labels: List of label strings (one per input neuron).
      :param float font_size: Font size for labels.
      :param float buff: Horizontal buffer between neuron and label.

   .. py:method:: label_output(labels, font_size=20, buff=30, **kwargs) -> NeuralNetwork

      Add text labels to the right of each output-layer neuron.

      :param list labels: List of label strings (one per output neuron).
      :param float font_size: Font size for labels.
      :param float buff: Horizontal buffer between neuron and label.

   .. py:method:: activate(layer_idx, neuron_idx, start=0, end=1, color='#FFFF00') -> NeuralNetwork

      Flash-animate a single neuron to indicate activation.

      :param int layer_idx: Zero-based layer index.
      :param int neuron_idx: Zero-based neuron index within the layer.
      :param float start: Animation start time.
      :param float end: Animation end time.
      :param str color: Flash color.

   .. py:method:: propagate(start=0, duration=2, delay=0.3, color='#FFFF00') -> NeuralNetwork

      Animate a forward-propagation signal that flashes each layer in
      sequence from input to output.

      :param float start: Animation start time.
      :param float duration: Total duration of the propagation animation.
      :param float delay: Time offset between successive layers.
      :param str color: Flash color.

   .. py:method:: highlight_path(path, start=0, delay=0.3, color='#FF6B6B', edge_color='#FF6B6B') -> NeuralNetwork

      Highlight a specific path through the network by flashing neurons
      and their connecting edges.

      :param list[int] path: Neuron index per layer (e.g. ``[0, 2, 1]``
         for a 3-layer network). Length must match the number of layers.
      :param float start: Animation start time.
      :param float delay: Time offset between successive layers.
      :param str color: Neuron flash color.
      :param str edge_color: Edge flash color.

   .. code-block:: python

      nn = NeuralNetwork([3, 5, 4, 2])
      nn.label_input(['x1', 'x2', 'x3'])
      nn.label_output(['y1', 'y2'])
      nn.propagate(start=0, duration=3)

----

Pendulum
--------

.. py:class:: Pendulum(pivot_x=960, pivot_y=200, length=300, angle=30, bob_radius=20, period=2.0, damping=0.0, start=0, end=5, creation=0, z=0)

   Animated simple pendulum consisting of a pivot point, a rigid rod, and
   a circular bob. The bob oscillates according to ``angle * exp(-damping * t) * cos(2*pi/period * t)``.

   :param float pivot_x: Pivot point x-coordinate.
   :param float pivot_y: Pivot point y-coordinate.
   :param float length: Rod length in pixels.
   :param float angle: Initial angle in **degrees** from vertical.
   :param float bob_radius: Radius of the bob circle.
   :param float period: Oscillation period in seconds.
   :param float damping: Exponential damping factor. ``0`` means no damping
      (perpetual oscillation); larger values cause the amplitude to decay.
   :param float start: Animation start time.
   :param float end: Animation end time.
   :param float creation: Creation time.
   :param float z: Z-index for layering.

   .. py:attribute:: pivot
      :type: Dot

      The pivot point dot (small grey circle).

   .. py:attribute:: rod
      :type: Line

      The rigid rod connecting the pivot to the bob.

   .. py:attribute:: bob
      :type: Circle

      The bob circle at the end of the rod.

   .. code-block:: python

      from vectormation.objects import *

      canvas = VectorMathAnim()
      canvas.set_background()

      p = Pendulum(angle=45, period=1.5, damping=0.1, start=0, end=10)
      canvas.add_objects(p)
      canvas.browser_display()

   Multiple pendulums with different periods can illustrate phase relationships:

   .. code-block:: python

      pendulums = [
          Pendulum(pivot_x=400 + i * 200, angle=30,
                   period=1.0 + i * 0.2, end=10)
          for i in range(5)
      ]
      canvas.add_objects(*pendulums)

----

StandingWave
------------

.. py:class:: StandingWave(x1=300, y1=540, x2=1620, y2=540, amplitude=100, harmonics=3, frequency=1.0, num_points=200, start=0, end=5, creation=0, z=0, **kwargs)

   Animated standing wave between two fixed endpoints. The wave displacement
   is computed as ``amplitude * sin(k * x) * cos(omega * t)`` where *k*
   depends on the harmonic number.

   :param float x1: Left endpoint x-coordinate.
   :param float y1: Left endpoint y-coordinate.
   :param float x2: Right endpoint x-coordinate.
   :param float y2: Right endpoint y-coordinate.
   :param float amplitude: Maximum displacement in pixels.
   :param int harmonics: Number of half-wavelengths (harmonic number).
      ``1`` gives the fundamental mode, ``2`` the second harmonic, etc.
   :param float frequency: Oscillation frequency in Hz.
   :param int num_points: Number of sample points along the wave path.
   :param float start: Animation start time.
   :param float end: Animation end time.
   :param float creation: Creation time.
   :param float z: Z-index for layering.
   :param kwargs: Additional SVG styling. Supports ``stroke`` (default
      ``'#58C4DD'``) and ``stroke_width`` (default ``3``).

   .. py:attribute:: dot1
      :type: Dot

      Fixed endpoint dot at ``(x1, y1)``.

   .. py:attribute:: dot2
      :type: Dot

      Fixed endpoint dot at ``(x2, y2)``.

   .. py:attribute:: wave
      :type: Path

      The animated wave path whose ``d`` attribute is recomputed each frame.

   .. code-block:: python

      from vectormation.objects import *

      canvas = VectorMathAnim()
      canvas.set_background()

      wave = StandingWave(harmonics=3, frequency=2.0, amplitude=80,
                          start=0, end=6)
      canvas.add_objects(wave)
      canvas.browser_display()

   Display multiple harmonics stacked vertically:

   .. code-block:: python

      waves = [
          StandingWave(y1=200 + i * 150, y2=200 + i * 150,
                       harmonics=i + 1, frequency=1.0, end=8,
                       stroke=['#58C4DD', '#FF6B6B', '#83C167',
                               '#FFFF00'][i])
          for i in range(4)
      ]
      canvas.add_objects(*waves)

----

Examples
--------

RLC circuit with component labels
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from vectormation.objects import *

   canvas = VectorMathAnim()
   canvas.set_background()

   y = 540
   r = Resistor(x1=200, y1=y, x2=500, y2=y, label='100\u03A9')
   ind = Inductor(x1=500, y1=y, x2=850, y2=y, label='10mH')
   c = Capacitor(x1=850, y1=y, x2=1100, y2=y, label='47\u00B5F')

   canvas.add_objects(r, ind, c)
   canvas.browser_display()

Neural network with activation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from vectormation.objects import *

   canvas = VectorMathAnim()
   canvas.set_background()

   nn = NeuralNetwork([4, 6, 6, 3], width=900, height=500)
   nn.label_input(['x1', 'x2', 'x3', 'x4'])
   nn.label_output(['cat', 'dog', 'bird'])
   nn.propagate(start=0, duration=4, color='#FFFF00')
   nn.highlight_path([1, 3, 2, 0], start=5, delay=0.5)

   canvas.add_objects(nn)
   canvas.browser_display()

Damped pendulum
^^^^^^^^^^^^^^^

.. code-block:: python

   from vectormation.objects import *

   canvas = VectorMathAnim()
   canvas.set_background()

   p = Pendulum(pivot_x=960, pivot_y=150, length=350, angle=60,
                period=2.0, damping=0.15, start=0, end=12)

   # Trace the path of the bob
   trail = p.bob.trace_path(start=0, end=12, stroke='#FF6B6B',
                             stroke_width=1, stroke_opacity=0.5)

   canvas.add_objects(p, trail)
   canvas.browser_display()

Molecule gallery
^^^^^^^^^^^^^^^^

.. code-block:: python

   from vectormation.objects import *

   canvas = VectorMathAnim()
   canvas.set_background()

   # Methane (CH4) - tetrahedral layout approximation
   methane = Molecule2D(
       atoms=[('C', 0, 0), ('H', -1, -0.7), ('H', 1, -0.7),
              ('H', -0.7, 0.9), ('H', 0.7, 0.9)],
       bonds=[(0, 1), (0, 2), (0, 3), (0, 4)],
       cx=480, cy=540,
   )

   # Ethylene (C2H4) with double bond
   ethylene = Molecule2D(
       atoms=[('C', -0.6, 0), ('C', 0.6, 0),
              ('H', -1.3, -0.6), ('H', -1.3, 0.6),
              ('H', 1.3, -0.6), ('H', 1.3, 0.6)],
       bonds=[(0, 1, 2), (0, 2), (0, 3), (1, 4), (1, 5)],
       cx=1440, cy=540,
   )

   canvas.add_objects(methane, ethylene)
   canvas.browser_display()
