"""Science and electronics classes: Resistor, NeuralNetwork, Pendulum, etc."""
import math
from vectormation._constants import _normalize, _label_text, ORIGIN, CANVAS_WIDTH, CANVAS_HEIGHT
from vectormation._base import VCollection
from vectormation._shapes import Circle, Dot, Line, Lines, Text, Path, Polygon, Rectangle


def _component_geom(x1, y1, x2, y2):
    """Return (length, ux, uy, px, py, mx, my) for a two-terminal component."""
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1
    ux, uy = _normalize(dx, dy)
    return length, ux, uy, -uy, ux, (x1 + x2) / 2, (y1 + y2) / 2


def _add_label(objects, label, lx, ly, creation, z):
    """Append a small grey label Text to *objects* if *label* is truthy."""
    if label:
        objects.append(Text(text=label, x=lx, y=ly, font_size=18,
                            fill='#aaa', stroke_width=0, text_anchor='middle',
                            creation=creation, z=z + 0.1))

_COMPONENT_STYLE = {'stroke': '#fff', 'stroke_width': 2}


class Resistor(VCollection):
    """Electrical resistor symbol (zigzag line)."""
    def __init__(self, x1: float = 400, y1=ORIGIN[1], x2: float = 600, y2=ORIGIN[1], label='R',
                 creation: float = 0, z: float = 0, **styling_kwargs):
        style_kw = _COMPONENT_STYLE | styling_kwargs
        length, ux, uy, px, py, mx, my = _component_geom(x1, y1, x2, y2)
        lead, zag_end = 0.25, 0.75
        n_zags, zag_amp = 6, 12
        pts = [(x1, y1), (x1 + ux * length * lead, y1 + uy * length * lead)]
        for i in range(n_zags):
            t = lead + (zag_end - lead) * (i + 0.5) / n_zags
            sign = 1 if i % 2 == 0 else -1
            pts.append((x1 + ux * length * t + px * zag_amp * sign,
                        y1 + uy * length * t + py * zag_amp * sign))
        pts.extend([(x1 + ux * length * zag_end, y1 + uy * length * zag_end), (x2, y2)])
        objects = [Lines(*pts, creation=creation, z=z, fill_opacity=0, **style_kw)]
        _add_label(objects, label, mx + px * (zag_amp + 16), my + py * (zag_amp + 16), creation, z)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'Resistor()'

class Capacitor(VCollection):
    """Electrical capacitor symbol (two parallel plates)."""
    def __init__(self, x1: float = 400, y1=ORIGIN[1], x2: float = 600, y2=ORIGIN[1], label='C',
                 creation: float = 0, z: float = 0, **styling_kwargs):
        style_kw = _COMPONENT_STYLE | styling_kwargs
        _, ux, uy, px, py, mx, my = _component_geom(x1, y1, x2, y2)
        gap, plate_h = 8, 24
        objects = [
            Line(x1=x1, y1=y1, x2=mx - ux * gap, y2=my - uy * gap,
                 creation=creation, z=z, **style_kw),
            Line(x1=mx - ux * gap + px * plate_h, y1=my - uy * gap + py * plate_h,
                 x2=mx - ux * gap - px * plate_h, y2=my - uy * gap - py * plate_h,
                 creation=creation, z=z, **style_kw),
            Line(x1=mx + ux * gap + px * plate_h, y1=my + uy * gap + py * plate_h,
                 x2=mx + ux * gap - px * plate_h, y2=my + uy * gap - py * plate_h,
                 creation=creation, z=z, **style_kw),
            Line(x1=mx + ux * gap, y1=my + uy * gap, x2=x2, y2=y2,
                 creation=creation, z=z, **style_kw),
        ]
        _add_label(objects, label, mx + px * (plate_h + 16), my + py * (plate_h + 16), creation, z)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'Capacitor()'

class Inductor(VCollection):
    """Electrical inductor symbol (coil/solenoid)."""
    def __init__(self, x1: float = 400, y1=ORIGIN[1], x2: float = 600, y2=ORIGIN[1], label='L',
                 n_loops=4, creation: float = 0, z: float = 0, **styling_kwargs):
        style_kw = _COMPONENT_STYLE | styling_kwargs
        length, ux, uy, px, py, mx, my = _component_geom(x1, y1, x2, y2)
        lead = 0.2
        coil_start = lead
        coil_end = 1 - lead
        coil_len = coil_end - coil_start
        arc_r = length * coil_len / (2 * n_loops)
        d_parts = [f'M{x1},{y1} L{x1 + ux * length * lead},{y1 + uy * length * lead}']
        for i in range(n_loops):
            end_t = coil_start + coil_len * (i + 1) / n_loops
            ex = x1 + ux * length * end_t
            ey = y1 + uy * length * end_t
            d_parts.append(f'A{arc_r},{arc_r} 0 0 1 {ex},{ey}')
        d_parts.append(f'L{x2},{y2}')
        d_str = ' '.join(d_parts)
        coil = Path(d_str, x=0, y=0, creation=creation, z=z, fill_opacity=0, **style_kw)
        objects = [coil]
        _add_label(objects, label, mx + px * (arc_r + 16), my + py * (arc_r + 16), creation, z)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'Inductor()'

class Diode(VCollection):
    """Electrical diode symbol (triangle with bar)."""
    def __init__(self, x1: float = 400, y1=ORIGIN[1], x2: float = 600, y2=ORIGIN[1], label='D',
                 creation: float = 0, z: float = 0, **styling_kwargs):
        style_kw = _COMPONENT_STYLE | styling_kwargs
        length, ux, uy, px, py, mx, my = _component_geom(x1, y1, x2, y2)
        tri_h, tri_w = length * 0.2, 20
        # Triangle vertices: tip pointing in direction of current flow
        tip_x = mx + ux * tri_h
        tip_y = my + uy * tri_h
        base1_x = mx - ux * tri_h + px * tri_w
        base1_y = my - uy * tri_h + py * tri_w
        base2_x = mx - ux * tri_h - px * tri_w
        base2_y = my - uy * tri_h - py * tri_w
        triangle = Polygon((base1_x, base1_y), (base2_x, base2_y), (tip_x, tip_y),
                           creation=creation, z=z, fill_opacity=0, **style_kw)
        # Bar at the tip
        bar = Line(x1=tip_x + px * tri_w, y1=tip_y + py * tri_w,
                   x2=tip_x - px * tri_w, y2=tip_y - py * tri_w,
                   creation=creation, z=z, **style_kw)
        # Lead wires
        lead1 = Line(x1=x1, y1=y1, x2=mx - ux * tri_h, y2=my - uy * tri_h,
                     creation=creation, z=z, **style_kw)
        lead2 = Line(x1=tip_x, y1=tip_y, x2=x2, y2=y2,
                     creation=creation, z=z, **style_kw)
        objects = [lead1, triangle, bar, lead2]
        _add_label(objects, label, mx + px * (tri_w + 16), my + py * (tri_w + 16), creation, z)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'Diode()'

class LED(VCollection):
    """Light-emitting diode symbol (diode with light rays)."""
    def __init__(self, x1: float = 400, y1=ORIGIN[1], x2: float = 600, y2=ORIGIN[1], label='LED',
                 color='#FF0000', creation: float = 0, z: float = 0, **styling_kwargs):
        diode = Diode(x1=x1, y1=y1, x2=x2, y2=y2, label='',
                      creation=creation, z=z, **styling_kwargs)
        _, ux, uy, px, py, mx, my = _component_geom(x1, y1, x2, y2)
        ray_len, ray_off = 20, 15
        objects = list(diode.objects)
        for off in (ray_off, ray_off + 8):
            sx, sy = mx + px * off, my + py * off
            objects.append(Line(x1=sx, y1=sy,
                                x2=sx + px * ray_len + ux * 5,
                                y2=sy + py * ray_len + uy * 5,
                                creation=creation, z=z, stroke=color, stroke_width=1.5))
        _add_label(objects, label, mx + px * (ray_off + ray_len + 16),
                   my + py * (ray_off + ray_len + 16), creation, z)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'LED()'

class UnitInterval:
    """A NumberLine from 0 to 1 -- commonly used for probabilities and parameters.
    Convenience wrapper with sensible defaults for [0, 1] range."""
    def __new__(cls, x: float = 360, y=ORIGIN[1], length: float = 600, tick_step: float = 0.1,
                show_labels=True, font_size: float = 18,
                creation: float = 0, z: float = 0, **styling_kwargs):
        from vectormation._composites import NumberLine
        return NumberLine(x_range=(0, 1, tick_step), length=length,
                         x=x, y=y, include_numbers=show_labels,
                         font_size=font_size,
                         creation=creation, z=z, **styling_kwargs)

class Molecule2D(VCollection):
    """Simple 2D molecule visualization from atom positions and bonds.

    atoms: list of (element_symbol, x, y) tuples.
    bonds: list of (i, j, order) tuples (order: 1=single, 2=double, 3=triple).
    """
    _ATOM_COLORS = {
        'C': '#555', 'H': '#fff', 'O': '#FF4444', 'N': '#4444FF',
        'S': '#FFFF00', 'P': '#FF8800', 'F': '#00FF00', 'Cl': '#00FF00',
        'Br': '#882200', 'I': '#8800FF',
    }

    def __init__(self, atoms, bonds=None, scale: float = 80, cx=ORIGIN[0], cy=ORIGIN[1],
                 atom_radius: float = 20, font_size: float = 16, creation: float = 0, z: float = 0):
        objects = []
        self._atom_objects = []
        if bonds:
            for bond in bonds:
                i, j = bond[0], bond[1]
                if i >= len(atoms) or j >= len(atoms):
                    continue
                bond_order = bond[2] if len(bond) > 2 else 1
                ax, ay = cx + atoms[i][1] * scale, cy + atoms[i][2] * scale
                bx, by = cx + atoms[j][1] * scale, cy + atoms[j][2] * scale
                bux, buy = _normalize(bx - ax, by - ay)
                perpx, perpy = -buy * 4, bux * 4
                for k in range(bond_order):
                    offset = (k - (bond_order - 1) / 2) * 1.5
                    objects.append(Line(
                        x1=ax + perpx * offset, y1=ay + perpy * offset,
                        x2=bx + perpx * offset, y2=by + perpy * offset,
                        stroke='#888', stroke_width=2, creation=creation, z=z))
        for elem, ax_pos, ay_pos in atoms:
            sx, sy = cx + ax_pos * scale, cy + ay_pos * scale
            color = self._ATOM_COLORS.get(elem, '#888')
            atom_c = Circle(r=atom_radius, cx=sx, cy=sy,
                            fill=color, fill_opacity=0.9, stroke='#444', stroke_width=1,
                            creation=creation, z=z + 0.1)
            lbl = _label_text(elem, sx, sy, font_size, creation=creation, z=z + 0.2, fill='#fff')
            self._atom_objects.append(atom_c)
            objects.extend([atom_c, lbl])
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return f'Molecule2D({len(self._atom_objects)} atoms)'

class NeuralNetwork(VCollection):
    """Neural network diagram with layers of neurons connected by edges.

    Parameters
    ----------
    layer_sizes : list[int]
        Number of neurons per layer (e.g. [3, 5, 2]).
    cx, cy : float
        Center position.
    width, height : float
        Total diagram dimensions.
    neuron_radius : float
        Radius of each neuron circle.
    neuron_fill : str
        Fill color for neurons.
    edge_color : str
        Stroke color for connecting lines.
    edge_width : float
        Stroke width for connecting lines.
    """

    def __init__(self, layer_sizes, cx=ORIGIN[0], cy=ORIGIN[1], width: float = 800, height: float = 500,
                 neuron_radius: float = 16, neuron_fill='#58C4DD', edge_color='#888',
                 edge_width: float = 1, creation: float = 0, z: float = 0):
        objects = []
        self._layers = []
        n_layers = len(layer_sizes)
        if n_layers < 2:
            super().__init__(creation=creation, z=z)
            return

        # Compute neuron positions
        x_left = cx - width / 2
        x_spacing = width / (n_layers - 1) if n_layers > 1 else 0
        max_neurons = max(layer_sizes)
        y_spacing = height / max(max_neurons - 1, 1) if max_neurons > 1 else 0
        layer_positions = []
        for li, n_neurons in enumerate(layer_sizes):
            lx = x_left + li * x_spacing
            y_top = cy - (n_neurons - 1) * y_spacing / 2
            positions = [(lx, y_top + ni * y_spacing)
                         for ni in range(n_neurons)]
            layer_positions.append(positions)

        # Draw edges first (behind neurons)
        self._edges = []
        for li in range(n_layers - 1):
            for (x1, y1) in layer_positions[li]:
                for (x2, y2) in layer_positions[li + 1]:
                    edge = Line(x1, y1, x2, y2, stroke=edge_color,
                                stroke_width=edge_width, creation=creation, z=z)
                    objects.append(edge)
                    self._edges.append(edge)

        # Draw neurons on top
        for li, positions in enumerate(layer_positions):
            layer_circles = []
            for (nx, ny) in positions:
                neuron = Circle(r=neuron_radius, cx=nx, cy=ny,
                                fill=neuron_fill, fill_opacity=1,
                                stroke='#fff', stroke_width=2,
                                creation=creation, z=z + 0.1)
                objects.append(neuron)
                layer_circles.append(neuron)
            self._layers.append(layer_circles)

        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        sizes = [len(l) for l in self._layers]
        return f'NeuralNetwork({sizes})'

    def _label_layer(self, layer_idx, labels, sign, anchor, font_size: float = 20, buff: float = 30, creation: float = 0, **kwargs):
        """Add labels to one side of a neuron layer."""
        if not self._layers:
            return self
        for neuron, text in zip(self._layers[layer_idx], labels):
            cx, cy = neuron.center(creation)
            self.add(Text(str(text), x=cx + sign * (neuron.rx.at_time(creation) + buff),
                          y=cy, font_size=font_size, text_anchor=anchor,
                          fill='#fff', creation=creation, **kwargs))
        return self

    def label_input(self, labels, font_size: float = 20, buff: float = 30, **kwargs):
        """Add labels to the left of input neurons."""
        return self._label_layer(0, labels, -1, 'end', font_size, buff, **kwargs)

    def label_output(self, labels, font_size: float = 20, buff: float = 30, **kwargs):
        """Add labels to the right of output neurons."""
        return self._label_layer(-1, labels, 1, 'start', font_size, buff, **kwargs)

    def activate(self, layer_idx, neuron_idx, start: float = 0, end: float = 1, color='#FFFF00'):
        """Animate a neuron activation (flash color)."""
        if 0 <= layer_idx < len(self._layers):
            layer = self._layers[layer_idx]
            if 0 <= neuron_idx < len(layer):
                layer[neuron_idx].flash(start=start, end=end, color=color)
        return self

    def propagate(self, start: float = 0, end: float = 1, delay: float = 0.3, color='#FFFF00'):
        """Animate a forward-propagation signal through the network."""
        duration = end - start
        for li, layer in enumerate(self._layers):
            t = start + li * delay
            for neuron in layer:
                neuron.flash(start=t, end=t + duration / len(self._layers),
                             color=color)
        return self

    def highlight_path(self, path, start: float = 0, delay: float = 0.3, color='#FF6B6B',
                       edge_color='#FF6B6B'):
        """Highlight a specific path through the network.

        path : list[int]
            Neuron indices per layer (e.g. [0, 2, 1] for a 3-layer net).
        """
        if len(path) != len(self._layers):
            return self
        n_layers = len(self._layers)
        # Highlight neurons along the path
        for li, ni in enumerate(path):
            t = start + li * delay
            if 0 <= ni < len(self._layers[li]):
                self._layers[li][ni].flash(start=t, end=t + delay, color=color)
        # Highlight edges between consecutive path neurons
        if not self._edges:
            return self
        sizes = [len(layer) for layer in self._layers]
        for li in range(n_layers - 1):
            n1, n2 = path[li], path[li + 1]
            if not (0 <= n1 < sizes[li] and 0 <= n2 < sizes[li + 1]):
                continue
            # Edge index in fully connected layer: n1 * sizes[li+1] + n2
            offset = sum(sizes[i] * sizes[i + 1] for i in range(li))
            edge_idx = offset + n1 * sizes[li + 1] + n2
            if 0 <= edge_idx < len(self._edges):
                t = start + li * delay
                self._edges[edge_idx].flash(start=t, end=t + delay * 2,
                                             color=edge_color)
        return self

class Pendulum(VCollection):
    """Animated pendulum with a pivot, rod, and bob.

    Uses the small-angle approximation or exact solution for animation.

    Parameters
    ----------
    pivot_x, pivot_y : float
        Pivot point position.
    length : float
        Rod length in pixels.
    angle : float
        Initial angle in degrees from vertical.
    bob_radius : float
        Radius of the bob circle.
    period : float
        Oscillation period in seconds.
    damping : float
        Damping factor (0 = no damping, 1 = fully damped).
    start, end : float
        Animation time range.
    """

    def __init__(self, pivot_x=ORIGIN[0], pivot_y: float = 200, length: float = 300, angle: float = 30,
                 bob_radius=20, period=2.0, damping=0.0,
                 start=0, end=5, creation: float = 0, z: float = 0):
        self._pivot_x = pivot_x
        self._pivot_y = pivot_y
        self._length = length
        self._init_angle = math.radians(angle)
        if period <= 0:
            raise ValueError("Pendulum period must be > 0")
        self._period = period
        self._damping = damping
        omega = math.tau / period

        # Pivot dot
        pivot = Dot(r=5, cx=pivot_x, cy=pivot_y, fill='#888',
                    creation=creation, z=z + 0.1)

        # Rod line
        rod = Line(pivot_x, pivot_y, pivot_x, pivot_y + length,
                   stroke='#aaa', stroke_width=3, creation=creation, z=z)

        # Bob
        bob = Circle(r=bob_radius, cx=pivot_x, cy=pivot_y + length,
                     fill='#58C4DD', fill_opacity=1, stroke='#fff',
                     stroke_width=2, creation=creation, z=z + 0.2)

        # Animate bob and rod end
        init_a = self._init_angle
        damp = damping
        px, py = pivot_x, pivot_y
        L = length

        def bob_pos(t, _end=end):
            dt = max(0, min(t, _end) - start)
            a = init_a * math.exp(-damp * dt) * math.cos(omega * dt)
            bx = px + L * math.sin(a)
            by = py + L * math.cos(a)
            return (bx, by)

        bob.c.set_onward(start, bob_pos)
        rod.p2.set_onward(start, bob_pos)

        self.pivot = pivot
        self.rod = rod
        self.bob = bob
        super().__init__(rod, pivot, bob, creation=creation, z=z)

    def __repr__(self):
        return f'Pendulum(length={self._length})'

class StandingWave(VCollection):
    """Animated standing wave between two fixed points.

    Parameters
    ----------
    x1, y1, x2, y2 : float
        Endpoints of the wave.
    amplitude : float
        Maximum displacement in pixels.
    harmonics : int
        Number of half-wavelengths (harmonic number).
    frequency : float
        Oscillation frequency in Hz.
    num_points : int
        Number of sample points along the wave.
    start, end : float
        Animation time range.
    """

    def __init__(self, x1: float = 300, y1=ORIGIN[1], x2: float = 1620, y2=ORIGIN[1],
                 amplitude=100, harmonics=3, frequency=1.0, num_points=200,
                 start=0, end=5, creation: float = 0, z: float = 0, **kwargs):
        wave_length = math.hypot(x2 - x1, y2 - y1)
        dx_norm = (x2 - x1) / wave_length if wave_length else 1
        dy_norm = (y2 - y1) / wave_length if wave_length else 0
        perp_x, perp_y = -dy_norm, dx_norm
        omega = math.tau * frequency
        k = harmonics * math.pi / wave_length if wave_length else 0

        # Fixed endpoint dots
        dot1 = Dot(r=6, cx=x1, cy=y1, fill='#888', creation=creation, z=z + 0.1)
        dot2 = Dot(r=6, cx=x2, cy=y2, fill='#888', creation=creation, z=z + 0.1)

        # Wave path
        wave = Path('', creation=creation, z=z,
                    stroke=kwargs.get('stroke', '#58C4DD'),
                    stroke_width=kwargs.get('stroke_width', 3),
                    fill_opacity=0)

        def wave_d(t, _x1=x1, _y1=y1, _a=amplitude,
                   _px=perp_x, _py=perp_y, _dx=dx_norm, _dy=dy_norm,
                   _wl=wave_length, _np=num_points, _start=start, _end=end):
            dt = max(0, min(t, _end) - _start)
            parts = [f'M {_x1:.1f} {_y1:.1f}']
            for i in range(1, _np):
                s = i / _np
                dist = s * _wl
                bx = _x1 + _dx * dist
                by = _y1 + _dy * dist
                disp = _a * math.sin(k * dist) * math.cos(omega * dt)
                px = bx + _px * disp
                py = by + _py * disp
                parts.append(f'L {px:.1f} {py:.1f}')
            parts.append(f'L {x2:.1f} {y2:.1f}')
            return ' '.join(parts)

        wave.d.set_onward(start, wave_d)

        self.dot1 = dot1
        self.dot2 = dot2
        self.wave = wave
        super().__init__(wave, dot1, dot2, creation=creation, z=z)

    def __repr__(self):
        return 'StandingWave()'


# ---------------------------------------------------------------------------
# Electrostatics
# ---------------------------------------------------------------------------

class Charge(VCollection):
    """Electrostatic point charge with a colored circle and +/- symbol.

    Parameters
    ----------
    magnitude : float
        Charge strength.  Positive values draw a red "+" charge,
        negative values draw a blue "-" charge.
    cx, cy : float
        Position in SVG coordinates.
    radius : float or None
        Circle radius.  ``None`` auto-scales from magnitude.
    color : str or None
        Override the automatic red/blue color.
    add_glow : bool
        If *True*, concentric translucent circles create a glow effect.
    glow_layers : int
        Number of glow rings (more = smoother but heavier).
    """

    def __init__(self, magnitude: float = 1, cx=ORIGIN[0], cy=ORIGIN[1], radius=None,
                 color=None, add_glow=True, glow_layers=12,
                 creation: float = 0, z: float = 0, **styling_kwargs):
        self.magnitude = magnitude
        self._cx = cx
        self._cy = cy
        is_positive = magnitude >= 0
        if radius is None:
            radius = min(abs(magnitude) * 16, 40) if abs(magnitude) < 5 else 40
            radius = max(radius, 10)
        self._radius = radius
        if color is None:
            color = '#FF4444' if is_positive else '#4488FF'
        self._color = color

        objects = []

        # Glow rings (back to front, decreasing opacity)
        if add_glow:
            glow_max_r = radius * 3.5
            from vectormation.colors import color_gradient as _cg
            if is_positive:
                glow_colors = _cg('#FF4444', '#FFAAAA', glow_layers)
            else:
                glow_colors = _cg('#4488FF', '#AACCFF', glow_layers)
            for i in range(glow_layers):
                t = (i + 1) / glow_layers
                gr = radius + (glow_max_r - radius) * t
                opacity = 0.25 * (1 - t) ** 1.5
                objects.append(Circle(r=gr, cx=cx, cy=cy,
                                      fill=glow_colors[i], fill_opacity=opacity,
                                      stroke_width=0, creation=creation, z=z))

        # Main circle
        objects.append(Circle(r=radius, cx=cx, cy=cy,
                              fill=color, fill_opacity=1,
                              stroke='#fff', stroke_width=2,
                              creation=creation, z=z + 0.1))

        # +/- symbol
        bar_w = radius * 0.8
        bar_h = radius * 0.15
        if is_positive:
            # Horizontal bar
            objects.append(Rectangle(bar_w, bar_h, x=cx, y=cy,
                                     fill='#fff', fill_opacity=1, stroke_width=0,
                                     creation=creation, z=z + 0.2))
            # Vertical bar
            objects.append(Rectangle(bar_h, bar_w, x=cx, y=cy,
                                     fill='#fff', fill_opacity=1, stroke_width=0,
                                     creation=creation, z=z + 0.2))
        else:
            # Just horizontal bar for minus
            objects.append(Rectangle(bar_w, bar_h, x=cx, y=cy,
                                     fill='#fff', fill_opacity=1, stroke_width=0,
                                     creation=creation, z=z + 0.2))

        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        sign = '+' if self.magnitude >= 0 else ''
        return f'Charge({sign}{self.magnitude})'


class ElectricField(VCollection):
    """Electric field visualization from a list of Charge objects.

    Computes the Coulomb field at grid points and renders arrows via
    ArrowVectorField from ``_svg_utils``.

    Parameters
    ----------
    charges : Charge
        One or more Charge instances (positional args).
    x_range, y_range : tuple
        Grid sampling ranges as ``(min, max, step)`` in SVG pixels.
    max_length : float
        Maximum arrow length in pixels.
    color : str
        Arrow color.
    """

    def __init__(self, *charges, x_range=(60, CANVAS_WIDTH - 60, 120),
                 y_range=(60, CANVAS_HEIGHT - 60, 120),
                 max_length=80, color='#58C4DD',
                 creation: float = 0, z: float = 0, **styling_kwargs):
        self.charges = charges
        # Collect positions and magnitudes
        positions = []
        magnitudes = []
        for ch in charges:
            positions.append((ch._cx, ch._cy))
            magnitudes.append(ch.magnitude)

        def field_func(x, y):
            """Coulomb superposition: E = sum(q / r^2 * r_hat)."""
            fx, fy = 0.0, 0.0
            for (px, py), mag in zip(positions, magnitudes):
                dx, dy = x - px, y - py
                dist = math.hypot(dx, dy)
                if dist < 15:  # avoid singularity near charge
                    return (0.0, 0.0)
                nx, ny = dx / dist, dy / dist
                fx += mag / dist ** 2 * nx
                fy += mag / dist ** 2 * ny
            return (fx, fy)

        from vectormation._svg_utils import ArrowVectorField
        avf = ArrowVectorField(field_func, x_range=x_range, y_range=y_range,
                               max_length=max_length, creation=creation, z=z,
                               stroke=color, **styling_kwargs)
        super().__init__(*avf.objects, creation=creation, z=z)

    def __repr__(self):
        return f'ElectricField({len(self.charges)} charges)'


# ---------------------------------------------------------------------------
# Optics
# ---------------------------------------------------------------------------

class Lens(VCollection):
    """Convex or concave lens shape for geometric optics diagrams.

    Parameters
    ----------
    cx, cy : float
        Center position.
    height : float
        Lens height (top to bottom) in pixels.
    focal_length : float
        Focal length in pixels.  Positive = convex, negative = concave.
    thickness : float
        Maximum lens thickness in pixels.
    n : float
        Refractive index (used by Ray for Snell's law).
    color : str
        Fill color.
    show_focal_points : bool
        Draw small dots at the focal points.
    show_axis : bool
        Draw the principal (optical) axis as a dashed line.
    """

    def __init__(self, cx=ORIGIN[0], cy=ORIGIN[1], height: float = 300,
                 focal_length: float = 200, thickness: float = 30, n: float = 1.52,
                 color='#58C4DD', show_focal_points=True, show_axis=True,
                 creation: float = 0, z: float = 0, **styling_kwargs):
        self._cx = cx
        self._cy = cy
        self._height = height
        self.focal_length = focal_length
        self._thickness = thickness
        self.n = n
        self._is_convex = focal_length > 0

        objects = []

        half_h = height / 2
        half_t = thickness / 2

        if self._is_convex:
            # Convex lens: two outward arcs forming a biconvex shape.
            # Approximate with cubic bezier curves.
            d = (
                f'M {cx},{cy - half_h} '
                f'C {cx + half_t * 2.2},{cy - half_h * 0.3} '
                f'  {cx + half_t * 2.2},{cy + half_h * 0.3} '
                f'  {cx},{cy + half_h} '
                f'C {cx - half_t * 2.2},{cy + half_h * 0.3} '
                f'  {cx - half_t * 2.2},{cy - half_h * 0.3} '
                f'  {cx},{cy - half_h} Z'
            )
        else:
            # Concave lens: thin at center, thick at edges.
            edge_t = half_t * 2.0
            center_t = half_t * 0.3
            d = (
                # Left edge outline
                f'M {cx - edge_t},{cy - half_h} '
                f'L {cx + edge_t},{cy - half_h} '
                # Right concave curve (inward)
                f'C {cx + center_t},{cy - half_h * 0.3} '
                f'  {cx + center_t},{cy + half_h * 0.3} '
                f'  {cx + edge_t},{cy + half_h} '
                # Bottom edge
                f'L {cx - edge_t},{cy + half_h} '
                # Left concave curve (inward)
                f'C {cx - center_t},{cy + half_h * 0.3} '
                f'  {cx - center_t},{cy - half_h * 0.3} '
                f'  {cx - edge_t},{cy - half_h} Z'
            )

        lens_path = Path(d, x=0, y=0, fill=color, fill_opacity=0.3,
                         stroke=color, stroke_width=2,
                         creation=creation, z=z + 0.1)
        objects.append(lens_path)

        # Optical axis (dashed horizontal line)
        if show_axis:
            axis_half = max(abs(focal_length) * 2, height)
            objects.append(Line(cx - axis_half, cy, cx + axis_half, cy,
                                stroke='#666', stroke_width=1,
                                stroke_dasharray='8 4',
                                creation=creation, z=z))

        # Focal points
        if show_focal_points:
            f_abs = abs(focal_length)
            objects.append(Dot(r=4, cx=cx - f_abs, cy=cy,
                               fill='#FFFF00', creation=creation, z=z + 0.2))
            objects.append(Dot(r=4, cx=cx + f_abs, cy=cy,
                               fill='#FFFF00', creation=creation, z=z + 0.2))
            objects.append(Text('F', x=cx - f_abs, y=cy + 20, font_size=16,
                                fill='#FFFF00', stroke_width=0,
                                text_anchor='middle',
                                creation=creation, z=z + 0.2))
            objects.append(Text('F', x=cx + f_abs, y=cy + 20, font_size=16,
                                fill='#FFFF00', stroke_width=0,
                                text_anchor='middle',
                                creation=creation, z=z + 0.2))

        self.lens_path = lens_path
        super().__init__(*objects, creation=creation, z=z)

    def image_point(self, obj_x, obj_y):
        """Compute the image position of a point object using the thin-lens equation.

        Returns (image_x, image_y) in SVG coordinates, or None if the object
        is exactly at the focal point (image at infinity).
        """
        f = self.focal_length
        # Object distance (positive = left of lens in standard convention)
        do = self._cx - obj_x
        if abs(do) < 1e-9:
            # Object at the lens center -- passes through
            return (obj_x, obj_y)
        # Thin-lens equation: 1/f = 1/do + 1/di  =>  di = f*do / (do - f)
        denom = do - f
        if abs(denom) < 1e-9:
            return None  # image at infinity
        di = f * do / denom
        magnification = -di / do
        image_x = self._cx + di
        image_y = self._cy + (obj_y - self._cy) * magnification
        return (image_x, image_y)

    def __repr__(self):
        kind = 'convex' if self._is_convex else 'concave'
        return f'Lens({kind}, f={self.focal_length})'


class Ray(VCollection):
    """A light ray that propagates and refracts through Lens objects.

    Parameters
    ----------
    x1, y1 : float
        Starting point of the ray.
    angle : float
        Initial direction in degrees (0 = rightward, 90 = downward).
    length : float
        Initial ray segment length in pixels.
    lenses : list[Lens] or None
        Lenses to propagate through.  Refraction uses Snell's law
        at each lens surface.
    color : str
        Ray stroke color.
    stroke_width : float
        Ray line width.
    show_arrow : bool
        Draw a small arrowhead at the ray tip.
    """

    def __init__(self, x1: float = 200, y1=ORIGIN[1], angle: float = 0, length: float = 1600,
                 lenses=None, color='#FFFF00', stroke_width: float = 2,
                 show_arrow=False,
                 creation: float = 0, z: float = 0, **styling_kwargs):
        self._x1 = x1
        self._y1 = y1
        self._angle = angle
        self._length = length
        self._color = color

        angle_rad = math.radians(angle)
        dx = math.cos(angle_rad)
        dy = math.sin(angle_rad)

        objects = []
        style_kw = {'stroke': color, 'stroke_width': stroke_width,
                     'fill_opacity': 0} | styling_kwargs

        if not lenses:
            # Simple straight ray
            x2 = x1 + dx * length
            y2 = y1 + dy * length
            objects.append(Line(x1, y1, x2, y2, creation=creation, z=z, **style_kw))
            if show_arrow:
                objects.extend(self._arrowhead(x2, y2, dx, dy, color, creation, z))
        else:
            # Sort lenses by intersection distance along the ray
            sorted_lenses = self._sort_lenses(x1, y1, dx, dy, lenses)
            segments = self._trace(x1, y1, dx, dy, length, sorted_lenses)
            for seg in segments:
                objects.append(Lines(*seg, creation=creation, z=z, **style_kw))
            if show_arrow and segments:
                last_seg = segments[-1]
                if len(last_seg) >= 2:
                    (ax, ay), (bx, by) = last_seg[-2], last_seg[-1]
                    adx, ady = _normalize(bx - ax, by - ay)
                    objects.extend(self._arrowhead(bx, by, adx, ady,
                                                   color, creation, z))

        self.segments = objects
        super().__init__(*objects, creation=creation, z=z)

    @staticmethod
    def _arrowhead(x, y, dx, dy, color, creation, z):
        """Return two short Lines forming a small arrowhead at (x, y)."""
        tip_len = 12
        px, py = -dy, dx  # perpendicular
        ax1 = x - dx * tip_len + px * tip_len * 0.4
        ay1 = y - dy * tip_len + py * tip_len * 0.4
        ax2 = x - dx * tip_len - px * tip_len * 0.4
        ay2 = y - dy * tip_len - py * tip_len * 0.4
        return [
            Line(x, y, ax1, ay1, stroke=color, stroke_width=2,
                 creation=creation, z=z + 0.1),
            Line(x, y, ax2, ay2, stroke=color, stroke_width=2,
                 creation=creation, z=z + 0.1),
        ]

    @staticmethod
    def _sort_lenses(x1, y1, dx, dy, lenses):
        """Sort lenses by distance of their center projected onto the ray."""
        dists = []
        for lens in lenses:
            # Project lens center onto the ray direction
            t = (lens._cx - x1) * dx + (lens._cy - y1) * dy
            dists.append((t, lens))
        dists.sort(key=lambda pair: pair[0])
        return [lens for _, lens in dists]

    @staticmethod
    def _intersect_ray_lens(rx, ry, dx, dy, lens):
        """Find where the ray hits the lens vertical extent.

        Returns the parameter t along the ray where the ray crosses
        the lens center x-coordinate, or None if it doesn't hit.
        """
        # Treat the lens as a vertical slab at x = lens._cx
        if abs(dx) < 1e-12:
            return None  # ray is vertical, parallel to lens
        t = (lens._cx - rx) / dx
        if t < 1:
            return None  # lens is behind the ray origin
        hit_y = ry + dy * t
        half_h = lens._height / 2
        if abs(hit_y - lens._cy) > half_h:
            return None  # misses the lens vertically
        return t

    @staticmethod
    def _refract(dx, dy, focal_length, hit_y, lens_cy):
        """Apply thin-lens refraction to the ray direction.

        For a thin lens, a ray at height h from the axis is deflected by
        angle = -h / f (paraxial approximation).
        """
        h = hit_y - lens_cy
        # Deflection angle from thin-lens formula
        if abs(focal_length) < 1e-9:
            return dx, dy
        deflection = -h / focal_length
        # Rotate direction vector by deflection angle
        cos_d = math.cos(deflection)
        sin_d = math.sin(deflection)
        # For a horizontal lens, the deflection is in the y-component
        # But we use a proper 2D rotation for generality
        new_dx = dx * cos_d - dy * sin_d
        new_dy = dx * sin_d + dy * cos_d
        mag = math.hypot(new_dx, new_dy)
        if mag > 0:
            new_dx /= mag
            new_dy /= mag
        return new_dx, new_dy

    @classmethod
    def _trace(cls, x1, y1, dx, dy, length, lenses):
        """Trace a ray through a list of lenses, returning polyline segments."""
        segments = []
        cur_x, cur_y = x1, y1
        cur_dx, cur_dy = dx, dy
        remaining = length

        for lens in lenses:
            t = cls._intersect_ray_lens(cur_x, cur_y, cur_dx, cur_dy, lens)
            if t is None or t > remaining:
                continue
            # Point where ray enters the lens
            hit_x = cur_x + cur_dx * t
            hit_y = cur_y + cur_dy * t
            # Segment before the lens
            segments.append([(cur_x, cur_y), (hit_x, hit_y)])
            remaining -= t
            # Refract through the lens
            cur_dx, cur_dy = cls._refract(
                cur_dx, cur_dy, lens.focal_length,
                hit_y, lens._cy,
            )
            cur_x, cur_y = hit_x, hit_y

        # Final segment after the last lens (or the only segment)
        end_x = cur_x + cur_dx * remaining
        end_y = cur_y + cur_dy * remaining
        segments.append([(cur_x, cur_y), (end_x, end_y)])
        return segments

    def __repr__(self):
        return f'Ray(angle={self._angle})'
