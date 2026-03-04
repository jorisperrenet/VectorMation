"""Data structure visualization classes: Array, Stack, Queue, LinkedList, etc."""
import math
import vectormation.easings as easings
from vectormation._constants import (
    ORIGIN, TEXT_Y_OFFSET, _label_text, _get_arrow,
)
from vectormation._base import VCollection
from vectormation._shapes import Circle, Rectangle, Line, Text
from vectormation.colors import _rgb_to_hex

_VIZ_TEXT_Y = 0.65  # Y-offset factor for vertically centering text in viz cells
_VIZ_SMALL_FONT = 0.7  # Small label font relative to main font_size

def _make_cell(x, y, w, h, val, font_size, fill, border_color, text_color,
               creation: float = 0, z: float = 0):
    """Create a rectangle cell + centered label text pair."""
    cell = Rectangle(width=w, height=h, x=x, y=y,
                     fill=fill, stroke=border_color, stroke_width=2,
                     creation=creation, z=z)
    lbl = _label_text(str(val), x + w / 2, y + h / 2,
                      font_size, creation=creation, z=z + 0.1, fill=text_color)
    return cell, lbl

def _flash_fill(obj, color, start, end, default='#264653'):
    """Temporarily change an object's fill color, reverting at *end*."""
    orig = obj.styling.fill.time_func(0)
    orig_hex = _rgb_to_hex(*orig) if orig else default
    obj.set_fill(color=color, start=start)
    obj.set_fill(color=orig_hex, start=end)

def _shift_pair(cell, lbl, **kwargs):
    """Shift a cell+label pair with identical parameters."""
    cell.shift(**kwargs)
    lbl.shift(**kwargs)

def _fadeout_pair(cell, lbl, start, end, change_existence=False):
    """Fade out a cell+label pair."""
    cell.fadeout(start=start, end=end, change_existence=change_existence)
    lbl.fadeout(start=start, end=end, change_existence=change_existence)

def _make_viz_cell(x, y, w, h, val, font_size, fill, creation: float = 0, z: float = 0):
    """Create a Rectangle + Text pair for Viz-style classes (white stroke, centered text)."""
    cell, lbl = _make_cell(x, y, w, h, val, font_size, fill, '#fff', '#fff', creation, z)
    cell.styling.fill_opacity.set_onward(0, 0.9)
    lbl.y.set_onward(0, y + h * _VIZ_TEXT_Y)
    return cell, lbl

class Array(VCollection):
    """Visual array data structure with cells, indices, and animation methods."""
    def __init__(self, values, x: float = 360, y: float = 440, cell_width: float = 80, cell_height: float = 60,
                 font_size: float = 24, index_font_size=16,
                 fill='#1e1e2e', text_color='#fff', border_color='#58C4DD',
                 show_indices=True, creation: float = 0, z: float = 0):
        self._cell_width, self._cell_height = cell_width, cell_height
        self._x, self._y = x, y
        self._cells, self._labels, objects = [], [], []
        for i, val in enumerate(values):
            cx = x + i * cell_width
            cell, lbl = _make_cell(cx, y, cell_width, cell_height, val, font_size,
                                   fill, border_color, text_color, creation, z)
            self._cells.append(cell)
            self._labels.append(lbl)
            objects.extend([cell, lbl])
            if show_indices:
                objects.append(_label_text(str(i), cx + cell_width / 2,
                               y + cell_height + index_font_size + 4,
                               index_font_size, creation=creation, z=z + 0.1, fill='#888'))
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self): return f'Array({len(self._cells)} cells)'

    def _check_index(self, index):
        n = len(self._cells)
        if index < 0 or index >= n:
            raise IndexError(f"Array index {index} out of range (0..{n - 1})")

    def highlight_cell(self, index, start: float = 0, end: float = 1, color='#58C4DD', easing=easings.there_and_back):
        """Flash-highlight a cell by index."""
        self._check_index(index)
        self._cells[index].flash(start, end, color=color, easing=easing)
        return self

    def swap_cells(self, i, j, start: float = 0, end: float = 1, easing=easings.smooth):
        """Animate swapping the values at indices i and j."""
        self._check_index(i); self._check_index(j)
        li, lj = self._labels[i], self._labels[j]
        dx = lj.center(start)[0] - li.center(start)[0]
        li.shift(dx=dx, start=start, end=end, easing=easing)
        lj.shift(dx=-dx, start=start, end=end, easing=easing)
        self._labels[i], self._labels[j] = self._labels[j], self._labels[i]
        return self

    def set_value(self, index, value, start: float = 0, end: float = 0.5):
        """Animate changing a cell's displayed value."""
        self._check_index(index)
        self._labels[index].set_text(str(value), start, end)
        return self

    def sort(self, start: float = 0, end: float = 2, easing=easings.smooth, delay: float = 0.15):
        """Animate a bubble sort, staggering swaps over [start, end]."""
        n = len(self._labels)
        swaps, values = [], [self._labels[i].text.at_time(start) for i in range(n)]
        for _ in range(n):
            for j in range(n - 1):
                if str(values[j]) > str(values[j + 1]):
                    values[j], values[j + 1] = values[j + 1], values[j]
                    swaps.append((j, j + 1))
        t = start
        for i_idx, j_idx in swaps:
            self.swap_cells(i_idx, j_idx, start=t, end=min(t + delay, end), easing=easing)
            t += delay
        return self

    def reverse(self, start: float = 0, end: float = 2, easing=easings.smooth, delay: float = 0.15):
        """Animate reversing the array by swapping from outside in."""
        n, t = len(self._labels), start
        for i in range(n // 2):
            self.swap_cells(i, n - 1 - i, start=t, end=min(t + delay, end), easing=easing)
            t += delay
        return self

    def add_pointer(self, index, label='', color='#FF6B6B', creation: float = 0, z: float = 1):
        """Add a pointer arrow above a cell. Returns the Arrow, or self if index is invalid."""
        Arrow = _get_arrow()
        if not (0 <= index < len(self._cells)):
            return self
        cx = self._x + index * self._cell_width + self._cell_width / 2
        arrow = Arrow(x1=cx, y1=self._y - 50, x2=cx, y2=self._y - 8,
                      tip_length=14, tip_width=12,
                      creation=creation, z=z, stroke=color, fill=color)
        self.objects.append(arrow)
        if label:
            self.objects.append(_label_text(label, cx, self._y - 58, 16,
                                            creation=creation, z=z, fill=color))
        return arrow

class Stack(VCollection):
    """Visual stack data structure (LIFO) with push/pop animations."""
    def __init__(self, values=None, x: float = ORIGIN[0] - 100, y: float = ORIGIN[1] + 60, cell_width: float = 100, cell_height: float = 50,
                 font_size: float = 22, fill='#1e1e2e', text_color='#fff', border_color='#58C4DD',
                 creation: float = 0, z: float = 0):
        self._cell_width, self._cell_height = cell_width, cell_height
        self._x, self._y_base = x, y
        self._font_size, self._fill = font_size, fill
        self._text_color, self._border_color = text_color, border_color
        self._items, objects = [], []
        if values:
            for i, val in enumerate(values):
                cell, lbl = _make_cell(x, y - i * cell_height, cell_width, cell_height,
                                       val, font_size, fill, border_color, text_color,
                                       creation, z)
                self._items.append((cell, lbl))
                objects.extend([cell, lbl])
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self): return f'Stack({len(self._items)} items)'
    def peek(self): return self._items[-1][1].text.at_time(0) if self._items else None
    def is_empty(self): return not self._items

    def push(self, value, start: float = 0, end: float = 0.5):
        """Animate pushing a value onto the stack."""
        n = len(self._items)
        slot_y = self._y_base - n * self._cell_height
        start_y = slot_y - self._cell_height * 2
        cell, lbl = _make_cell(self._x, start_y, self._cell_width, self._cell_height,
                               value, self._font_size, self._fill, self._border_color,
                               self._text_color, start, 0)
        _shift_pair(cell, lbl, dy=slot_y - start_y, start=start, end=end,
                    easing=easings.ease_out_back)
        self._items.append((cell, lbl))
        self.objects.extend([cell, lbl])
        return self

    def pop(self, start: float = 0, end: float = 0.5):
        """Animate popping the top value from the stack."""
        if not self._items:
            return self
        cell, lbl = self._items.pop()
        _fadeout_pair(cell, lbl, start, end, change_existence=True)
        return self

class Queue(VCollection):
    """Visual queue data structure (FIFO) with enqueue/dequeue animations."""
    def __init__(self, values=None, x: float = 360, y: float = 440, cell_width: float = 80, cell_height: float = 60,
                 font_size: float = 22, fill='#1e1e2e', text_color='#fff', border_color='#83C167',
                 creation: float = 0, z: float = 0):
        self._cell_width, self._cell_height = cell_width, cell_height
        self._x, self._y = x, y
        self._font_size, self._fill = font_size, fill
        self._text_color, self._border_color = text_color, border_color
        self._items, objects = [], []
        if values:
            for i, val in enumerate(values):
                cell, lbl = _make_cell(x + i * cell_width, y, cell_width, cell_height,
                                       val, font_size, fill, border_color, text_color,
                                       creation, z)
                self._items.append((cell, lbl))
                objects.extend([cell, lbl])
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self): return f'Queue({len(self._items)} items)'
    def peek(self): return self._items[0][1].text.at_time(0) if self._items else None
    def is_empty(self): return not self._items

    def enqueue(self, value, start: float = 0, end: float = 0.5):
        """Animate adding a value to the back of the queue."""
        n = len(self._items)
        start_cx = self._x + (n + 1) * self._cell_width
        cell, lbl = _make_cell(start_cx, self._y, self._cell_width, self._cell_height,
                               value, self._font_size, self._fill, self._border_color,
                               self._text_color, start, 0)
        _shift_pair(cell, lbl, dx=-self._cell_width, start=start, end=end,
                    easing=easings.ease_out_back)
        self._items.append((cell, lbl))
        self.objects.extend([cell, lbl])
        return self

    def dequeue(self, start: float = 0, end: float = 0.5):
        """Animate removing the front value from the queue."""
        if not self._items:
            return self
        cell, lbl = self._items.pop(0)
        _fadeout_pair(cell, lbl, start, end, change_existence=True)
        for c, l in self._items:
            _shift_pair(c, l, dx=-self._cell_width, start=start, end=end,
                        easing=easings.smooth)
        return self

class LinkedList(VCollection):
    """Visual linked list with nodes and arrow pointers."""
    def __init__(self, values, x: float = 200, y: float = 440, node_width: float = 80, node_height: float = 50,
                 gap: float = 40, font_size: float = 22,
                 fill='#1e1e2e', text_color='#fff', border_color='#58C4DD',
                 arrow_color='#fff', creation: float = 0, z: float = 0):
        Arrow = _get_arrow()
        self._nodes, self._arrows, objects = [], [], []
        self._x, self._y = x, y
        self._node_width, self._node_height = node_width, node_height
        self._gap, self._font_size = gap, font_size
        self._fill, self._text_color = fill, text_color
        self._border_color, self._arrow_color = border_color, arrow_color
        step = node_width + gap
        for i, val in enumerate(values):
            nx = x + i * step
            node, lbl = _make_cell(nx, y, node_width, node_height, val, font_size,
                                   fill, border_color, text_color, creation, z)
            self._nodes.append((node, lbl))
            objects.extend([node, lbl])
            if i < len(values) - 1:
                ay = y + node_height / 2
                arrow = Arrow(x1=nx + node_width, y1=ay, x2=nx + step, y2=ay,
                              tip_length=14, tip_width=12,
                              creation=creation, z=z, stroke=arrow_color, fill=arrow_color)
                self._arrows.append(arrow)
                objects.append(arrow)
        self._null_text = None
        if values:
            nx = x + (len(values) - 1) * step + node_width + 10
            self._null_text = Text(text='null', x=nx, y=y + node_height / 2 + font_size * TEXT_Y_OFFSET,
                                   font_size=font_size - 4, fill='#888', stroke_width=0,
                                   creation=creation, z=z)
            objects.append(self._null_text)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self): return f'LinkedList({len(self._nodes)} nodes)'

    def highlight_node(self, index, start: float = 0, end: float = 1, color='#FF6B6B',
                       easing=easings.there_and_back):
        """Flash-highlight a node by index."""
        if index < 0 or index >= len(self._nodes):
            return self
        self._nodes[index][0].flash(start, end, color=color, easing=easing)
        return self

    def append_node(self, value, start: float = 0, end: float = 0.5):
        """Animate appending a new node at the end of the list."""
        Arrow = _get_arrow()
        n = len(self._nodes)
        step = self._node_width + self._gap
        nx, ay = self._x + n * step, self._y + self._node_height / 2
        node, lbl = _make_cell(nx, self._y, self._node_width, self._node_height,
                               value, self._font_size, self._fill, self._border_color,
                               self._text_color, start, 0)
        if n > 0:
            ax1 = self._x + (n - 1) * step + self._node_width
            arrow = Arrow(x1=ax1, y1=ay, x2=nx, y2=ay,
                          tip_length=14, tip_width=12,
                          creation=start, z=0, stroke=self._arrow_color,
                          fill=self._arrow_color)
            self._arrows.append(arrow)
            self.objects.append(arrow)
        self._nodes.append((node, lbl))
        node.fadein(start=start, end=end)
        lbl.fadein(start=start, end=end)
        self.objects.extend([node, lbl])
        if self._null_text is not None:
            self._null_text.shift(dx=step, start=start, end=end)
        return self

    def remove_node(self, index, start: float = 0, end: float = 0.5):
        """Animate removing a node by index (fades out, shifts remaining nodes left)."""
        if index < 0 or index >= len(self._nodes):
            return self
        n = len(self._nodes)
        step = self._node_width + self._gap
        node, lbl = self._nodes.pop(index)
        _fadeout_pair(node, lbl, start, end, change_existence=True)
        # Remove the appropriate arrow
        if n > 1:
            if index == n - 1:
                # Last node: remove the arrow pointing to it
                self._arrows.pop(index - 1).fadeout(start, end, change_existence=True)
            else:
                # First or middle node: remove the arrow going from it
                self._arrows.pop(index).fadeout(start, end, change_existence=True)
        # Shift subsequent nodes left
        for i in range(index, len(self._nodes)):
            ni, li = self._nodes[i]
            _shift_pair(ni, li, dx=-step, start=start, end=end, easing=easings.smooth)
        # Shift subsequent arrows left
        for i in range(index, len(self._arrows)):
            self._arrows[i].shift(dx=-step, start=start, end=end, easing=easings.smooth)
        # Shift null text left
        if self._null_text is not None:
            self._null_text.shift(dx=-step, start=start, end=end, easing=easings.smooth)
        return self

class BinaryTree(VCollection):
    """Visual binary tree with automatic layout."""
    def __init__(self, tree, x=ORIGIN[0], y: float = 120, h_spacing: float = 200, v_spacing: float = 100,
                 node_radius: float = 25, font_size: float = 20,
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
            # Add node before children (pre-order) so traverse() visits root first
            self._node_objects.append(
                Circle(r=node_radius, cx=cx, cy=cy, fill=fill, stroke=border_color,
                       stroke_width=2, creation=creation, z=z + 0.1))
            objects.append(self._node_objects[-1])
            objects.append(_label_text(str(val), cx, cy, font_size,
                                       creation=creation, z=z + 0.2, fill=text_color))
            child_y, child_spread = cy + v_spacing, spread / 2
            for child, sign in ((left, -1), (right, 1)):
                if child is not None:
                    child_x = cx + sign * child_spread
                    objects.append(Line(x1=cx, y1=cy, x2=child_x, y2=child_y,
                                        stroke=edge_color, stroke_width=2,
                                        creation=creation, z=z))
                    _draw(child, child_x, child_y, child_spread)

        _draw(tree, x, y, h_spacing)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self): return f'BinaryTree({len(self._node_objects)} nodes)'

    def highlight_node(self, index, start: float = 0, end: float = 1, color='#E9C46A'):
        """Temporarily highlight a node by index (depth-first order)."""
        if 0 <= index < len(self._node_objects):
            _flash_fill(self._node_objects[index], color, start, end, '#1e1e2e')
        return self

    def traverse(self, start: float = 0, delay: float = 0.3, color='#E9C46A'):
        """Animate highlighting each node sequentially (depth-first order)."""
        for i, obj in enumerate(self._node_objects):
            t = start + i * delay
            _flash_fill(obj, color, t, t + delay, '#1e1e2e')
        return self

class ArrayViz(VCollection):
    """Visualise an array as a row of labeled cells."""

    def __init__(self, values, cell_size: float = 80, x=None, y=None,
                 colors=None, default_fill='#264653', show_indices=True,
                 font_size: float = 32, creation: float = 0, z: float = 0):
        n = len(values)
        if x is None: x = ORIGIN[0] - n * cell_size / 2
        if y is None: y = ORIGIN[1] - cell_size / 2
        self._cells, self._labels, self._index_labels = [], [], []
        self._cell_size = cell_size
        self.values = list(values)
        objects = []
        for i, val in enumerate(values):
            cx = x + i * cell_size
            fill = colors[i] if colors and i < len(colors) else default_fill
            cell, lbl = _make_viz_cell(cx, y, cell_size, cell_size, val, font_size, fill, creation, z)
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

    def __repr__(self): return f'ArrayViz({self.values})'

    def highlight(self, index, start: float = 0, end: float = 1, color='#FFFF00'):
        """Temporarily highlight a cell by changing its fill color."""
        if 0 <= index < len(self._cells):
            _flash_fill(self._cells[index], color, start, end)
        return self

    def swap(self, i, j, start: float = 0, end: float = 1, easing=easings.smooth):
        """Animate swapping the values at indices *i* and *j*."""
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

    def set_value(self, index, new_val, start: float = 0, end: float | None = None):
        """Change the displayed value of a cell."""
        if 0 <= index < len(self._labels):
            lbl = self._labels[index]
            if end is not None:
                lbl.set_text(str(new_val), start, end)
            else:
                lbl.text.set_onward(start, str(new_val))
            self.values[index] = new_val
        return self

    def pointer(self, index, label='', start: float = 0, end: float | None = None, color='#FC6255'):
        """Add an arrow pointer above a cell."""
        Arrow = _get_arrow()
        if not (0 <= index < len(self._cells)):
            return self
        cell = self._cells[index]
        cx = cell.x.at_time(start) + self._cell_size / 2
        cy = cell.y.at_time(start)
        fade_end = start + 0.3 if end is None else end
        arr = Arrow(x1=cx, y1=cy - 50, x2=cx, y2=cy - 8,
                    stroke=color, fill=color, fill_opacity=1,
                    stroke_width=2, creation=start)
        arr.fadein(start, fade_end)
        self.objects.append(arr)
        if label:
            lbl = Text(text=label, x=cx, y=cy - 60,
                       font_size=20, fill=color, stroke_width=0,
                       text_anchor='middle', creation=start)
            lbl.fadein(start, fade_end)
            self.objects.append(lbl)
        return arr

class LinkedListViz(VCollection):
    """Visualise a singly linked list as nodes connected by arrows."""

    def __init__(self, values, node_radius: float = 35, spacing: float = 140,
                 x=None, y=ORIGIN[1], node_fill='#264653',
                 font_size: float = 28, creation: float = 0, z: float = 0):
        Arrow = _get_arrow()
        n = len(values)
        if x is None: x = ORIGIN[0] - (n - 1) * spacing / 2
        self._nodes, self._labels, self._arrows = [], [], []
        self._node_radius, self._spacing = node_radius, spacing
        self.values = list(values)
        objects = []
        for i, val in enumerate(values):
            cx = x + i * spacing
            node = Circle(r=node_radius, cx=cx, cy=y,
                          fill=node_fill, fill_opacity=0.9,
                          stroke='#fff', stroke_width=2,
                          creation=creation, z=z)
            lbl = _label_text(val, cx, y, font_size,
                              creation=creation, z=z + 0.1)
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
        null_lbl = _label_text('\u2205', last_cx + spacing * 0.6, y, font_size,
                               creation=creation, z=z, fill='#888')
        null_arr = Arrow(x1=last_cx + node_radius + 4, y1=y,
                         x2=last_cx + spacing * 0.6 - 15, y2=y,
                         stroke='#888', fill='#888', fill_opacity=1,
                         stroke_width=2, creation=creation, z=z)
        objects.extend([null_arr, null_lbl])
        self._null_lbl, self._null_arr = null_lbl, null_arr
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self): return f'LinkedListViz({self.values})'

    def highlight(self, index, start: float = 0, end: float = 1, color='#FFFF00'):
        """Temporarily highlight a node."""
        if 0 <= index < len(self._nodes):
            _flash_fill(self._nodes[index], color, start, end)
        return self

    def traverse(self, start: float = 0, delay: float = 0.5, color='#FFFF00'):
        """Animate traversing each node in sequence."""
        for i in range(len(self._nodes)):
            t = start + i * delay
            self.highlight(i, t, t + delay, color)
        return self

class StackViz(VCollection):
    """Visualise a stack (LIFO) as vertically stacked cells."""

    def __init__(self, values, cell_width: float = 120, cell_height: float = 50,
                 x=None, y=None, fill='#264653',
                 font_size: float = 28, creation: float = 0, z: float = 0):
        Arrow = _get_arrow()
        n = len(values)
        if x is None: x = ORIGIN[0] - cell_width / 2
        if y is None: y = ORIGIN[1] + n * cell_height / 2
        self._cell_width, self._cell_height = cell_width, cell_height
        self._base_x, self._base_y = x, y
        self._fill, self._font_size, self._z = fill, font_size, z
        self._stack_cells, self._stack_labels = [], []
        self.values = list(values)
        objects = []
        for i, val in enumerate(values):
            cell, lbl = _make_viz_cell(x, y - i * cell_height, cell_width, cell_height,
                                       val, font_size, fill, creation, z)
            self._stack_cells.append(cell)
            self._stack_labels.append(lbl)
            objects.extend([cell, lbl])
        # "TOP" label
        top_y = y - (n - 1) * cell_height if n > 0 else y
        self._top_arrow = Arrow(x1=x - 50, y1=top_y + cell_height / 2,
                                x2=x - 8, y2=top_y + cell_height / 2,
                                stroke='#FC6255', fill='#FC6255', fill_opacity=1,
                                stroke_width=2, creation=creation, z=z)
        self._top_label = Text(text='TOP', x=x - 58, y=top_y + cell_height * _VIZ_TEXT_Y,
                               font_size=int(font_size * _VIZ_SMALL_FONT), fill='#FC6255', stroke_width=0,
                               text_anchor='end', creation=creation, z=z)
        objects.extend([self._top_arrow, self._top_label])
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self): return f'StackViz({self.values})'

    def push(self, value, start: float = 0, end: float = 0.5):
        """Animate pushing a value onto the stack."""
        cy = self._base_y - len(self._stack_cells) * self._cell_height
        cell, lbl = _make_viz_cell(self._base_x, cy, self._cell_width, self._cell_height,
                                   value, self._font_size, self._fill, start, self._z)
        cell.fadein(start, end)
        lbl.fadein(start, end)
        self._stack_cells.append(cell)
        self._stack_labels.append(lbl)
        self.values.append(value)
        self.objects.extend([cell, lbl])
        _shift_pair(self._top_arrow, self._top_label,
                    dy=-self._cell_height, start=start, end=end)
        return self

    def pop(self, start: float = 0, end: float = 0.5):
        """Animate popping the top value from the stack."""
        if not self._stack_cells:
            return self
        self._stack_cells.pop().fadeout(start, end)
        self._stack_labels.pop().fadeout(start, end)
        self.values.pop()
        if self._stack_cells:
            _shift_pair(self._top_arrow, self._top_label,
                        dy=self._cell_height, start=start, end=end)
        return self

class QueueViz(VCollection):
    """Visualise a queue (FIFO) as a horizontal row of cells."""

    def __init__(self, values, cell_width: float = 80, cell_height: float = 60,
                 x=None, y=None, fill='#264653',
                 font_size: float = 28, creation: float = 0, z: float = 0):
        n = len(values)
        if x is None: x = ORIGIN[0] - n * cell_width / 2
        if y is None: y = ORIGIN[1] - cell_height / 2
        self._cell_width, self._cell_height = cell_width, cell_height
        self._base_x, self._base_y = x, y
        self._fill, self._font_size, self._z = fill, font_size, z
        self._queue_cells, self._queue_labels = [], []
        self.values = list(values)
        objects = []
        for i, val in enumerate(values):
            cx = x + i * cell_width
            cell, lbl = _make_viz_cell(cx, y, cell_width, cell_height, val, font_size,
                                       fill, creation, z)
            self._queue_cells.append(cell)
            self._queue_labels.append(lbl)
            objects.extend([cell, lbl])
        # FRONT / BACK labels
        mid_y = y + cell_height * _VIZ_TEXT_Y
        sm_font = int(font_size * _VIZ_SMALL_FONT)
        self._front_label = Text(text='FRONT', x=x - 8, y=mid_y,
                                  font_size=sm_font, fill='#50FA7B',
                                  stroke_width=0, text_anchor='end',
                                  creation=creation, z=z)
        self._back_label = Text(text='BACK', x=x + n * cell_width + 8, y=mid_y,
                                 font_size=sm_font, fill='#FC6255',
                                 stroke_width=0, text_anchor='start',
                                 creation=creation, z=z)
        objects.extend([self._front_label, self._back_label])
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self): return f'QueueViz({self.values})'

    def enqueue(self, value, start: float = 0, end: float = 0.5):
        """Animate adding a value to the back of the queue."""
        cx = self._base_x + len(self._queue_cells) * self._cell_width
        cell, lbl = _make_viz_cell(cx, self._base_y, self._cell_width, self._cell_height,
                                   value, self._font_size, self._fill, start, self._z)
        cell.fadein(start, end)
        lbl.fadein(start, end)
        self._queue_cells.append(cell)
        self._queue_labels.append(lbl)
        self.values.append(value)
        self.objects.extend([cell, lbl])
        self._back_label.shift(dx=self._cell_width, start=start, end=end)
        return self

    def dequeue(self, start: float = 0, end: float = 0.5):
        """Animate removing the front value from the queue."""
        if not self._queue_cells:
            return self
        self._queue_cells.pop(0).fadeout(start, end)
        self._queue_labels.pop(0).fadeout(start, end)
        self.values.pop(0)
        for c, l in zip(self._queue_cells, self._queue_labels):
            _shift_pair(c, l, dx=-self._cell_width, start=start, end=end)
        self._back_label.shift(dx=-self._cell_width, start=start, end=end)
        return self

    def highlight(self, index, start: float = 0, end: float = 0.5, color='#E9C46A'):
        """Temporarily highlight a cell at *index*."""
        if 0 <= index < len(self._queue_cells):
            _flash_fill(self._queue_cells[index], color, start, end, self._fill)
        return self
