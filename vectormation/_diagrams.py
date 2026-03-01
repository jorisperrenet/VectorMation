"""Diagram classes: Tree, FlowChart, NetworkGraph, Automaton, etc."""
import math
from collections import deque
import vectormation.easings as easings
from vectormation._constants import (
    ORIGIN, DEFAULT_CHART_COLORS,
    TEXT_Y_OFFSET, _normalize, _label_text, _get_arrow,
)
from vectormation._base import VCollection
from vectormation._shapes import (
    Circle, Dot, Rectangle, RoundedRectangle, Line,
    Text, Path, Arc,
)

_SPRING_ITERATIONS = 50
_REPULSION_STRENGTH = 5000
_ATTRACTION_STRENGTH = 0.01
_POSITION_DAMPING = 0.1
_ELECTRON_SHELL_CAPS = (2, 8, 8, 18, 18, 32)
_LABEL_OFFSET = 15  # perpendicular offset for edge labels

def _apply_force(forces, a, b, fx, fy):
    """Apply equal-and-opposite force between nodes *a* and *b*."""
    forces[a][0] += fx
    forces[a][1] += fy
    forces[b][0] -= fx
    forces[b][1] -= fy

def _shortened_endpoints(x1, y1, x2, y2, r1, r2):
    """Shorten a line segment by r1 at the start and r2 at the end."""
    ux, uy = _normalize(x2 - x1, y2 - y1)
    return (x1 + ux * r1, y1 + uy * r1, x2 - ux * r2, y2 - uy * r2)

_DIAGRAM_TIP = {'tip_length': 12, 'tip_width': 10}


def _make_node_circle(r, cx, cy, creation, z, fill='#1e1e2e', stroke='#58C4DD'):
    """Create a styled node circle for diagrams."""
    return Circle(r=r, cx=cx, cy=cy, creation=creation, z=z,
                  fill=fill, fill_opacity=0.9, stroke=stroke, stroke_width=2)


def _highlight_in_dict(obj_dict, key, start, end, color, easing):
    """Flash-highlight an object looked up by key in a dict."""
    if key in obj_dict:
        obj_dict[key].flash(start, end, color=color, easing=easing)


def _circular_layout(keys, cx, cy, radius):
    """Return dict mapping each key to (x, y) evenly spaced on a circle."""
    n = max(len(keys), 1)
    return {k: (cx + radius * math.cos(math.tau * i / n - math.pi / 2),
                cy + radius * math.sin(math.tau * i / n - math.pi / 2))
            for i, k in enumerate(keys)}

# ---------------------------------------------------------------------------
# ChessBoard
# ---------------------------------------------------------------------------

class ChessBoard(VCollection):
    """Chess board visualization."""
    _PIECE_SYMBOLS = {
        'K': '\u2654', 'Q': '\u2655', 'R': '\u2656', 'B': '\u2657', 'N': '\u2658', 'P': '\u2659',
        'k': '\u265a', 'q': '\u265b', 'r': '\u265c', 'b': '\u265d', 'n': '\u265e', 'p': '\u265f',
    }

    def __init__(self, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR',
                 cx=ORIGIN[0], cy=ORIGIN[1], size=600, show_coordinates=True,
                 light_color='#f0d9b5', dark_color='#b58863',
                 creation: float = 0, z: float = 0):
        cell = size / 8
        x0 = cx - size / 2
        y0 = cy - size / 2
        objects = []
        self._pieces = {}
        self._cell = cell
        self._x0, self._y0 = x0, y0

        # Draw squares
        for row in range(8):
            for col in range(8):
                color = light_color if (row + col) % 2 == 0 else dark_color
                sq = Rectangle(cell, cell, x=x0 + col * cell, y=y0 + row * cell,
                               creation=creation, z=z,
                               fill=color, fill_opacity=1, stroke_width=0)
                objects.append(sq)

        # Coordinate labels
        if show_coordinates:
            for col in range(8):
                lbl = Text(text=chr(ord('a') + col),
                           x=x0 + col * cell + cell / 2,
                           y=y0 + size + 18,
                           font_size=16, text_anchor='middle',
                           creation=creation, z=z, fill='#aaa', stroke_width=0)
                objects.append(lbl)
            for row in range(8):
                lbl = Text(text=str(8 - row),
                           x=x0 - 14,
                           y=y0 + row * cell + cell / 2 + 6,
                           font_size=16, text_anchor='middle',
                           creation=creation, z=z, fill='#aaa', stroke_width=0)
                objects.append(lbl)

        # Place pieces from FEN
        rows = fen.split('/')
        for row_idx, row_str in enumerate(rows):
            col_idx = 0
            for ch in row_str:
                if ch.isdigit():
                    col_idx += int(ch)
                elif ch in self._PIECE_SYMBOLS:
                    px = x0 + col_idx * cell + cell / 2
                    py = y0 + row_idx * cell + cell / 2 + cell * 0.1
                    piece = Text(text=self._PIECE_SYMBOLS[ch],
                                 x=px, y=py, font_size=cell * 0.7,
                                 text_anchor='middle',
                                 creation=creation, z=z + 1,
                                 fill='#fff' if ch.isupper() else '#222',
                                 stroke_width=0)
                    sq_name = chr(ord('a') + col_idx) + str(8 - row_idx)
                    self._pieces[sq_name] = piece
                    objects.append(piece)
                    col_idx += 1

        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return f'ChessBoard({len(self._pieces)} pieces)'

    @staticmethod
    def _sq_to_idx(sq):
        """Convert algebraic notation (e.g. 'e4') to (col, row) indices."""
        return ord(sq[0]) - ord('a'), 8 - int(sq[1])

    def move_piece(self, from_sq, to_sq, start: float = 0, end: float = 1, easing=easings.smooth):
        """Animate moving a piece from one square to another (e.g. 'e2' -> 'e4')."""
        piece = self._pieces.get(from_sq)
        if piece is None:
            return self
        fc, fr = self._sq_to_idx(from_sq)
        tc, tr = self._sq_to_idx(to_sq)
        piece.shift(dx=(tc - fc) * self._cell, dy=(tr - fr) * self._cell,
                    start=start, end=end, easing=easing)
        self._pieces[to_sq] = piece
        del self._pieces[from_sq]
        return self

# ---------------------------------------------------------------------------
# PeriodicTable + helper
# ---------------------------------------------------------------------------

_ELEMENT_DATA = [
    (1, 'H', 'Hydrogen', 1, 1), (2, 'He', 'Helium', 18, 1),
    (3, 'Li', 'Lithium', 1, 2), (4, 'Be', 'Beryllium', 2, 2),
    (5, 'B', 'Boron', 13, 2), (6, 'C', 'Carbon', 14, 2),
    (7, 'N', 'Nitrogen', 15, 2), (8, 'O', 'Oxygen', 16, 2),
    (9, 'F', 'Fluorine', 17, 2), (10, 'Ne', 'Neon', 18, 2),
    (11, 'Na', 'Sodium', 1, 3), (12, 'Mg', 'Magnesium', 2, 3),
    (13, 'Al', 'Aluminium', 13, 3), (14, 'Si', 'Silicon', 14, 3),
    (15, 'P', 'Phosphorus', 15, 3), (16, 'S', 'Sulfur', 16, 3),
    (17, 'Cl', 'Chlorine', 17, 3), (18, 'Ar', 'Argon', 18, 3),
    (19, 'K', 'Potassium', 1, 4), (20, 'Ca', 'Calcium', 2, 4),
    (21, 'Sc', 'Scandium', 3, 4), (22, 'Ti', 'Titanium', 4, 4),
    (23, 'V', 'Vanadium', 5, 4), (24, 'Cr', 'Chromium', 6, 4),
    (25, 'Mn', 'Manganese', 7, 4), (26, 'Fe', 'Iron', 8, 4),
    (27, 'Co', 'Cobalt', 9, 4), (28, 'Ni', 'Nickel', 10, 4),
    (29, 'Cu', 'Copper', 11, 4), (30, 'Zn', 'Zinc', 12, 4),
    (31, 'Ga', 'Gallium', 13, 4), (32, 'Ge', 'Germanium', 14, 4),
    (33, 'As', 'Arsenic', 15, 4), (34, 'Se', 'Selenium', 16, 4),
    (35, 'Br', 'Bromine', 17, 4), (36, 'Kr', 'Krypton', 18, 4),
]

_CATEGORY_COLORS = {
    'nonmetal': '#58C4DD', 'noble_gas': '#9A72AC', 'alkali': '#FC6255',
    'alkaline': '#F0AC5F', 'metalloid': '#5CD0B3', 'halogen': '#FFFF00',
    'transition': '#C55F73', 'post_transition': '#83C167',
}

def _element_category(z):
    if z in (1, 6, 7, 8, 15, 16, 34): return 'nonmetal'
    if z in (2, 10, 18, 36): return 'noble_gas'
    if z in (3, 11, 19): return 'alkali'
    if z in (4, 12, 20): return 'alkaline'
    if z in (5, 14, 32, 33): return 'metalloid'
    if z in (9, 17, 35): return 'halogen'
    if 21 <= z <= 30: return 'transition'
    return 'post_transition'

class PeriodicTable(VCollection):
    """Periodic table of elements (first 36 elements)."""
    def __init__(self, cx=ORIGIN[0], cy=ORIGIN[1], cell_size=48, creation: float = 0, z: float = 0):
        objects = []
        total_w = 18 * cell_size
        total_h = 4 * cell_size
        x0 = cx - total_w / 2
        y0 = cy - total_h / 2

        self._cells = {}
        for atomic_num, symbol, _name, col, row in _ELEMENT_DATA:
            cat = _element_category(atomic_num)
            color = _CATEGORY_COLORS.get(cat, '#888')
            ex = x0 + (col - 1) * cell_size
            ey = y0 + (row - 1) * cell_size
            bg = Rectangle(cell_size - 2, cell_size - 2, x=ex + 1, y=ey + 1,
                           creation=creation, z=z,
                           fill=color, fill_opacity=0.3, stroke=color, stroke_width=1)
            objects.append(bg)
            num_t = Text(text=str(atomic_num), x=ex + 4, y=ey + 12,
                         font_size=10, creation=creation, z=z,
                         fill='#aaa', stroke_width=0)
            objects.append(num_t)
            sym_t = Text(text=symbol, x=ex + cell_size / 2, y=ey + cell_size / 2 + 4,
                         font_size=18, text_anchor='middle',
                         creation=creation, z=z, fill='#fff', stroke_width=0)
            objects.append(sym_t)
            self._cells[symbol] = (bg, num_t, sym_t)

        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'PeriodicTable()'

    def highlight(self, symbol, start: float = 0, end: float = 1, color='#FFFF00', easing=easings.there_and_back):
        """Highlight an element by symbol."""
        if symbol in self._cells:
            bg, _, sym = self._cells[symbol]
            bg.indicate(start, end, easing=easing)
            sym.flash(start, end, color=color, easing=easing)
        return self

# ---------------------------------------------------------------------------
# BohrAtom
# ---------------------------------------------------------------------------

class BohrAtom(VCollection):
    """Bohr model of an atom with electron shells."""
    def __init__(self, protons=1, neutrons=0, electrons=None, cx=ORIGIN[0], cy=ORIGIN[1],
                 nucleus_r=30, shell_spacing=40, creation: float = 0, z: float = 0):
        objects = []

        # Nucleus
        nucleus = Circle(r=nucleus_r, cx=cx, cy=cy, creation=creation, z=z + 1,
                         fill='#FC6255', fill_opacity=0.8, stroke='#fff', stroke_width=2)
        objects.append(nucleus)
        nucleus_text = f'{protons}p\u207a' if neutrons == 0 else f'{protons}p {neutrons}n'
        label = Text(text=nucleus_text, x=cx, y=cy + 6,
                     font_size=max(10, nucleus_r * 0.5), text_anchor='middle',
                     creation=creation, z=z + 2, fill='#fff', stroke_width=0)
        objects.append(label)

        if electrons is None:
            # Auto-fill shells: 2, 8, 8, 18, ...
            remaining = protons
            electrons = []
            for cap in _ELECTRON_SHELL_CAPS:
                if remaining <= 0:
                    break
                electrons.append(min(remaining, cap))
                remaining -= electrons[-1]

        # Electron shells
        self._electron_dots = []
        for shell_idx, n_electrons in enumerate(electrons):
            r = nucleus_r + (shell_idx + 1) * shell_spacing
            orbit = Circle(r=r, cx=cx, cy=cy, creation=creation, z=z,
                           fill_opacity=0, stroke='#58C4DD', stroke_width=1, stroke_opacity=0.4)
            objects.append(orbit)
            for e in range(n_electrons):
                angle = math.tau * e / n_electrons
                ex = cx + r * math.cos(angle)
                ey = cy - r * math.sin(angle)
                dot = Dot(r=5, cx=ex, cy=ey, creation=creation, z=z + 1,
                          fill='#58C4DD', fill_opacity=1)
                objects.append(dot)
                self._electron_dots.append(dot)

        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return f'BohrAtom({len(self._electron_dots)} electrons)'

    def orbit(self, start: float = 0, end: float | None = None, speed=45):
        """Animate all electrons orbiting around the nucleus."""
        for dot in self._electron_dots:
            dot.always_rotate(start=start, end=end, degrees_per_second=speed)
        return self

# ---------------------------------------------------------------------------
# Automaton
# ---------------------------------------------------------------------------

class Automaton(VCollection):
    """Finite state machine / automaton visualization."""
    def __init__(self, states, transitions, accept_states=None, initial_state=None,
                 cx=ORIGIN[0], cy=ORIGIN[1], radius=300, state_r=35, font_size=20,
                 creation: float = 0, z: float = 0):
        Arrow = _get_arrow()
        objects = []
        accept_states = accept_states or set()
        n = len(states)
        self._state_positions = {}
        self._state_circles = {}
        self._transitions = list(transitions)
        self._transition_arrows = {}
        self._accept_states = set(accept_states)
        self._initial_state = initial_state
        if n == 0:
            super().__init__(creation=creation, z=z)
            return

        # Arrange states in a circle
        self._state_positions = _circular_layout(states, cx, cy, radius)
        for name in states:
            sx, sy = self._state_positions[name]
            circle = _make_node_circle(state_r, sx, sy, creation, z)
            objects.append(circle)
            self._state_circles[name] = circle

            if name in accept_states:
                inner = Circle(r=state_r - 5, cx=sx, cy=sy, creation=creation, z=z,
                               fill_opacity=0, stroke='#58C4DD', stroke_width=2)
                objects.append(inner)

            label = Text(text=name, x=sx, y=sy + font_size * TEXT_Y_OFFSET,
                         font_size=font_size, text_anchor='middle',
                         creation=creation, z=z + 1, fill='#fff', stroke_width=0)
            objects.append(label)

        # Initial state arrow
        if initial_state and initial_state in self._state_positions:
            sx, sy = self._state_positions[initial_state]
            objects.append(Arrow(x1=sx - state_r - 50, y1=sy, x2=sx - state_r - 2, y2=sy,
                                 **_DIAGRAM_TIP, creation=creation, z=z, stroke='#fff', stroke_width=2))

        # Transitions
        for from_s, to_s, label_text in transitions:
            if from_s not in self._state_positions or to_s not in self._state_positions:
                continue
            fx, fy = self._state_positions[from_s]
            tx, ty = self._state_positions[to_s]

            if from_s == to_s:
                # Self-loop: arc above the state
                loop_r = state_r * 0.8
                loop = Arc(cx=fx, cy=fy - state_r - loop_r, r=loop_r,
                           start_angle=210, end_angle=330,
                           creation=creation, z=z, stroke='#83C167', stroke_width=2)
                objects.append(loop)
                self._transition_arrows[(from_s, to_s)] = loop
                lbl = Text(text=label_text, x=fx, y=fy - state_r - loop_r * 2 - 8,
                           font_size=font_size * 0.8, text_anchor='middle',
                           creation=creation, z=z + 1, fill='#83C167', stroke_width=0)
                objects.append(lbl)
            else:
                sx, sy, ex, ey = _shortened_endpoints(fx, fy, tx, ty, state_r, state_r)
                arrow = Arrow(x1=sx, y1=sy, x2=ex, y2=ey,
                              **_DIAGRAM_TIP, creation=creation, z=z, stroke='#83C167', stroke_width=2)
                objects.append(arrow)
                self._transition_arrows[(from_s, to_s)] = arrow
                mx, my = (sx + ex) / 2, (sy + ey) / 2
                # Offset label perpendicular to arrow
                ux, uy = _normalize(tx - fx, ty - fy)
                px, py = -uy * _LABEL_OFFSET, ux * _LABEL_OFFSET
                lbl = Text(text=label_text, x=mx + px, y=my + py + font_size * TEXT_Y_OFFSET,
                           font_size=font_size * 0.8, text_anchor='middle',
                           creation=creation, z=z + 1, fill='#83C167', stroke_width=0)
                objects.append(lbl)

        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return f'Automaton({len(self._state_positions)} states)'

    def highlight_state(self, state_name, start: float = 0, end: float = 1, color='#FFFF00', easing=easings.there_and_back):
        """Highlight a state by flashing its circle."""
        _highlight_in_dict(self._state_circles, state_name, start, end, color, easing)
        return self

    def highlight_transition(self, from_state, to_state, start: float = 0, end: float = 1, color='#FFFF00'):
        """Highlight the arrow between from_state and to_state by flashing its color."""
        arrow = self._transition_arrows.get((from_state, to_state))
        if arrow is None:
            return self
        duration = max(end - start, 0)
        # Arrow is a VCollection (shaft + tip); Arc is a VObject — handle both
        if hasattr(arrow, 'shaft'):
            arrow.shaft.flash_color(color, start=start, end=start + duration, attr='stroke')
            arrow.tip.flash_color(color, start=start, end=start + duration, attr='fill')
        else:
            # Arc (self-loop): flash the stroke color
            arrow.flash_color(color, start=start, end=start + duration, attr='stroke')
        return self

    def simulate_input(self, word, start: float = 0, delay=0.5, color='#FFFF00', transitions=None):
        """Animate stepping through the automaton one character at a time.

        For each character in *word*, highlights the current state, then the
        transition arrow, then the next state.  If no transition exists the
        current state is highlighted red (rejected).  At the end the final
        state is highlighted green if it is an accept state, red otherwise.
        """
        trans_list = transitions if transitions is not None else self._transitions
        # Build lookup: (state, char) -> next_state
        lookup = {}
        for from_s, to_s, label in trans_list:
            lookup[(from_s, label)] = to_s

        current = self._initial_state
        if current is None:
            raise ValueError("simulate_input requires an initial_state")
        t = start

        for ch in word:
            # Highlight current state
            self.highlight_state(current, start=t, end=t + delay, color=color)
            t += delay

            next_state = lookup.get((current, ch))
            if next_state is None:
                # No transition — reject
                self.highlight_state(current, start=t, end=t + delay, color='#FF0000')
                return self

            # Highlight transition arrow
            self.highlight_transition(current, next_state, start=t, end=t + delay, color=color)
            t += delay

            # Highlight next state arriving
            self.highlight_state(next_state, start=t, end=t + delay, color=color)
            t += delay
            current = next_state

        # Final state: green if accept, red if reject
        final_color = '#00FF00' if current in self._accept_states else '#FF0000'
        self.highlight_state(current, start=t, end=t + delay, color=final_color)
        return self

# ---------------------------------------------------------------------------
# NetworkGraph
# ---------------------------------------------------------------------------

class NetworkGraph(VCollection):
    """Network/graph visualization with nodes and edges."""
    def __init__(self, nodes, edges=None, cx=ORIGIN[0], cy=ORIGIN[1], radius=300,
                 node_r=30, font_size=20, layout='circular', directed=False,
                 creation: float = 0, z: float = 0):
        Arrow = _get_arrow()
        objects = []
        edges = edges or []

        # Normalize nodes to dict
        if isinstance(nodes, (list, tuple)):
            nodes = {i: str(v) for i, v in enumerate(nodes)}

        node_ids = list(nodes.keys())
        n = len(node_ids)
        self._node_positions = {}
        self._node_circles = {}
        if n == 0:
            super().__init__(creation=creation, z=z)
            return

        # Layout
        if layout == 'circular':
            self._node_positions = _circular_layout(node_ids, cx, cy, radius)
        elif layout == 'grid':
            cols = max(1, int(math.ceil(math.sqrt(n))))
            spacing = radius * 2 / max(cols - 1, 1) if cols > 1 else 0
            x0 = cx - (cols - 1) * spacing / 2
            y0 = cy - ((n - 1) // cols) * spacing / 2
            for i, nid in enumerate(node_ids):
                r, c = divmod(i, cols)
                self._node_positions[nid] = (x0 + c * spacing, y0 + r * spacing)
        else:  # spring (simple force-directed, few iterations)
            import random
            rng = random.Random(42)
            pos = {nid: (cx + rng.uniform(-radius, radius), cy + rng.uniform(-radius, radius))
                   for nid in node_ids}
            for _ in range(_SPRING_ITERATIONS):
                forces = {nid: [0.0, 0.0] for nid in node_ids}
                # Repulsion
                for i, a in enumerate(node_ids):
                    for b in node_ids[i + 1:]:
                        dx = pos[a][0] - pos[b][0]
                        dy = pos[a][1] - pos[b][1]
                        d = math.hypot(dx, dy) + 1
                        f = _REPULSION_STRENGTH / (d * d)
                        _apply_force(forces, a, b, f * dx / d, f * dy / d)
                # Attraction (edges)
                for edge in edges:
                    a, b = edge[0], edge[1]
                    if a not in pos or b not in pos:
                        continue
                    dx = pos[b][0] - pos[a][0]
                    dy = pos[b][1] - pos[a][1]
                    d = math.hypot(dx, dy) + 1
                    f = d * _ATTRACTION_STRENGTH
                    _apply_force(forces, a, b, f * dx / d, f * dy / d)
                for nid in node_ids:
                    pos[nid] = (pos[nid][0] + forces[nid][0] * _POSITION_DAMPING,
                                pos[nid][1] + forces[nid][1] * _POSITION_DAMPING)
            # Center the layout
            avg_x = sum(p[0] for p in pos.values()) / n if n else cx
            avg_y = sum(p[1] for p in pos.values()) / n if n else cy
            for nid in node_ids:
                self._node_positions[nid] = (pos[nid][0] - avg_x + cx,
                                             pos[nid][1] - avg_y + cy)

        # Draw edges
        for edge in edges:
            a, b = edge[0], edge[1]
            label = edge[2] if len(edge) > 2 else None
            if a not in self._node_positions or b not in self._node_positions:
                continue
            ax, ay = self._node_positions[a]
            bx, by = self._node_positions[b]
            if directed:
                ax2, ay2, bx2, by2 = _shortened_endpoints(ax, ay, bx, by, node_r, node_r)
                arrow = Arrow(x1=ax2, y1=ay2, x2=bx2, y2=by2,
                              **_DIAGRAM_TIP, creation=creation, z=z, stroke='#888', stroke_width=2)
                objects.append(arrow)
            else:
                line = Line(x1=ax, y1=ay, x2=bx, y2=by,
                            creation=creation, z=z, stroke='#888', stroke_width=2)
                objects.append(line)
            if label:
                mx, my = (ax + bx) / 2, (ay + by) / 2
                lbl = Text(text=str(label), x=mx, y=my - 10,
                           font_size=font_size * 0.8, text_anchor='middle',
                           creation=creation, z=z + 2, fill='#aaa', stroke_width=0)
                objects.append(lbl)

        # Draw nodes
        for nid in node_ids:
            nx, ny = self._node_positions[nid]
            circle = _make_node_circle(node_r, nx, ny, creation, z + 1)
            objects.append(circle)
            self._node_circles[nid] = circle
            lbl = _label_text(nodes[nid], nx, ny, font_size, creation=creation, z=z + 2)
            objects.append(lbl)

        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return f'NetworkGraph({len(self._node_positions)} nodes)'

    def highlight_node(self, node_id, start: float = 0, end: float = 1, color='#FFFF00', easing=easings.there_and_back):
        """Flash-highlight a node by its ID."""
        _highlight_in_dict(self._node_circles, node_id, start, end, color, easing)
        return self

    def get_node_position(self, node_id):
        """Get the (x, y) position of a node."""
        return self._node_positions.get(node_id, ORIGIN)

# ---------------------------------------------------------------------------
# Tree
# ---------------------------------------------------------------------------

class Tree(VCollection):
    """Hierarchical tree layout visualization."""
    def __init__(self, data, cx=ORIGIN[0], cy=100, h_spacing=120, v_spacing=100,
                 node_r=20, font_size=18, layout='down',
                 creation: float = 0, z: float = 0):
        objects = []

        # Normalize data to (label, children) format
        if isinstance(data, dict):
            data = self._dict_to_tree(data)

        # Use id(node_tuple) as key to handle duplicate labels
        positions = {}   # id(node) -> (x, y)
        labels = {}      # id(node) -> label string
        widths = {}      # id(node) -> subtree width
        node_map = {}    # label -> id(node) (first occurrence, for API)

        self._collect_nodes(data, labels, node_map)
        self._calc_widths(data, widths, h_spacing)
        self._layout(data, cx, cy, widths, h_spacing, v_spacing, positions, layout)

        # Draw edges
        self._draw_edges_impl(data, positions, objects, creation, z, Line)

        # Draw nodes (skip empty-label nodes)
        self._node_objects = {}
        self._positions_by_label = {}
        for node_tuple, (nx, ny) in [(n, positions[id(n)]) for n in self._all_nodes(data) if id(n) in positions]:
            label = node_tuple[0]
            if not label:
                continue
            circle = _make_node_circle(node_r, nx, ny, creation, z + 1)
            objects.append(circle)
            nid = id(node_tuple)
            self._node_objects[nid] = circle
            if label not in self._positions_by_label:
                self._positions_by_label[label] = (nx, ny)
                self._node_objects[label] = circle  # label-based lookup (first occurrence)
            lbl = _label_text(label, nx, ny, font_size, creation=creation, z=z + 2)
            objects.append(lbl)

        super().__init__(*objects, creation=creation, z=z)

    @staticmethod
    def _all_nodes(node):
        """Yield all nodes in pre-order."""
        yield node
        for child in node[1]:
            yield from Tree._all_nodes(child)

    @staticmethod
    def _collect_nodes(node, labels, node_map):
        label = node[0]
        labels[id(node)] = label
        if label and label not in node_map:
            node_map[label] = id(node)
        for child in node[1]:
            Tree._collect_nodes(child, labels, node_map)

    @staticmethod
    def _dict_to_tree(d):
        """Convert dict tree to tuple tree.

        Supports ``{'A': ['B', 'C']}`` (list children) and
        ``{'A': {'B': ..., 'C': ...}}`` (nested dict) formats.
        """
        if not d:
            return ('', [])
        key = next(iter(d))
        children = d[key]
        if isinstance(children, dict):
            return (key, [Tree._dict_to_tree({k: v}) for k, v in children.items()])
        if isinstance(children, (list, tuple)):
            result = []
            for child in children:
                if isinstance(child, dict):
                    result.append(Tree._dict_to_tree(child))
                else:
                    result.append((str(child), []))
            return (key, result)
        return (key, [])

    @staticmethod
    def _calc_widths(node, widths, spacing):
        if not node[1]:
            widths[id(node)] = spacing
        else:
            total = 0
            for child in node[1]:
                Tree._calc_widths(child, widths, spacing)
                total += widths[id(child)]
            widths[id(node)] = max(total, spacing)

    @staticmethod
    def _layout(node, x, y, widths, h_spacing, v_spacing, positions, layout):
        positions[id(node)] = (x, y)
        children = node[1]
        if not children:
            return
        total_w = sum(widths[id(c)] for c in children)
        cur = x - total_w / 2
        for child in children:
            cw = widths[id(child)]
            child_x = cur + cw / 2
            if layout == 'down':
                Tree._layout(child, child_x, y + v_spacing, widths, h_spacing, v_spacing, positions, layout)
            else:
                Tree._layout(child, x + v_spacing, child_x, widths, h_spacing, v_spacing, positions, layout)
            cur += cw

    @staticmethod
    def _draw_edges_impl(node, positions, objects, creation, z, LineClass):
        px, py = positions[id(node)]
        for child in node[1]:
            if id(child) in positions:
                ccx, ccy = positions[id(child)]
                objects.append(LineClass(x1=px, y1=py, x2=ccx, y2=ccy,
                                        creation=creation, z=z, stroke='#888', stroke_width=2))
            Tree._draw_edges_impl(child, positions, objects, creation, z, LineClass)

    def __repr__(self):
        return f'Tree({len(self._positions_by_label)} nodes)'

    def get_node_position(self, label):
        """Get (x, y) position of a node by label (first occurrence if duplicates)."""
        return self._positions_by_label.get(label, ORIGIN)

    def highlight_node(self, label, start: float = 0, end: float = 1, color='#FFFF00', easing=easings.there_and_back):
        """Flash-highlight a node by label."""
        _highlight_in_dict(self._node_objects, label, start, end, color, easing)
        return self

# ---------------------------------------------------------------------------
# Stamp
# ---------------------------------------------------------------------------

class Stamp(VCollection):
    """Place copies of a template object at specified positions."""
    def __init__(self, template, points, creation: float = 0, z: float = 0):
        from copy import deepcopy
        objects = []
        for px, py in points:
            c = deepcopy(template)
            cx, cy = c.center(creation)
            c.shift(dx=px - cx, dy=py - cy, start=creation)
            objects.append(c)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return f'Stamp({len(self.objects)} copies)'

# ---------------------------------------------------------------------------
# TimelineBar
# ---------------------------------------------------------------------------

class TimelineBar(VCollection):
    """Visual timeline bar with labeled markers."""
    def __init__(self, markers, total_duration=10, x=200, y=900,
                 width=1520, height=6, marker_color='#FFFF00',
                 font_size=14, creation: float = 0, z: float = 0):
        objects = []
        # Track bar
        track = Rectangle(width, height, x=x, y=y - height / 2,
                          fill='#444', fill_opacity=0.8, stroke_width=0,
                          creation=creation, z=z)
        objects.append(track)
        # Markers
        if total_duration <= 0:
            total_duration = 1
        for t_val, label in markers.items():
            frac = t_val / total_duration
            mx = x + frac * width
            tick = Line(x1=mx, y1=y - 15, x2=mx, y2=y + 15,
                        stroke=marker_color, stroke_width=2,
                        creation=creation, z=z + 0.1)
            dot = Circle(r=4, cx=mx, cy=y, fill=marker_color,
                         fill_opacity=1, stroke_width=0,
                         creation=creation, z=z + 0.2)
            txt = Text(text=str(label), x=mx, y=y - 22,
                       font_size=font_size, fill='#ccc', stroke_width=0,
                       text_anchor='middle', creation=creation, z=z + 0.1)
            objects.extend([tick, dot, txt])
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'TimelineBar()'

# ---------------------------------------------------------------------------
# FlowChart
# ---------------------------------------------------------------------------

class FlowChart(VCollection):
    """Simple flow chart with labeled boxes connected by arrows."""
    def __init__(self, steps, direction='right', x=200, y=400,
                 box_width=200, box_height=60, spacing=80,
                 box_color='#58C4DD', text_color='#fff', arrow_color='#999',
                 font_size=20, corner_radius=8, creation: float = 0, z: float = 0):
        Arrow = _get_arrow()
        objects = []
        self._boxes = []
        self._labels = []
        horizontal = direction == 'right'
        for i, label in enumerate(steps):
            if horizontal:
                bx = x + i * (box_width + spacing)
                by = y
            else:
                bx = x
                by = y + i * (box_height + spacing)
            box = RoundedRectangle(box_width, box_height, x=bx, y=by,
                                   corner_radius=corner_radius,
                                   fill=box_color, fill_opacity=0.8,
                                   stroke=box_color, creation=creation, z=z)
            txt = Text(text=label, x=bx + box_width / 2, y=by + box_height / 2 + font_size * TEXT_Y_OFFSET,
                       font_size=font_size, fill=text_color, stroke_width=0,
                       text_anchor='middle', creation=creation, z=z + 0.1)
            self._boxes.append(box)
            self._labels.append(txt)
            objects.extend([box, txt])
            # Arrow between boxes
            if i > 0:
                if horizontal:
                    prev_bx = x + (i - 1) * (box_width + spacing)
                    ax1, ay1 = prev_bx + box_width, y + box_height / 2
                    ax2, ay2 = bx, y + box_height / 2
                else:
                    prev_by = y + (i - 1) * (box_height + spacing)
                    ax1, ay1 = x + box_width / 2, prev_by + box_height
                    ax2, ay2 = x + box_width / 2, by
                arr = Arrow(ax1, ay1, ax2, ay2, stroke=arrow_color,
                            creation=creation, z=z - 0.1)
                objects.append(arr)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return f'FlowChart({len(self._boxes)} steps)'

# ---------------------------------------------------------------------------
# VennDiagram
# ---------------------------------------------------------------------------

class VennDiagram(VCollection):
    """Venn diagram with 2 or 3 overlapping circles."""
    def __init__(self, labels, sizes=None, x=ORIGIN[0], y=ORIGIN[1], radius=150,
                 colors=None, font_size=24, creation: float = 0, z: float = 0):
        n = len(labels)
        if n < 2 or n > 3:
            super().__init__(creation=creation, z=z)
            return
        if colors is None:
            colors = ['#58C4DD', '#FF6B6B', '#83C167']
        if sizes is None:
            sizes = [radius] * n
        objects = []
        # Circle positions
        if n == 2:
            sep = radius * 0.7
            positions = [(x - sep / 2, y), (x + sep / 2, y)]
        else:
            sep = radius * 0.65
            ang120 = math.tau / 3
            positions = [(x + sep * math.cos(math.pi / 2 + i * ang120),
                          y - sep * math.sin(math.pi / 2 + i * ang120))
                         for i in range(3)]
        for i, (cx, cy) in enumerate(positions):
            c = Circle(r=sizes[i], cx=cx, cy=cy,
                       fill=colors[i % len(colors)], fill_opacity=0.25,
                       stroke=colors[i % len(colors)], stroke_width=2,
                       creation=creation, z=z)
            objects.append(c)
        # Labels outside circles
        for i, (cx, cy) in enumerate(positions):
            if n == 2:
                lx = cx + (-1 if i == 0 else 1) * sizes[i] * 0.5
                ly = cy - sizes[i] - 15
            else:
                dx, dy = cx - x, cy - y
                ux, uy = _normalize(dx, dy)
                lx = cx + ux * (sizes[i] + 20)
                ly = cy + uy * (sizes[i] + 20) + font_size * TEXT_Y_OFFSET
            lbl = Text(text=str(labels[i]), x=lx, y=ly,
                       font_size=font_size, fill=colors[i % len(colors)],
                       stroke_width=0, text_anchor='middle',
                       creation=creation, z=z + 0.1)
            objects.append(lbl)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'VennDiagram()'

# ---------------------------------------------------------------------------
# OrgChart
# ---------------------------------------------------------------------------

class OrgChart(VCollection):
    """Organization chart from a tree structure."""
    def __init__(self, root, x=ORIGIN[0], y=80, h_spacing=180, v_spacing=100,
                 box_width=120, box_height=40, font_size=16,
                 colors=None, creation: float = 0, z: float = 0):
        if colors is None:
            colors = list(DEFAULT_CHART_COLORS)
        # Layout: BFS to compute positions
        levels = []
        queue = deque([(root, 0)])
        while queue:
            node, depth = queue.popleft()
            while len(levels) <= depth:
                levels.append([])
            levels[depth].append(node)
            _, children = node
            for child in children:
                queue.append((child, depth + 1))
        # Assign x positions per level
        positions = {}
        for depth, nodes in enumerate(levels):
            total_w = len(nodes) * h_spacing
            start_x = x - total_w / 2 + h_spacing / 2
            for i, node in enumerate(nodes):
                nx = start_x + i * h_spacing
                ny = y + depth * v_spacing
                positions[id(node)] = (nx, ny)
        objects = []
        # Draw connections then boxes (so boxes are on top)
        self._draw_tree(root, positions, objects, colors, 0,
                        box_width, box_height, font_size, creation, z)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'OrgChart()'

    def _draw_tree(self, node, positions, objects, colors, depth,
                   box_width, box_height, font_size, creation, z):
        label, children = node
        nx, ny = positions[id(node)]
        color = colors[depth % len(colors)]
        # Connection lines to children
        for child in children:
            cx, cy = positions[id(child)]
            mid_y = ny + box_height / 2 + (cy - ny - box_height / 2) / 2
            # L-shaped connector: down, across, down
            d = (f'M{nx:.1f},{ny + box_height:.1f} '
                 f'L{nx:.1f},{mid_y:.1f} '
                 f'L{cx:.1f},{mid_y:.1f} '
                 f'L{cx:.1f},{cy:.1f}')
            conn = Path(d, stroke='#666', stroke_width=1.5,
                        fill_opacity=0, creation=creation, z=z)
            objects.append(conn)
        # Box

        rect = RoundedRectangle(width=box_width, height=box_height,
                                 x=nx - box_width / 2, y=ny,
                                 corner_radius=6, fill=color, fill_opacity=0.85,
                                 stroke=color, stroke_width=1,
                                 creation=creation, z=z + 0.1)
        objects.append(rect)
        # Label
        lbl = Text(text=str(label), x=nx, y=ny + box_height / 2 + font_size * TEXT_Y_OFFSET,
                   font_size=font_size, fill='#fff', stroke_width=0,
                   text_anchor='middle', creation=creation, z=z + 0.2)
        objects.append(lbl)
        for child in children:
            self._draw_tree(child, positions, objects, colors, depth + 1,
                            box_width, box_height, font_size, creation, z)

# ---------------------------------------------------------------------------
# MindMap
# ---------------------------------------------------------------------------

class MindMap(VCollection):
    """Radial mind map diagram."""
    def __init__(self, root, cx=ORIGIN[0], cy=ORIGIN[1], radius=250, font_size=18,
                 colors=None, creation: float = 0, z: float = 0):
        if colors is None:
            colors = list(DEFAULT_CHART_COLORS)
        objects = []
        root_label, children = root
        # Central node
        root_dot = Circle(r=35, cx=cx, cy=cy, fill=colors[0], fill_opacity=0.9,
                          stroke=colors[0], stroke_width=2, creation=creation, z=z + 0.2)
        objects.append(root_dot)
        root_txt = _label_text(root_label, cx, cy, font_size,
                               creation=creation, z=z + 0.3)
        objects.append(root_txt)
        if not children:
            super().__init__(*objects, creation=creation, z=z)
            return
        n_ch = len(children)
        branch_pos = _circular_layout(range(n_ch), cx, cy, radius)
        for i, (child_label, grandchildren) in enumerate(children):
            bx, by = branch_pos[i]
            angle = math.tau * i / n_ch - math.pi / 2
            color = colors[(i + 1) % len(colors)]
            # Branch line
            line = Line(x1=cx, y1=cy, x2=bx, y2=by, stroke=color,
                        stroke_width=2, stroke_opacity=0.5,
                        creation=creation, z=z)
            objects.append(line)
            # Branch node
            br = 25
            bdot = Circle(r=br, cx=bx, cy=by, fill=color, fill_opacity=0.85,
                          stroke=color, stroke_width=1.5, creation=creation, z=z + 0.2)
            objects.append(bdot)
            btxt = _label_text(child_label, bx, by, font_size * 0.85,
                               creation=creation, z=z + 0.3)
            objects.append(btxt)
            # Grandchildren as smaller nodes
            if grandchildren:
                gn = len(grandchildren)
                spread = math.pi * 0.6
                for j, (gc_label, _) in enumerate(grandchildren):
                    ga = angle if gn == 1 else angle - spread / 2 + spread * j / (gn - 1)
                    gx = bx + radius * 0.5 * math.cos(ga)
                    gy = by + radius * 0.5 * math.sin(ga)
                    gl = Line(x1=bx, y1=by, x2=gx, y2=gy, stroke=color,
                              stroke_width=1, stroke_opacity=0.4,
                              creation=creation, z=z)
                    objects.append(gl)
                    gdot = Dot(cx=gx, cy=gy, r=15, fill=color, fill_opacity=0.7,
                               stroke_width=0, creation=creation, z=z + 0.2)
                    objects.append(gdot)
                    gtxt = _label_text(gc_label, gx, gy, font_size * 0.65,
                                       creation=creation, z=z + 0.3, fill='#ddd')
                    objects.append(gtxt)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'MindMap()'
