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
   :no-index:

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
   :no-index:

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
   :no-index:

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
   :no-index:

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
   :no-index:

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
   :no-index:

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
   :no-index:

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

   ======= ============ ============
   Symbol  Color        Description
   ======= ============ ============
   C       ``#555``     Carbon
   H       ``#fff``     Hydrogen
   O       ``#FF4444``  Oxygen
   N       ``#4444FF``  Nitrogen
   S       ``#FFFF00``  Sulfur
   P       ``#FF8800``  Phosphorus
   F       ``#00FF00``  Fluorine
   Cl      ``#00FF00``  Chlorine
   Br      ``#882200``  Bromine
   I       ``#8800FF``  Iodine
   ======= ============ ============

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
   :no-index:

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
      :no-index:

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
   :no-index:

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
   :no-index:

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

Charge
------

.. py:class:: Charge(magnitude=1, cx=960, cy=540, radius=None, color=None, add_glow=True, glow_layers=12, creation=0, z=0, **styling_kwargs)

   Electrostatic point charge with a colored circle and +/- symbol.
   Positive charges are drawn in red with a "+" sign, negative charges
   in blue with a "-" sign.  Optional concentric translucent rings
   create a glow effect.

   :param float magnitude: Charge strength. Positive = red "+", negative = blue "-".
   :param float cx: Center x-coordinate.
   :param float cy: Center y-coordinate.
   :param float radius: Circle radius. ``None`` auto-scales from magnitude.
   :param str color: Override the automatic red/blue color.
   :param bool add_glow: Draw concentric translucent rings for a glow effect.
   :param int glow_layers: Number of glow rings (more = smoother but heavier).
   :param float creation: Creation time.
   :param float z: Z-index for layering.

   .. code-block:: python

      q_pos = Charge(magnitude=3, cx=600, cy=540)
      q_neg = Charge(magnitude=-2, cx=1300, cy=540)

----

ElectricField
-------------

.. py:class:: ElectricField(*charges, x_range=(60, 1860, 120), y_range=(60, 1020, 120), max_length=80, color='#58C4DD', creation=0, z=0, **styling_kwargs)

   Electric field visualization from a list of :py:class:`Charge` objects.
   Computes Coulomb superposition at grid points and renders arrows
   via ``ArrowVectorField``.

   :param Charge charges: One or more Charge instances (positional args).
   :param tuple x_range: Grid sampling x-range as ``(min, max, step)``.
   :param tuple y_range: Grid sampling y-range as ``(min, max, step)``.
   :param float max_length: Maximum arrow length in pixels.
   :param str color: Arrow color.
   :param float creation: Creation time.
   :param float z: Z-index for layering.

   .. code-block:: python

      q1 = Charge(magnitude=3, cx=600, cy=540)
      q2 = Charge(magnitude=-3, cx=1300, cy=540)
      field = ElectricField(q1, q2)

----

Lens
----

.. py:class:: Lens(cx=960, cy=540, height=300, focal_length=200, thickness=30, n=1.52, color='#58C4DD', show_focal_points=True, show_axis=True, creation=0, z=0, **styling_kwargs)

   Convex or concave lens for geometric optics diagrams.  Convex lenses
   (positive focal length) are drawn as a biconvex shape; concave lenses
   (negative focal length) are thin at the center and thick at the edges.

   :param float cx: Center x-coordinate.
   :param float cy: Center y-coordinate.
   :param float height: Lens height in pixels.
   :param float focal_length: Positive = convex, negative = concave.
   :param float thickness: Maximum lens thickness in pixels.
   :param float n: Refractive index (used by Ray for Snell's law).
   :param str color: Fill color.
   :param bool show_focal_points: Draw dots at the focal points.
   :param bool show_axis: Draw the principal axis as a dashed line.
   :param float creation: Creation time.
   :param float z: Z-index for layering.

   .. py:method:: image_point(obj_x, obj_y)

      Compute the image position using the thin-lens equation
      ``1/f = 1/do + 1/di``.  Returns ``(image_x, image_y)`` or ``None``
      if the object is at the focal point (image at infinity).

      :param float obj_x: Object x-coordinate.
      :param float obj_y: Object y-coordinate.
      :returns: ``(image_x, image_y)`` or ``None``.

   .. code-block:: python

      lens = Lens(focal_length=200, height=400)
      # Compute where an object at (400, 400) forms its image:
      img = lens.image_point(400, 400)

----

Ray
---

.. py:class:: Ray(x1=200, y1=540, angle=0, length=1600, lenses=None, color='#FFFF00', stroke_width=2, show_arrow=False, creation=0, z=0, **styling_kwargs)

   A light ray that propagates in a straight line and refracts through
   :py:class:`Lens` objects using Snell's law (thin-lens paraxial
   approximation).

   :param float x1: Starting x-coordinate.
   :param float y1: Starting y-coordinate.
   :param float angle: Initial direction in degrees (0 = rightward).
   :param float length: Ray length in pixels.
   :param list lenses: List of :py:class:`Lens` instances to refract through.
   :param str color: Ray stroke color.
   :param float stroke_width: Ray line width.
   :param bool show_arrow: Draw a small arrowhead at the tip.
   :param float creation: Creation time.
   :param float z: Z-index for layering.

   .. code-block:: python

      lens = Lens(focal_length=200)
      ray = Ray(x1=200, y1=400, angle=5, lenses=[lens], show_arrow=True)

----

Electrostatics example
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from vectormation.objects import *

   canvas = VectorMathAnim()
   canvas.set_background()

   q1 = Charge(magnitude=3, cx=600, cy=540)
   q2 = Charge(magnitude=-3, cx=1300, cy=540)
   field = ElectricField(q1, q2)

   canvas.add_objects(field, q1, q2)
   canvas.browser_display()

Optics example
^^^^^^^^^^^^^^

.. code-block:: python

   from vectormation.objects import *

   canvas = VectorMathAnim()
   canvas.set_background()

   lens = Lens(focal_length=200, height=400)

   # Three parallel rays at different heights
   rays = [
       Ray(x1=200, y1=440, lenses=[lens], show_arrow=True),
       Ray(x1=200, y1=540, lenses=[lens], show_arrow=True),
       Ray(x1=200, y1=640, lenses=[lens], show_arrow=True),
   ]

   canvas.add_objects(lens, *rays)
   canvas.browser_display()

----

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
