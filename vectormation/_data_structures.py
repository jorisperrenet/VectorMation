"""Data structure visualization classes: Array, Stack, Queue, LinkedList, etc."""
import math
import vectormation.easings as easings
from vectormation._constants import (
    ORIGIN, TEXT_Y_OFFSET, _label_text, _get_arrow,
)
from vectormation._base import VCollection
from vectormation._shapes import Circle, Rectangle, Line, Text


def _flash_fill(obj, color, start, end, default='#264653'):
    """Temporarily change an object's fill colour, reverting at *end*."""
    orig = obj.styling.fill.time_func(0)
    orig_hex = '#{:02x}{:02x}{:02x}'.format(*orig) if orig else default
    obj.set_fill(color=color, start=start)
    obj.set_fill(color=orig_hex, start=end)


class Array(VCollection):
    """Visual array data structure with cells, indices, and animation methods.

    values: list of initial values to display in cells.
    """
    def __init__(self, values, x=360, y=440, cell_width=80, cell_height=60,
                 font_size=24, index_font_size=16,
                 fill='#1e1e2e', text_color='#fff', border_color='#58C4DD',
                 show_indices=True, creation: float = 0, z: float = 0):
        self._cell_width = cell_width
        self._cell_height = cell_height
        self._x, self._y = x, y
        self._cells = []
        self._labels = []
        objects = []
        for i, val in enumerate(values):
            cx = x + i * cell_width
            cell = Rectangle(width=cell_width, height=cell_height, x=cx, y=y,
                             fill=fill, stroke=border_color, stroke_width=2,
                             creation=creation, z=z)
            lbl = _label_text(str(val), cx + cell_width / 2, y + cell_height / 2,
                              font_size, creation=creation, z=z + 0.1, fill=text_color)
            self._cells.append(cell)
            self._labels.append(lbl)
            objects.extend([cell, lbl])
            if show_indices:
                idx = _label_text(str(i), cx + cell_width / 2, y + cell_height + index_font_size + 4,
                                  index_font_size, creation=creation, z=z + 0.1, fill='#888')
                objects.append(idx)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return f'Array({len(self._cells)} cells)'

    def highlight_cell(self, index, start=0, end=1, color='#58C4DD', easing=easings.there_and_back):
        """Flash-highlight a cell by index."""
        if 0 <= index < len(self._cells):
            self._cells[index].flash(start, end, color=color, easing=easing)
        return self

    def swap_cells(self, i, j, start=0, end=1, easing=easings.smooth):
        """Animate swapping the values at indices i and j."""
        if 0 <= i < len(self._labels) and 0 <= j < len(self._labels):
            li, lj = self._labels[i], self._labels[j]
            bxi = li.bbox(start)[0] + li.bbox(start)[2] / 2
            bxj = lj.bbox(start)[0] + lj.bbox(start)[2] / 2
            dx = bxj - bxi
            li.shift(dx=dx, start=start, end=end, easing=easing)
            lj.shift(dx=-dx, start=start, end=end, easing=easing)
            self._labels[i], self._labels[j] = self._labels[j], self._labels[i]
        return self

    def add_pointer(self, index, label='', color='#FF6B6B', creation=0, z=1):
        """Add a pointer arrow above a cell."""
        Arrow = _get_arrow()
        if 0 <= index < len(self._cells):
            cx = self._x + index * self._cell_width + self._cell_width / 2
            arrow = Arrow(x1=cx, y1=self._y - 50, x2=cx, y2=self._y - 8,
                          creation=creation, z=z, stroke=color, fill=color)
            self.objects.append(arrow)
            if label:
                lbl = _label_text(label, cx, self._y - 58, 16,
                                  creation=creation, z=z, fill=color)
                self.objects.append(lbl)
            return arrow
        return None


class Stack(VCollection):
    """Visual stack data structure (LIFO) with push/pop animations.

    values: initial values (bottom to top).
    """
    def __init__(self, values=None, x=860, y=600, cell_width=100, cell_height=50,
                 font_size=22, fill='#1e1e2e', text_color='#fff', border_color='#58C4DD',
                 creation: float = 0, z: float = 0):
        self._cell_width = cell_width
        self._cell_height = cell_height
        self._x, self._y_base = x, y
        self._font_size = font_size
        self._fill = fill
        self._text_color = text_color
        self._border_color = border_color
        self._items = []
        objects = []
        if values:
            for i, val in enumerate(values):
                cy = y - i * cell_height
                cell = Rectangle(width=cell_width, height=cell_height, x=x, y=cy,
                                 fill=fill, stroke=border_color, stroke_width=2,
                                 creation=creation, z=z)
                lbl = _label_text(str(val), x + cell_width / 2, cy + cell_height / 2,
                                  font_size, creation=creation, z=z + 0.1, fill=text_color)
                self._items.append((cell, lbl))
                objects.extend([cell, lbl])
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return f'Stack({len(self._items)} items)'

    def push(self, value, start=0, end=0.5):
        """Animate pushing a value onto the stack."""
        n = len(self._items)
        slot_y = self._y_base - n * self._cell_height
        start_y = slot_y - self._cell_height * 2
        cell = Rectangle(width=self._cell_width, height=self._cell_height,
                         x=self._x, y=start_y,
                         fill=self._fill, stroke=self._border_color, stroke_width=2,
                         creation=start, z=0)
        lbl = _label_text(str(value), self._x + self._cell_width / 2,
                          start_y + self._cell_height / 2,
                          self._font_size, creation=start, z=0.1, fill=self._text_color)
        dy = slot_y - start_y
        cell.shift(dy=dy, start=start, end=end, easing=easings.ease_out_back)
        lbl.shift(dy=dy, start=start, end=end, easing=easings.ease_out_back)
        self._items.append((cell, lbl))
        self.objects.extend([cell, lbl])
        return self

    def pop(self, start=0, end=0.5):
        """Animate popping the top value from the stack."""
        if not self._items:
            return self
        cell, lbl = self._items.pop()
        cell.fadeout(start=start, end=end, change_existence=True)
        lbl.fadeout(start=start, end=end, change_existence=True)
        return self


class Queue(VCollection):
    """Visual queue data structure (FIFO) with enqueue/dequeue animations.

    values: initial values (front to back).
    """
    def __init__(self, values=None, x=360, y=440, cell_width=80, cell_height=60,
                 font_size=22, fill='#1e1e2e', text_color='#fff', border_color='#83C167',
                 creation: float = 0, z: float = 0):
        self._cell_width = cell_width
        self._cell_height = cell_height
        self._x, self._y = x, y
        self._font_size = font_size
        self._fill = fill
        self._text_color = text_color
        self._border_color = border_color
        self._items = []
        objects = []
        if values:
            for i, val in enumerate(values):
                cx = x + i * cell_width
                cell = Rectangle(width=cell_width, height=cell_height, x=cx, y=y,
                                 fill=fill, stroke=border_color, stroke_width=2,
                                 creation=creation, z=z)
                lbl = _label_text(str(val), cx + cell_width / 2, y + cell_height / 2,
                                  font_size, creation=creation, z=z + 0.1, fill=text_color)
                self._items.append((cell, lbl))
                objects.extend([cell, lbl])
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return f'Queue({len(self._items)} items)'

    def enqueue(self, value, start=0, end=0.5):
        """Animate adding a value to the back of the queue."""
        n = len(self._items)
        target_cx = self._x + n * self._cell_width
        start_cx = target_cx + self._cell_width
        cell = Rectangle(width=self._cell_width, height=self._cell_height,
                         x=start_cx, y=self._y,
                         fill=self._fill, stroke=self._border_color, stroke_width=2,
                         creation=start, z=0)
        lbl = _label_text(str(value), start_cx + self._cell_width / 2,
                          self._y + self._cell_height / 2,
                          self._font_size, creation=start, z=0.1, fill=self._text_color)
        cell.shift(dx=-self._cell_width, start=start, end=end,
                   easing=easings.ease_out_back)
        lbl.shift(dx=-self._cell_width, start=start, end=end,
                  easing=easings.ease_out_back)
        self._items.append((cell, lbl))
        self.objects.extend([cell, lbl])
        return self

    def dequeue(self, start=0, end=0.5):
        """Animate removing the front value from the queue."""
        if not self._items:
            return self
        cell, lbl = self._items.pop(0)
        cell.fadeout(start=start, end=end, change_existence=True)
        lbl.fadeout(start=start, end=end, change_existence=True)
        for c, l in self._items:
            c.shift(dx=-self._cell_width, start=start, end=end, easing=easings.smooth)
            l.shift(dx=-self._cell_width, start=start, end=end, easing=easings.smooth)
        return self


class LinkedList(VCollection):
    """Visual linked list with nodes and arrow pointers.

    values: list of node values.
    """
    def __init__(self, values, x=200, y=440, node_width=80, node_height=50,
                 gap=40, font_size=22,
                 fill='#1e1e2e', text_color='#fff', border_color='#58C4DD',
                 arrow_color='#fff', creation: float = 0, z: float = 0):
        Arrow = _get_arrow()
        self._nodes = []
        objects = []
        step = node_width + gap
        for i, val in enumerate(values):
            nx = x + i * step
            node = Rectangle(width=node_width, height=node_height, x=nx, y=y,
                             fill=fill, stroke=border_color, stroke_width=2,
                             creation=creation, z=z)
            lbl = _label_text(str(val), nx + node_width / 2, y + node_height / 2,
                              font_size, creation=creation, z=z + 0.1, fill=text_color)
            self._nodes.append((node, lbl))
            objects.extend([node, lbl])
            if i < len(values) - 1:
                ax1 = nx + node_width
                ax2 = nx + step
                ay = y + node_height / 2
                objects.append(Arrow(x1=ax1, y1=ay, x2=ax2, y2=ay,
                                     creation=creation, z=z, stroke=arrow_color, fill=arrow_color))
        if values:
            nx = x + (len(values) - 1) * step + node_width + 10
            ny = y + node_height / 2
            objects.append(Text(text='null', x=nx, y=ny + font_size * TEXT_Y_OFFSET,
                                font_size=font_size - 4, fill='#888', stroke_width=0,
                                creation=creation, z=z))
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return f'LinkedList({len(self._nodes)} nodes)'

    def highlight_node(self, index, start=0, end=1, color='#FF6B6B',
                       easing=easings.there_and_back):
        """Flash-highlight a node by index."""
        if 0 <= index < len(self._nodes):
            self._nodes[index][0].flash(start, end, color=color, easing=easing)
        return self


class BinaryTree(VCollection):
    """Visual binary tree with automatic layout.

    tree: nested tuple (value, left_subtree, right_subtree).
    Leaves can be just a value or (value, None, None).
    """
    def __init__(self, tree, x=960, y=120, h_spacing=200, v_spacing=100,
                 node_radius=25, font_size=20,
                 fill='#1e1e2e', text_color='#fff', border_color='#58C4DD',
                 edge_color='#888', creation: float = 0, z: float = 0):
        objects = []
        self._node_objects = []

        def _draw(node, cx, cy, spread):
            if node is None:
                return
            if isinstance(node, (int, float, str)):
                val, left, right = node, None, None
            elif isinstance(node, (tuple, list)) and len(node) >= 1:
                val = node[0]
                left = node[1] if len(node) > 1 else None
                right = node[2] if len(node) > 2 else None
            else:
                return
            child_y = cy + v_spacing
            child_spread = spread / 2
            if left is not None:
                lx = cx - child_spread
                objects.append(Line(x1=cx, y1=cy, x2=lx, y2=child_y,
                                    stroke=edge_color, stroke_width=2,
                                    creation=creation, z=z))
                _draw(left, lx, child_y, child_spread)
            if right is not None:
                rx = cx + child_spread
                objects.append(Line(x1=cx, y1=cy, x2=rx, y2=child_y,
                                    stroke=edge_color, stroke_width=2,
                                    creation=creation, z=z))
                _draw(right, rx, child_y, child_spread)
            node_obj = Circle(r=node_radius, cx=cx, cy=cy,
                              fill=fill, stroke=border_color, stroke_width=2,
                              creation=creation, z=z + 0.1)
            lbl = _label_text(str(val), cx, cy, font_size,
                              creation=creation, z=z + 0.2, fill=text_color)
            self._node_objects.append(node_obj)
            objects.extend([node_obj, lbl])

        _draw(tree, x, y, h_spacing)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return f'BinaryTree({len(self._node_objects)} nodes)'

    def highlight_node(self, index, color='#E9C46A', start=0, end=0.5):
        """Temporarily highlight a node by index (depth-first order)."""
        if 0 <= index < len(self._node_objects):
            _flash_fill(self._node_objects[index], color, start, end, '#1e1e2e')
        return self


class ArrayViz(VCollection):
    """Visualise an array as a row of labeled cells.

    Each element is rendered as a Rectangle with centred Text inside.
    Supports animated swaps, highlights, and value changes.

    Parameters
    ----------
    values : list
        Initial values to display in the array.
    cell_size : float
        Width and height of each cell.
    x, y : float
        Position of the top-left corner of the first cell.
    colors : list or None
        Per-cell fill colours.  If *None*, all cells use *default_fill*.
    default_fill : str
        Default cell fill colour.
    show_indices : bool
        If *True*, show 0-based indices below each cell.
    """

    def __init__(self, values, cell_size=80, x=None, y=None,
                 colors=None, default_fill='#264653', show_indices=True,
                 font_size=32, creation: float = 0, z: float = 0):
        n = len(values)
        if x is None:
            x = ORIGIN[0] - n * cell_size / 2
        if y is None:
            y = ORIGIN[1] - cell_size / 2
        self._cells = []
        self._labels = []
        self._index_labels = []
        self._cell_size = cell_size
        self.values = list(values)
        objects = []
        for i, val in enumerate(values):
            cx = x + i * cell_size
            fill = colors[i] if colors and i < len(colors) else default_fill
            cell = Rectangle(cell_size, cell_size, x=cx, y=y,
                             fill=fill, fill_opacity=0.9, stroke='#fff',
                             stroke_width=2, creation=creation, z=z)
            lbl = Text(text=str(val), x=cx + cell_size / 2,
                       y=y + cell_size * 0.65,
                       font_size=font_size, fill='#fff', stroke_width=0,
                       text_anchor='middle', creation=creation, z=z + 0.1)
            self._cells.append(cell)
            self._labels.append(lbl)
            objects.extend([cell, lbl])
            if show_indices:
                idx_lbl = Text(text=str(i), x=cx + cell_size / 2,
                               y=y + cell_size + 20,
                               font_size=font_size * 0.6, fill='#888',
                               stroke_width=0, text_anchor='middle',
                               creation=creation, z=z)
                self._index_labels.append(idx_lbl)
                objects.append(idx_lbl)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return f'ArrayViz({self.values})'

    def highlight(self, index, start=0, end=1, color='#FFFF00'):
        """Temporarily highlight a cell by changing its fill colour."""
        if 0 <= index < len(self._cells):
            _flash_fill(self._cells[index], color, start, end)
        return self

    def swap(self, i, j, start=0, end=1, easing=easings.smooth):
        """Animate swapping the values at indices *i* and *j*.

        Cell rectangles stay in place; labels animate to the other position
        using arc paths.
        """
        if i == j or not (0 <= i < len(self._labels)) or not (0 <= j < len(self._labels)):
            return self
        a, b = self._labels[i], self._labels[j]
        ax, ay = a.x.at_time(start), a.y.at_time(start)
        bx, by = b.x.at_time(start), b.y.at_time(start)
        a.path_arc(bx, by, start=start, end=end, angle=math.pi / 3, easing=easing)
        b.path_arc(ax, ay, start=start, end=end, angle=-math.pi / 3, easing=easing)
        self._labels[i], self._labels[j] = self._labels[j], self._labels[i]
        self.values[i], self.values[j] = self.values[j], self.values[i]
        return self

    def set_value(self, index, new_val, start=0, end=None):
        """Change the displayed value of a cell.

        If *end* is given, the old text fades out and the new text fades in
        over [start, end].  Otherwise the change is instant.
        """
        if 0 <= index < len(self._labels):
            lbl = self._labels[index]
            if end is not None:
                lbl.set_text(start, end, str(new_val))
            else:
                lbl.text.set_onward(start, str(new_val))
            self.values[index] = new_val
        return self

    def pointer(self, index, label='', start=0, end=None, color='#FC6255'):
        """Add an arrow pointer above a cell.

        Returns the Arrow object (also added to self).
        """
        Arrow = _get_arrow()
        if not (0 <= index < len(self._cells)):
            return self
        cell = self._cells[index]
        cx = cell.x.at_time(start) + self._cell_size / 2
        cy = cell.y.at_time(start)
        arr = Arrow(x1=cx, y1=cy - 50, x2=cx, y2=cy - 8,
                    stroke=color, fill=color, fill_opacity=1,
                    stroke_width=2, creation=start)
        arr.fadein(start, start + 0.3 if end is None else end)
        self.objects.append(arr)
        if label:
            lbl = Text(text=label, x=cx, y=cy - 60,
                       font_size=20, fill=color, stroke_width=0,
                       text_anchor='middle', creation=start)
            lbl.fadein(start, start + 0.3 if end is None else end)
            self.objects.append(lbl)
        return arr


class LinkedListViz(VCollection):
    """Visualise a singly linked list as nodes connected by arrows.

    Parameters
    ----------
    values : list
        Initial node values.
    node_radius : float
        Radius of each node circle.
    spacing : float
        Horizontal distance between node centres.
    x, y : float
        Position of the first node's centre.
    """

    def __init__(self, values, node_radius=35, spacing=140,
                 x=None, y=540, node_fill='#264653',
                 font_size=28, creation: float = 0, z: float = 0):
        Arrow = _get_arrow()
        n = len(values)
        if x is None:
            x = ORIGIN[0] - (n - 1) * spacing / 2
        self._nodes = []
        self._labels = []
        self._arrows = []
        self._node_radius = node_radius
        self._spacing = spacing
        self.values = list(values)
        objects = []
        for i, val in enumerate(values):
            cx = x + i * spacing
            node = Circle(r=node_radius, cx=cx, cy=y,
                          fill=node_fill, fill_opacity=0.9,
                          stroke='#fff', stroke_width=2,
                          creation=creation, z=z)
            lbl = Text(text=str(val), x=cx, y=y + font_size * 0.35,
                       font_size=font_size, fill='#fff', stroke_width=0,
                       text_anchor='middle', creation=creation, z=z + 0.1)
            self._nodes.append(node)
            self._labels.append(lbl)
            objects.extend([node, lbl])
            if i > 0:
                prev_cx = x + (i - 1) * spacing
                arr = Arrow(x1=prev_cx + node_radius + 4, y1=y,
                            x2=cx - node_radius - 4, y2=y,
                            stroke='#fff', fill='#fff', fill_opacity=1,
                            stroke_width=2, creation=creation, z=z)
                self._arrows.append(arr)
                objects.append(arr)
        # Null terminator
        last_cx = x + (n - 1) * spacing
        null_lbl = Text(text='\u2205', x=last_cx + spacing * 0.6,
                        y=y + font_size * 0.35,
                        font_size=font_size, fill='#888', stroke_width=0,
                        text_anchor='middle', creation=creation, z=z)
        null_arr = Arrow(x1=last_cx + node_radius + 4, y1=y,
                         x2=last_cx + spacing * 0.6 - 15, y2=y,
                         stroke='#888', fill='#888', fill_opacity=1,
                         stroke_width=2, creation=creation, z=z)
        objects.extend([null_arr, null_lbl])
        self._null_lbl = null_lbl
        self._null_arr = null_arr
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return f'LinkedListViz({self.values})'

    def highlight(self, index, start=0, end=1, color='#FFFF00'):
        """Temporarily highlight a node."""
        if 0 <= index < len(self._nodes):
            _flash_fill(self._nodes[index], color, start, end)
        return self

    def traverse(self, start=0, delay=0.5, color='#FFFF00'):
        """Animate traversing each node in sequence.

        Each node lights up for *delay* seconds in order.
        """
        for i in range(len(self._nodes)):
            t = start + i * delay
            self.highlight(i, t, t + delay, color)
        return self


class StackViz(VCollection):
    """Visualise a stack (LIFO) as vertically stacked cells.

    Parameters
    ----------
    values : list
        Initial values (bottom to top).
    cell_width, cell_height : float
        Dimensions of each cell.
    x, y : float
        Position of the bottom-left corner of the bottom cell.
    """

    def __init__(self, values, cell_width=120, cell_height=50,
                 x=None, y=None, fill='#264653',
                 font_size=28, creation: float = 0, z: float = 0):
        Arrow = _get_arrow()
        n = len(values)
        if x is None:
            x = ORIGIN[0] - cell_width / 2
        if y is None:
            y = ORIGIN[1] + n * cell_height / 2
        self._cell_width = cell_width
        self._cell_height = cell_height
        self._base_x = x
        self._base_y = y
        self._fill = fill
        self._font_size = font_size
        self._stack_cells = []
        self._stack_labels = []
        self._z = z
        self.values = list(values)
        objects = []
        for i, val in enumerate(values):
            cy = y - i * cell_height
            cell = Rectangle(cell_width, cell_height, x=x, y=cy,
                              fill=fill, fill_opacity=0.9, stroke='#fff',
                              stroke_width=2, creation=creation, z=z)
            lbl = Text(text=str(val), x=x + cell_width / 2,
                       y=cy + cell_height * 0.65,
                       font_size=font_size, fill='#fff', stroke_width=0,
                       text_anchor='middle', creation=creation, z=z + 0.1)
            self._stack_cells.append(cell)
            self._stack_labels.append(lbl)
            objects.extend([cell, lbl])
        # "TOP" label
        top_y = y - (n - 1) * cell_height if n > 0 else y
        self._top_arrow = Arrow(x1=x - 50, y1=top_y + cell_height / 2,
                                x2=x - 8, y2=top_y + cell_height / 2,
                                stroke='#FC6255', fill='#FC6255', fill_opacity=1,
                                stroke_width=2, creation=creation, z=z)
        top_lbl = Text(text='TOP', x=x - 58, y=top_y + cell_height * 0.65,
                       font_size=int(font_size * 0.7), fill='#FC6255', stroke_width=0,
                       text_anchor='end', creation=creation, z=z)
        self._top_label = top_lbl
        objects.extend([self._top_arrow, top_lbl])
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return f'StackViz({self.values})'

    def push(self, value, start=0, end=0.5):
        """Animate pushing a value onto the stack."""
        n = len(self._stack_cells)
        cy = self._base_y - n * self._cell_height
        cell = Rectangle(self._cell_width, self._cell_height,
                         x=self._base_x, y=cy,
                         fill=self._fill, fill_opacity=0.9, stroke='#fff',
                         stroke_width=2, creation=start, z=self._z)
        lbl = Text(text=str(value), x=self._base_x + self._cell_width / 2,
                   y=cy + self._cell_height * 0.65,
                   font_size=self._font_size, fill='#fff', stroke_width=0,
                   text_anchor='middle', creation=start, z=self._z + 0.1)
        cell.fadein(start, end)
        lbl.fadein(start, end)
        self._stack_cells.append(cell)
        self._stack_labels.append(lbl)
        self.values.append(value)
        self.objects.extend([cell, lbl])
        # Move TOP arrow up
        self._top_arrow.shift(dy=-self._cell_height, start=start, end=end)
        self._top_label.shift(dy=-self._cell_height, start=start, end=end)
        return self

    def pop(self, start=0, end=0.5):
        """Animate popping the top value from the stack."""
        if not self._stack_cells:
            return self
        cell = self._stack_cells.pop()
        lbl = self._stack_labels.pop()
        self.values.pop()
        cell.fadeout(start, end)
        lbl.fadeout(start, end)
        # Move TOP arrow down
        if self._stack_cells:
            self._top_arrow.shift(dy=self._cell_height, start=start, end=end)
            self._top_label.shift(dy=self._cell_height, start=start, end=end)
        return self


class QueueViz(VCollection):
    """Visualise a queue (FIFO) as a horizontal row of cells.

    Parameters
    ----------
    values : list
        Initial values (front on the left, back on the right).
    cell_width, cell_height : float
        Dimensions of each cell.
    x, y : float
        Position of the top-left corner of the front cell.
    """

    def __init__(self, values, cell_width=80, cell_height=60,
                 x=None, y=None, fill='#264653',
                 font_size=28, creation: float = 0, z: float = 0):
        n = len(values)
        if x is None:
            x = ORIGIN[0] - n * cell_width / 2
        if y is None:
            y = ORIGIN[1] - cell_height / 2
        self._cell_width = cell_width
        self._cell_height = cell_height
        self._base_x = x
        self._base_y = y
        self._fill = fill
        self._font_size = font_size
        self._z = z
        self._queue_cells = []
        self._queue_labels = []
        self.values = list(values)
        objects = []
        for i, val in enumerate(values):
            cx = x + i * cell_width
            cell = Rectangle(cell_width, cell_height, x=cx, y=y,
                              fill=fill, fill_opacity=0.9, stroke='#fff',
                              stroke_width=2, creation=creation, z=z)
            lbl = _label_text(str(val), cx + cell_width / 2, y + cell_height / 2,
                              font_size, creation=creation, z=z + 0.1)
            self._queue_cells.append(cell)
            self._queue_labels.append(lbl)
            objects.extend([cell, lbl])
        # FRONT / BACK labels
        front_x = x - 8
        back_x = x + n * cell_width + 8
        mid_y = y + cell_height * 0.65
        self._front_label = Text(text='FRONT', x=front_x, y=mid_y,
                                  font_size=int(font_size * 0.7), fill='#50FA7B',
                                  stroke_width=0, text_anchor='end',
                                  creation=creation, z=z)
        self._back_label = Text(text='BACK', x=back_x, y=mid_y,
                                 font_size=int(font_size * 0.7), fill='#FC6255',
                                 stroke_width=0, text_anchor='start',
                                 creation=creation, z=z)
        objects.extend([self._front_label, self._back_label])
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return f'QueueViz({self.values})'

    def enqueue(self, value, start=0, end=0.5):
        """Animate adding a value to the back of the queue."""
        n = len(self._queue_cells)
        cx = self._base_x + n * self._cell_width
        cell = Rectangle(self._cell_width, self._cell_height,
                         x=cx, y=self._base_y,
                         fill=self._fill, fill_opacity=0.9, stroke='#fff',
                         stroke_width=2, creation=start, z=self._z)
        lbl = _label_text(str(value), cx + self._cell_width / 2,
                          self._base_y + self._cell_height / 2,
                          self._font_size, creation=start, z=self._z + 0.1)
        cell.fadein(start, end)
        lbl.fadein(start, end)
        self._queue_cells.append(cell)
        self._queue_labels.append(lbl)
        self.values.append(value)
        self.objects.extend([cell, lbl])
        self._back_label.shift(dx=self._cell_width, start=start, end=end)
        return self

    def dequeue(self, start=0, end=0.5):
        """Animate removing the front value from the queue."""
        if not self._queue_cells:
            return self
        cell = self._queue_cells.pop(0)
        lbl = self._queue_labels.pop(0)
        self.values.pop(0)
        cell.fadeout(start, end)
        lbl.fadeout(start, end)
        # Slide remaining cells left
        for c, l in zip(self._queue_cells, self._queue_labels):
            c.shift(dx=-self._cell_width, start=start, end=end)
            l.shift(dx=-self._cell_width, start=start, end=end)
        self._back_label.shift(dx=-self._cell_width, start=start, end=end)
        return self

    def highlight(self, index, color='#E9C46A', start=0, end=0.5):
        """Temporarily highlight a cell at *index*."""
        if 0 <= index < len(self._queue_cells):
            _flash_fill(self._queue_cells[index], color, start, end, self._fill)
        return self
