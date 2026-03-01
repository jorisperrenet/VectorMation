"""Chart and visualization classes."""
import math
from collections import deque

import vectormation.easings as easings
import vectormation.attributes as attributes
import vectormation.style as style
from vectormation._constants import (
    DEFAULT_CHART_COLORS, ORIGIN,
    CHAR_WIDTH_FACTOR, TEXT_Y_OFFSET, _label_text,
)
from vectormation._base import VObject, VCollection, _lerp
from vectormation._base_helpers import _clamp01, _norm_dir
from vectormation._shapes import (
    Polygon, Circle, Dot, Rectangle, RoundedRectangle, Line, Lines,
    Text, Path, Arc, Wedge,
)


def _default_colors(colors):
    """Return *colors* or a copy of DEFAULT_CHART_COLORS if None."""
    return list(DEFAULT_CHART_COLORS) if colors is None else colors


def _check_idx(index, collection, name, *, allow_negative=False):
    """Validate index bounds; return item or raise IndexError."""
    n = len(collection)
    if allow_negative:
        if index < -n or index >= n:
            raise IndexError(f"{name} index {index} out of range for {n} items")
    else:
        if index < 0 or index >= n:
            raise IndexError(f"{name} index {index} out of range (0..{n - 1})")
    return collection[index]


def _angular_pos(cx, cy, angle_deg, radius):
    """Return (x, y) at *angle_deg* (math convention, CCW from East) on a circle."""
    rad = math.radians(angle_deg)
    return cx + radius * math.cos(rad), cy - radius * math.sin(rad)


def _from_dict(cls, data, **kwargs):
    """Create a chart from a dict {label: value}."""
    return cls(list(data.values()), labels=list(data.keys()), **kwargs)


def _highlight_sector_impl(self, index, start, end, pull_distance, easing):
    """Shared highlight_sector logic for PieChart and DonutChart."""
    sector = _check_idx(index, self._sectors, 'sector')
    if end - start <= 0:
        return self
    dx, dy = self._sector_offset(index, pull_distance)
    sector.shift(dx=dx, dy=dy, start=start, end=end, easing=easing)
    return self

class PieChart(VCollection):
    """Pie chart visualization using Wedge sectors."""
    def __init__(self, values, labels=None, colors=None, cx=ORIGIN[0], cy=ORIGIN[1], r: float = 240,
                 start_angle: float = 90, creation: float = 0, z: float = 0):
        colors = _default_colors(colors)
        total = sum(values)
        if total == 0:
            total = len(values) or 1
            values = [1] * len(values) if values else values
        objects: list[VObject] = []
        angle = start_angle
        for i, val in enumerate(values):
            sweep = 360 * val / total
            color = colors[i % len(colors)]
            sector = Wedge(cx=cx, cy=cy, r=r, start_angle=angle, end_angle=angle + sweep,
                           creation=creation, z=z, fill=color, fill_opacity=0.85, stroke='#222', stroke_width=2)
            objects.append(sector)
            if labels and i < len(labels):
                lx, ly = _angular_pos(cx, cy, angle + sweep / 2, r * 0.65)
                lbl = Text(text=str(labels[i]), x=lx, y=ly, font_size=17,
                           text_anchor='middle', creation=creation, z=z, fill='#fff', stroke_width=0)
                objects.append(lbl)
            angle += sweep
        self._sectors = [o for o in objects if isinstance(o, Wedge)]
        super().__init__(*objects, creation=creation, z=z)
        self.values = values
        self._cx, self._cy = cx, cy
        self._start_angle = start_angle

    from_dict = classmethod(_from_dict)

    def __repr__(self):
        return f'PieChart({len(self.values)} sectors)'

    def get_sector(self, index):
        return _check_idx(index, self._sectors, 'sector')

    def _sector_offset(self, index, distance, time: float = 0):
        """Compute (dx, dy) to push sector *index* outward by *distance*."""
        sector = self._sectors[index]
        sa = sector.start_angle.at_time(time)
        ea = sector.end_angle.at_time(time)
        mid_rad = math.radians((sa + ea) / 2)
        return distance * math.cos(mid_rad), -distance * math.sin(mid_rad)

    def highlight_sector(self, index, start: float = 0, end: float = 1, pull_distance: float = 30, easing=easings.there_and_back):
        """Pull out a sector from the pie to highlight it."""
        return _highlight_sector_impl(self, index, start, end, pull_distance, easing)

    def explode(self, indices, distance: float = 20, start: float = 0, end: float | None = None, easing=None):
        """Permanently shift specified sectors outward from the pie center."""
        for idx in indices:
            if idx < 0 or idx >= len(self._sectors):
                continue
            dx, dy = self._sector_offset(idx, distance, start)
            self._sectors[idx].shift(dx=dx, dy=dy, start=start, end=end, easing=easing or easings.smooth)
        return self

    def animate_values(self, new_values, start: float = 0, end: float = 1, easing=easings.smooth):
        """Animate pie chart to new values by morphing sector angles."""
        if len(new_values) != len(self.values):
            raise ValueError(
                f"animate_values expects {len(self.values)} values, got {len(new_values)}"
            )
        old_values = list(self.values)
        old_total = sum(old_values) or 1
        new_total = sum(new_values) or 1
        dur = end - start
        if dur <= 0:
            return self
        # Update stored values
        self.values = list(new_values)
        # Animate each sector's start/end angles
        sa0 = self._start_angle
        cum_old, cum_new = 0, 0
        for i, sector in enumerate(self._sectors):
            old_start_angle = 360 * cum_old / old_total + sa0
            old_end_angle = 360 * (cum_old + old_values[i]) / old_total + sa0
            new_start_angle = 360 * cum_new / new_total + sa0
            new_end_angle = 360 * (cum_new + new_values[i]) / new_total + sa0
            _d = max(dur, 1e-9)
            sector.start_angle.set(start, end,
                _lerp(start, _d, old_start_angle, new_start_angle, easing), stay=True)
            sector.end_angle.set(start, end,
                _lerp(start, _d, old_end_angle, new_end_angle, easing), stay=True)
            cum_old += old_values[i]
            cum_new += new_values[i]
        return self

    def sweep_in(self, start: float = 0, end: float = 1, easing=easings.smooth):
        """Animate all sectors sweeping from zero to their full angles."""
        dur = end - start
        if dur <= 0:
            return self
        _d = max(dur, 1e-9)
        sa0 = self._sectors[0].start_angle.at_time(start) if self._sectors else 90
        for sector in self._sectors:
            ea = sector.end_angle.at_time(start)
            sector.start_angle.set(start, end,
                _lerp(start, _d, sa0, sector.start_angle.at_time(start), easing), stay=True)
            sector.end_angle.set(start, end,
                _lerp(start, _d, sa0, ea, easing), stay=True)
        return self

    def add_percentage_labels(self, fmt='{:.0f}%', font_size: float = 16, color='#fff', creation: float = 0):
        """Add percentage labels at the center of each sector."""
        total = sum(self.values) or 1
        angle = self._start_angle
        for sector, val in zip(self._sectors, self.values):
            sweep = 360 * val / total
            r = sector.r.at_time(creation) * 0.65
            cx = sector.cx.at_time(creation)
            cy = sector.cy.at_time(creation)
            lx, ly = _angular_pos(cx, cy, angle + sweep / 2, r)
            label = Text(text=fmt.format(val / total * 100), font_size=font_size,
                         x=lx, y=ly, creation=creation, fill=color,
                         text_anchor='middle', stroke_width=0)
            self.objects.append(label)
            angle += sweep
        return self

    def add_legend(self, labels, x=None, y=None, font_size: float = 16, creation: float = 0):
        """Add a legend using the sector colors. Position defaults to upper-right."""
        if x is None:
            x = self._cx + 280
        if y is None:
            y = self._cy - 150
        items = []
        for i, label in enumerate(labels[:len(self._sectors)]):
            sector = self._sectors[i]
            color = sector.styling.fill.time_func(0)
            if isinstance(color, tuple):
                from vectormation.colors import _rgb_to_hex
                color = _rgb_to_hex(*color[:3])
            items.append((color, str(label)))
        legend = Legend(items, x=x, y=y, font_size=font_size, creation=creation)
        self.objects.extend(legend.objects)
        return self


def _donut_sector_path(cx, cy, a1_rad, a2_rad, r, ir):
    """Generate SVG path for a donut sector from angles in radians."""
    ox1, oy1 = cx + r * math.cos(a1_rad), cy - r * math.sin(a1_rad)
    ox2, oy2 = cx + r * math.cos(a2_rad), cy - r * math.sin(a2_rad)
    ix1, iy1 = cx + ir * math.cos(a2_rad), cy - ir * math.sin(a2_rad)
    ix2, iy2 = cx + ir * math.cos(a1_rad), cy - ir * math.sin(a1_rad)
    large = 1 if math.degrees(a2_rad - a1_rad) > 180 else 0
    return (f'M{ox1:.1f},{oy1:.1f} A{r},{r} 0 {large} 0 {ox2:.1f},{oy2:.1f} '
            f'L{ix1:.1f},{iy1:.1f} A{ir},{ir} 0 {large} 1 {ix2:.1f},{iy2:.1f} Z')


class DonutChart(VCollection):
    """Donut (ring) chart — PieChart with a hollow center."""
    def __init__(self, values, labels=None, colors=None, cx=ORIGIN[0], cy=ORIGIN[1],
                 r: float = 240, inner_radius: float = 120, start_angle: float = 90,
                 center_text=None, font_size: float = 17, creation: float = 0, z: float = 0):
        colors = _default_colors(colors)
        total = sum(values)
        if total == 0:
            total = len(values) or 1
            values = [1] * len(values) if values else values
        objects: list[VObject] = []
        angle = start_angle
        sectors = []
        for i, val in enumerate(values):
            sweep = 360 * val / total
            color = colors[i % len(colors)]
            d = _donut_sector_path(cx, cy, math.radians(angle),
                                    math.radians(angle + sweep), r, inner_radius)
            sector = Path(d, x=0, y=0, fill=color, fill_opacity=0.85,
                          stroke='#222', stroke_width=2, creation=creation, z=z)
            sectors.append(sector)
            objects.append(sector)
            if labels and i < len(labels):
                lx, ly = _angular_pos(cx, cy, angle + sweep / 2, (r + inner_radius) / 2)
                lbl = Text(text=str(labels[i]), x=lx, y=ly,
                           font_size=font_size, text_anchor='middle',
                           creation=creation, z=z + 0.1, fill='#fff', stroke_width=0)
                objects.append(lbl)
            angle += sweep
        self._sectors = sectors
        self._cx, self._cy = cx, cy
        self._r, self._inner_radius = r, inner_radius
        self._start_angle = start_angle
        if center_text is not None:
            ct = Text(text=str(center_text), x=cx, y=cy + font_size * TEXT_Y_OFFSET,
                      font_size=int(font_size * 1.5), text_anchor='middle',
                      fill='#fff', stroke_width=0, creation=creation, z=z + 0.1)
            objects.append(ct)
        super().__init__(*objects, creation=creation, z=z)
        self.values = values

    from_dict = classmethod(_from_dict)

    def __repr__(self):
        return f'DonutChart({len(self.values)} sectors)'

    def get_sector(self, index):
        """Return the Path object for the sector at index."""
        return _check_idx(index, self._sectors, 'sector')

    def _sector_offset(self, index, distance):
        """Compute (dx, dy) to push sector *index* outward by *distance*."""
        total = sum(self.values) or 1
        mid_deg = self._start_angle + 360 * sum(self.values[:index]) / total + 180 * self.values[index] / total
        mid_rad = math.radians(mid_deg)
        return distance * math.cos(mid_rad), -distance * math.sin(mid_rad)

    def highlight_sector(self, index, start: float = 0, end: float = 1, pull_distance: float = 30, easing=easings.there_and_back):
        """Pull out a donut sector to highlight it by shifting it outward."""
        return _highlight_sector_impl(self, index, start, end, pull_distance, easing)

    def animate_values(self, new_values, start: float = 0, end: float = 1, easing=easings.smooth):
        """Animate donut chart to new values by morphing sector path shapes."""
        if len(new_values) != len(self.values):
            raise ValueError(
                f"animate_values expects {len(self.values)} values, got {len(new_values)}"
            )
        old_values = list(self.values)
        old_total = sum(old_values) or 1
        new_total = sum(new_values) or 1
        dur = end - start
        if dur <= 0:
            return self
        self.values = list(new_values)
        cx, cy = self._cx, self._cy
        r, ir = self._r, self._inner_radius
        sa0 = self._start_angle
        _d = max(dur, 1e-9)
        old_cum, new_cum = 0, 0
        for i, sector in enumerate(self._sectors):
            old_a1 = sa0 + 360 * old_cum / old_total
            old_a2 = sa0 + 360 * (old_cum + old_values[i]) / old_total
            new_a1 = sa0 + 360 * new_cum / new_total
            new_a2 = sa0 + 360 * (new_cum + new_values[i]) / new_total

            def _make_d(t, _s=start, _d=_d, _oa1=old_a1, _oa2=old_a2,
                        _na1=new_a1, _na2=new_a2):
                prog = easing(_clamp01((t - _s) / _d))
                a1 = math.radians(_oa1 + (_na1 - _oa1) * prog)
                a2 = math.radians(_oa2 + (_na2 - _oa2) * prog)
                return _donut_sector_path(cx, cy, a1, a2, r, ir)

            sector.d.set(start, end, _make_d, stay=True)
            old_cum += old_values[i]
            new_cum += new_values[i]
        return self

class BarChart(VCollection):
    """Simple bar chart visualization."""
    def __init__(self, values, labels=None, colors=None, x: float = 120, y: float = 60,
                 width: float = 1440, height: float = 840, bar_spacing: float = 0.2,
                 creation: float = 0, z: float = 0):
        colors = _default_colors(colors)
        n = len(values)
        # Store instance vars early so _bar_geometry can use them
        self._height, self._y = height, y
        self._x, self._width = x, width
        self._bar_spacing = bar_spacing
        self._colors = colors
        self._creation = creation
        self._z = z
        if n == 0:
            super().__init__(creation=creation, z=z)
            self.values, self.bar_count, self._bars, self._labels = [], 0, [], []
            return
        max_val = (max(abs(v) for v in values) if values else 1) or 1
        objects: list[VObject] = []
        bars: list = []
        label_objs: list = []

        for i, val in enumerate(values):
            _, inner_width, bar_h, bx, by = self._bar_geometry(val, i, n, max_val)
            color = colors[i % len(colors)]
            bar = Rectangle(inner_width, bar_h, x=bx, y=by,
                            creation=creation, z=z,
                            fill=color, fill_opacity=0.8, stroke_width=0)
            objects.append(bar)
            bars.append(bar)

            if labels and i < len(labels):
                lbl = Text(text=str(labels[i]),
                           x=bx + inner_width / 2, y=y + height + 24,
                           font_size=14, text_anchor='middle',
                           creation=creation, z=z, fill='#aaa', stroke_width=0)
                objects.append(lbl)
                label_objs.append(lbl)
            else:
                label_objs.append(None)

        # Baseline
        baseline = Line(x1=x, y1=y + height, x2=x + width, y2=y + height,
                        creation=creation, z=z, stroke='#fff', stroke_width=3)
        objects.append(baseline)
        super().__init__(*objects, creation=creation, z=z)
        self.values = values
        self.bar_count = n
        self._bars = bars
        self._labels = label_objs

    def _bar_geometry(self, value, index, n_bars, max_val):
        """Compute (bar_width, inner_width, bar_h, bx, by) for a bar."""
        bw = self._width / n_bars
        iw = bw * (1 - self._bar_spacing)
        bh = abs(value) / max_val * self._height * 0.85
        bx = self._x + index * bw + (bw - iw) / 2
        by = (self._y + self._height - bh) if value >= 0 else (self._y + self._height)
        return bw, iw, bh, bx, by

    from_dict = classmethod(_from_dict)

    def __repr__(self):
        return f'BarChart({self.bar_count} bars)'

    def animate_values(self, new_values, start: float = 0, end: float = 1, easing=easings.smooth):
        """Animate bars to new values over [start, end]."""
        if len(new_values) != len(self._bars):
            raise ValueError(
                f"animate_values expects {len(self._bars)} values, got {len(new_values)}"
            )
        max_val = (max(abs(v) for v in new_values) if new_values else 1) or 1
        dur = max(end - start, 1e-9)
        for bar, new_val in zip(self._bars, new_values):
            old_h = bar.height.at_time(start)
            new_h = abs(new_val) / max_val * self._height * 0.85
            old_y = bar.y.at_time(start)
            new_y = self._y + self._height - new_h if new_val >= 0 else self._y + self._height
            bar.height.set(start, end, _lerp(start, dur, old_h, new_h, easing), stay=True)
            bar.y.set(start, end, _lerp(start, dur, old_y, new_y, easing), stay=True)
        self.values = new_values
        return self

    def set_bar_color(self, index, color, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Change the color of a specific bar."""
        bar = _check_idx(index, self._bars, 'bar', allow_negative=True)
        if end is None:
            bar.styling.fill = attributes.Color(start, color)
        else:
            bar.styling.fill.interpolate(attributes.Color(start, color), start, end, easing=easing)
        return self

    def set_bar_colors(self, colors, start: float = 0):
        """Change all bar colors at once."""
        for i, color in enumerate(colors):
            if i < len(self._bars):
                self._bars[i].styling.fill = attributes.Color(start, color)
        return self

    def get_bar(self, index):
        """Return the bar VObject at the given index."""
        return self._bars[index]

    def get_bars(self, start_idx=None, end_idx=None):
        """Return a VCollection of bars, optionally sliced by index range."""
        bars = self._bars[start_idx:end_idx]
        return VCollection(*bars)

    def highlight_bar(self, index, color='#FFFF00', start: float = 0, end: float | None = None, opacity=None):
        """Highlight a specific bar by changing its fill color."""
        self.set_bar_color(index, color, start, end)
        if opacity is not None:
            bar = _check_idx(index, self._bars, 'bar', allow_negative=True)
            if end is None:
                bar.styling.fill_opacity.set_onward(start, opacity)
            else:
                bar.styling.fill_opacity.move_to(start, end, opacity)
        return self

    def get_bar_by_label(self, label):
        """Return the bar (Rectangle) matching the given label text, or None."""
        for i, lbl in enumerate(self._labels):
            if lbl is not None and lbl.text.at_time(0) == label:
                return self._bars[i]
        return None

    def add_value_labels(self, fmt='{:.0f}', offset: float = 10, font_size: float = 20, creation: float = 0):
        """Add text labels showing each bar's value above (or below) the bar."""
        for bar, val in zip(self._bars, self.values):
            _, by, _, bh = bar.bbox(creation)
            lx = bar.center(creation)[0]
            ly = by - offset if val >= 0 else by + bh + offset + font_size
            label_text = fmt.format(val)
            label = Text(text=label_text, font_size=font_size, x=lx, y=ly,
                         creation=creation, fill='#fff', text_anchor='middle',
                         stroke_width=0)
            self.objects.append(label)
        return self

    def grow_from_zero(self, start: float = 0, end: float = 1, easing=easings.smooth, stagger=True, delay: float = 0.1):
        """Animate bars growing up from zero height at the baseline."""
        n = len(self._bars)
        for i, bar in enumerate(self._bars):
            if stagger and n > 1:
                bar_start = start + i * delay
                bar_end = bar_start + (end - start - (n - 1) * delay)
                bar_end = max(bar_end, bar_start + 0.01)
            else:
                bar_start, bar_end = start, end
            bar.grow_from_edge('bottom', bar_start, bar_end, easing=easing)
        return self

    def get_max_bar(self) -> 'Rectangle | None':
        """Return the bar Rectangle with the maximum value, or None if no bars."""
        return self._bar_by_extreme(max)

    def get_min_bar(self) -> 'Rectangle | None':
        """Return the bar Rectangle with the minimum value, or None if no bars."""
        return self._bar_by_extreme(min)

    get_tallest_bar = get_max_bar
    get_shortest_bar = get_min_bar

    def _bar_by_extreme(self, func) -> 'Rectangle | None':
        if not self._bars:
            return None
        idx = func(range(len(self.values)), key=lambda i: self.values[i])
        return self._bars[idx]

    def add_bar(self, value, label=None, start: float = 0, end: float | None = None):
        """Add a new bar to the right side of the chart."""
        n = len(self._bars)
        all_vals = list(self.values) + [value]
        max_val = max(abs(v) for v in all_vals) or 1
        new_n = n + 1
        _, inner_width, bar_h, bx, by = self._bar_geometry(value, n, new_n, max_val)
        color = self._colors[n % len(self._colors)]
        bar = Rectangle(inner_width, bar_h, x=bx, y=by,
                        creation=start, z=self._z,
                        fill=color, fill_opacity=0.8, stroke_width=0)
        if end is not None:
            # Animate: start at zero height at baseline, grow to full
            bar.height.set_onward(start, 0)
            bar.y.set_onward(start, self._y + self._height)
            dur = end - start
            if dur > 0:
                bar.height.set(start, end,
                    _lerp(start, dur, 0, bar_h, easings.smooth), stay=True)
                bar.y.set(start, end,
                    _lerp(start, dur, self._y + self._height, by, easings.smooth),
                    stay=True)
        self.objects.append(bar)
        self._bars.append(bar)
        self.values = all_vals
        self.bar_count = new_n
        # Label
        if label is not None:
            lbl = Text(text=str(label),
                       x=bx + inner_width / 2,
                       y=self._y + self._height + 24,
                       font_size=14, text_anchor='middle',
                       creation=start, z=self._z,
                       fill='#aaa', stroke_width=0)
            self.objects.append(lbl)
            self._labels.append(lbl)
        else:
            self._labels.append(None)
        return self

    def remove_bar(self, index, start: float = 0, end: float | None = None):
        """Remove a bar by index."""
        _check_idx(index, self._bars, 'bar', allow_negative=True)
        if index < 0:
            index += len(self._bars)
        bar = self._bars[index]
        lbl = self._labels[index]
        if end is not None:
            dur = end - start
            if dur > 0:
                # Animate shrinking to zero height at baseline
                _oh = bar.height.at_time(start)
                _oy = bar.y.at_time(start)
                _by = self._y + self._height
                bar.height.set(start, end,
                    _lerp(start, dur, _oh, 0, easings.smooth), stay=True)
                bar.y.set(start, end,
                    _lerp(start, dur, _oy, _by, easings.smooth), stay=True)
            # Hide bar and label after animation
            bar._hide_from(end)
            if lbl is not None:
                lbl._hide_from(end)
        else:
            bar._hide_from(start)
            if lbl is not None:
                lbl._hide_from(start)
        # Remove from tracking lists
        self._bars.pop(index)
        self._labels.pop(index)
        self.values = list(self.values)
        self.values.pop(index)
        self.bar_count = len(self._bars)
        # Shift remaining bars left to fill gap
        if index < len(self._bars):
            new_n = len(self._bars)
            if new_n > 0:
                bar_width = self._width / new_n
                inner_width = bar_width * (1 - self._bar_spacing)
                shift_time = end if end is not None else start
                for i in range(index, len(self._bars)):
                    target_x = self._x + i * bar_width + (bar_width - inner_width) / 2
                    self._bars[i].x.set_onward(shift_time, target_x)
                    if self._labels[i] is not None:
                        self._labels[i].x.set_onward(shift_time, target_x + inner_width / 2)
        return self

    def animate_sort(self, key=None, reverse=False, start: float = 0, end: float = 1, easing=None):
        """Smoothly animate bars sliding into sorted order."""
        if easing is None:
            easing = easings.smooth
        if len(self._bars) <= 1:
            return self
        if key is None:
            key = lambda v: v
        indexed = [(key(val), i) for i, val in enumerate(self.values)]
        indexed.sort(key=lambda x: x[0], reverse=reverse)
        # Record current x positions at start time
        old_xs = [bar.x.at_time(start) for bar in self._bars]
        dur = end - start
        if dur <= 0:
            return self
        for new_pos, (_, old_idx) in enumerate(indexed):
            if new_pos == old_idx:
                continue
            bar = self._bars[old_idx]
            target_x = old_xs[new_pos]
            current_x = old_xs[old_idx]
            # Animate bar x position smoothly
            bar.x.set(start, end,
                _lerp(start, dur, current_x, target_x, easing), stay=True)
            # Also animate label if present
            lbl = self._labels[old_idx]
            if lbl is not None:
                lbl_x = lbl.x.at_time(start)
                lbl.x.set(start, end,
                    _lerp(start, dur, lbl_x, lbl_x + target_x - current_x, easing),
                    stay=True)
        # Reorder internal lists to match new order
        new_order = [orig_idx for _, orig_idx in indexed]
        self._bars = [self._bars[i] for i in new_order]
        self._labels = [self._labels[i] for i in new_order]
        self.values = [self.values[i] for i in new_order]
        return self

    sort_bars = animate_sort

class PolarAxes(VCollection):
    """Polar coordinate system with radial gridlines and angle markers."""
    def __init__(self, cx=ORIGIN[0], cy=ORIGIN[1], max_radius: float = 400, r_range=(0, 5),
                 n_rings=5, n_sectors=12, creation: float = 0, z: float = 0):
        objects = []
        self._cx, self._cy = cx, cy
        self._max_radius = max_radius
        self._r_max = r_range[1]
        self._r_min = r_range[0]
        r_span = r_range[1] - r_range[0]
        px_per_unit = max_radius / r_span if r_span > 0 else 1

        # Concentric rings
        for i in range(1, max(n_rings, 1) + 1):
            r_val = r_range[0] + i * r_span / max(n_rings, 1)
            r_px = (r_val - r_range[0]) * px_per_unit
            ring = Circle(r=r_px, cx=cx, cy=cy, creation=creation, z=z,
                          stroke='#444', stroke_width=1, fill_opacity=0)
            objects.append(ring)
            label = Text(text=f'{r_val:g}', x=cx + r_px + 5, y=cy - 5,
                         font_size=14, creation=creation, z=z, fill='#666', stroke_width=0)
            objects.append(label)

        # Angular sector lines
        n_sectors = max(n_sectors, 1)
        for i in range(n_sectors):
            angle = math.tau * i / n_sectors
            ex = cx + max_radius * math.cos(angle)
            ey = cy - max_radius * math.sin(angle)
            line = Line(x1=cx, y1=cy, x2=ex, y2=ey,
                        creation=creation, z=z, stroke='#444', stroke_width=1)
            objects.append(line)
            # Angle label
            deg = round(360 * i / n_sectors)
            lx = cx + (max_radius + 20) * math.cos(angle)
            ly = cy - (max_radius + 20) * math.sin(angle)
            lbl = Text(text=f'{deg}\u00b0', x=lx, y=ly + 5,
                       font_size=14, text_anchor='middle',
                       creation=creation, z=z, fill='#888', stroke_width=0)
            objects.append(lbl)

        super().__init__(*objects, creation=creation, z=z)
        self._px_per_unit = px_per_unit

    def __repr__(self):
        return 'PolarAxes()'

    def polar_to_point(self, r, theta_deg):
        """Convert (r, theta) to SVG pixel coordinates."""
        theta = math.radians(theta_deg)
        px = (r - self._r_min) * self._px_per_unit
        return (self._cx + px * math.cos(theta),
                self._cy - px * math.sin(theta))

    def plot_polar(self, func, theta_range=(0, 360), num_points: int = 200,
                   creation: float = 0, z: float = 0, **styling_kwargs):
        """Plot r = func(theta_deg) on this polar axes."""
        style_kw = {'stroke': '#58C4DD', 'stroke_width': 3, 'fill_opacity': 0} | styling_kwargs
        t0, t1 = theta_range
        num_points = max(1, num_points)
        pts = []
        for i in range(num_points + 1):
            theta = t0 + i * (t1 - t0) / num_points
            r = func(theta)
            pts.append(self.polar_to_point(r, theta))
        curve = Lines(*pts, creation=creation, z=z, **style_kw)
        self.objects.append(curve)
        return curve

class Legend(VCollection):
    """Chart legend with colored swatches and labels."""
    def __init__(self, items, x: float = 100, y: float = 100, swatch_size: float = 16, spacing: float = 8,
                 font_size: float = 16, direction='down', creation: float = 0, z: float = 0):
        direction = _norm_dir(direction, 'down')
        objects = []
        horizontal = direction == 'right'
        cursor_x, cursor_y = x, y
        for color, label in items:
            swatch = Rectangle(swatch_size, swatch_size, x=cursor_x, y=cursor_y,
                               fill=color, fill_opacity=0.9, stroke_width=0,
                               creation=creation, z=z)
            txt = Text(text=label, x=cursor_x + swatch_size + spacing,
                       y=cursor_y + swatch_size * 0.75,
                       font_size=font_size, fill='#ccc', stroke_width=0,
                       creation=creation, z=z)
            objects.extend([swatch, txt])
            if horizontal:
                # estimate text width
                cursor_x += swatch_size + spacing + len(label) * font_size * CHAR_WIDTH_FACTOR + spacing * 2
            else:
                cursor_y += swatch_size + spacing
        self._n_items = len(items)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return f'Legend({self._n_items} items)'

class RadarChart(VCollection):
    """Radar/spider chart visualization."""
    def __init__(self, values, labels=None, max_val=None, colors=None,
                 cx=ORIGIN[0], cy=ORIGIN[1], radius: float = 250, font_size: float = 16,
                 fill_opacity=0.3, creation: float = 0, z: float = 0):
        n = len(values)
        if n < 3:
            raise ValueError(f"RadarChart requires at least 3 values, got {n}")
        if max_val is None:
            max_val = max(values) if values else 1
        if max_val == 0:
            max_val = 1
        if colors is None:
            colors = ['#58C4DD']
        objects = []
        # Draw concentric rings (grid)
        for level in range(1, 4):
            r = radius * level / 3
            ring = Circle(r=r, cx=cx, cy=cy, fill_opacity=0,
                          stroke='#444', stroke_width=1, creation=creation, z=z)
            objects.append(ring)
        # Draw axis lines
        angles = [i * math.tau / n - math.pi / 2 for i in range(n)]
        for angle in angles:
            lx = cx + radius * math.cos(angle)
            ly = cy + radius * math.sin(angle)
            line = Line(x1=cx, y1=cy, x2=lx, y2=ly,
                        stroke='#555', stroke_width=1, creation=creation, z=z)
            objects.append(line)
        # Draw data polygon
        points = []
        for i, val in enumerate(values):
            r = radius * min(val / max_val, 1)
            px = cx + r * math.cos(angles[i])
            py = cy + r * math.sin(angles[i])
            points.append((px, py))
        color = colors[0]
        data_poly = Polygon(*points, fill=color, fill_opacity=fill_opacity,
                            stroke=color, stroke_width=2, creation=creation, z=z + 0.1)
        objects.append(data_poly)
        # Draw data dots
        for px, py in points:
            dot = Dot(cx=px, cy=py, fill=color, creation=creation, z=z + 0.2)
            objects.append(dot)
        # Labels
        if labels:
            for i, label in enumerate(labels[:n]):
                lx = cx + (radius + 30) * math.cos(angles[i])
                ly = cy + (radius + 30) * math.sin(angles[i])
                anchor = 'middle'
                if math.cos(angles[i]) > 0.3:
                    anchor = 'start'
                elif math.cos(angles[i]) < -0.3:
                    anchor = 'end'
                txt = Text(text=label, x=lx, y=ly + font_size * TEXT_Y_OFFSET,
                           font_size=font_size, fill='#ccc', stroke_width=0,
                           text_anchor=anchor, creation=creation, z=z + 0.1)
                objects.append(txt)
        self._data_poly = data_poly
        self._n = n
        self._max_val = max_val
        self._cx, self._cy = cx, cy
        self._radius = radius
        self._angles = angles
        self._colors = colors if colors else ['#58C4DD']
        self._fill_opacity = fill_opacity
        self._dataset_count = 1
        super().__init__(*objects, creation=creation, z=z)

    def add_dataset(self, values, color=None, fill_opacity=None, creation: float = 0, z: float = 0.15):
        """Add an additional data polygon overlay to the radar chart."""
        if len(values) != self._n:
            raise ValueError(f"add_dataset expects {self._n} values, got {len(values)}")
        if color is None:
            cols = _default_colors(None)
            color = cols[self._dataset_count % len(cols)]
        if fill_opacity is None:
            fill_opacity = self._fill_opacity
        points = []
        for i, val in enumerate(values):
            r = self._radius * min(val / self._max_val, 1)
            points.append((self._cx + r * math.cos(self._angles[i]),
                           self._cy + r * math.sin(self._angles[i])))
        poly = Polygon(*points, fill=color, fill_opacity=fill_opacity,
                       stroke=color, stroke_width=2, creation=creation, z=z)
        self.objects.append(poly)
        for px, py in points:
            self.objects.append(Dot(cx=px, cy=py, fill=color, creation=creation, z=z + 0.1))
        self._dataset_count += 1
        return self

    from_dict = classmethod(_from_dict)

    def __repr__(self):
        return 'RadarChart()'

class ProgressBar(VCollection):
    """Animated progress bar that fills from left to right."""
    def __init__(self, width: float = 400, height: float = 30, x: float = 760, y: float = 520,
                 bg_color='#333', fill_color='#58C4DD',
                 corner_radius=6, creation: float = 0, z: float = 0):

        self._bar_width = width
        bg = RoundedRectangle(width, height, x=x, y=y, corner_radius=corner_radius,
                              fill=bg_color, fill_opacity=0.5, stroke_width=0, creation=creation, z=z)
        fill = RoundedRectangle(0.01, height, x=x, y=y, corner_radius=corner_radius,
                                fill=fill_color, fill_opacity=1, stroke_width=0, creation=creation, z=z + 0.1)
        self._fill = fill
        super().__init__(bg, fill, creation=creation, z=z)

    def set_progress(self, value, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Set progress (0 to 1). Animates if end is given."""
        target_w = max(0.01, self._bar_width * _clamp01(value))
        if end is None:
            self._fill.width.set_onward(start, target_w)
        else:
            self._fill.width.move_to(start, end, target_w, easing=easing)
        return self

    animate_to = set_progress  # Alias for backward compat

    def get_progress(self, time: float = 0):
        """Return the current progress value (0-1) at the given time."""
        fill_w = self._fill.width.at_time(time)
        return fill_w / self._bar_width if self._bar_width else 0

    def __repr__(self):
        return f'ProgressBar({self.get_progress():.0%})'

class WaterfallChart(VCollection):
    """Waterfall chart showing cumulative effect of positive/negative values."""
    def __init__(self, values, labels=None, x: float = 200, y: float = 100,
                 width: float = 800, height: float = 400, bar_width: float = 0.7,
                 pos_color='#83C167', neg_color='#FF6B6B', total_color='#58C4DD',
                 connector_color='#666', font_size: float = 16,
                 show_total=True, creation: float = 0, z: float = 0):
        n = len(values)
        if n == 0:
            super().__init__(creation=creation, z=z)
            return
        # Compute cumulative running totals
        cumulative = [0.0]
        for v in values:
            cumulative.append(cumulative[-1] + v)
        all_vals = list(cumulative)
        if show_total:
            all_vals.append(cumulative[-1])
        n_bars = n + (1 if show_total else 0)
        vmin = min(all_vals + [0])
        vmax = max(all_vals + [0])
        vspan = vmax - vmin if vmax != vmin else 1
        # Axes geometry
        margin_left = 60
        margin_bottom = 50
        plot_w = width - margin_left
        plot_h = height - margin_bottom
        bar_step = plot_w / max(n_bars, 1)
        def _val_to_y(v):
            return y + plot_h - (v - vmin) / vspan * plot_h
        objects = []
        # Y-axis line
        y_axis = Line(x1=x + margin_left, y1=y, x2=x + margin_left, y2=y + plot_h,
                      stroke='#888', stroke_width=1, creation=creation, z=z)
        objects.append(y_axis)
        # Zero line
        zero_y = _val_to_y(0)
        zero_line = Line(x1=x + margin_left, y1=zero_y,
                         x2=x + width, y2=zero_y,
                         stroke='#555', stroke_width=1,
                         stroke_dasharray='4 3', creation=creation, z=z)
        objects.append(zero_line)
        def _bar_x(idx):
            return x + margin_left + idx * bar_step + bar_step * (1 - bar_width) / 2
        bw = bar_step * bar_width
        def _add_bar(idx, base_y, top_y, color, lbl_text, val_text):
            bx = _bar_x(idx)
            by_top = _val_to_y(max(base_y, top_y))
            bh = abs(_val_to_y(base_y) - _val_to_y(top_y))
            rect = Rectangle(width=bw, height=max(bh, 1), x=bx, y=by_top,
                              fill=color, fill_opacity=0.8, stroke=color, stroke_width=1,
                              creation=creation, z=z + 0.1)
            self._bars.append(rect)
            objects.append(rect)
            objects.append(Text(text=lbl_text, x=bx + bw / 2, y=y + plot_h + 20,
                                font_size=font_size, fill='#ccc', stroke_width=0,
                                text_anchor='middle', creation=creation, z=z + 0.2))
            objects.append(Text(text=val_text, x=bx + bw / 2, y=by_top - 5,
                                font_size=font_size - 2, fill=color, stroke_width=0,
                                text_anchor='middle', creation=creation, z=z + 0.2))
        # Bars
        self._bars = []
        for i in range(n):
            v = values[i]
            base, top = cumulative[i], cumulative[i + 1]
            color = pos_color if v >= 0 else neg_color
            lbl = labels[i] if labels and i < len(labels) else str(i)
            val_text = f'{v:+.1f}' if v != int(v) else f'{v:+.0f}'
            _add_bar(i, base, top, color, lbl, val_text)
            # Connector line to next bar
            if i < n - 1 or show_total:
                bx = _bar_x(i)
                conn = Line(x1=bx + bw, y1=_val_to_y(top),
                            x2=_bar_x(i + 1), y2=_val_to_y(top),
                            stroke=connector_color, stroke_width=1,
                            stroke_dasharray='3 2', creation=creation, z=z + 0.05)
                objects.append(conn)
        # Total bar
        if show_total:
            total = cumulative[-1]
            lbl = labels[n] if labels and n < len(labels) else 'Total'
            val_text = f'{total:.1f}' if total != int(total) else f'{int(total)}'
            _add_bar(n, 0, total, total_color, lbl, val_text)
        super().__init__(*objects, creation=creation, z=z)

    from_dict = classmethod(_from_dict)

    def __repr__(self):
        return 'WaterfallChart()'

class GanttChart(VCollection):
    """Gantt chart for project timelines."""
    def __init__(self, tasks, x: float = 100, y: float = 80, width: float = 1200,
                 bar_height: float = 30, bar_spacing: float = 10, colors=None,
                 font_size: float = 16, creation: float = 0, z: float = 0):
        n = len(tasks)
        if n == 0:
            super().__init__(creation=creation, z=z)
            return
        colors = _default_colors(colors)
        # Compute time range
        all_starts = [t[1] for t in tasks]
        all_ends = [t[2] for t in tasks]
        t_min, t_max = min(all_starts), max(all_ends)
        t_span = t_max - t_min if t_max != t_min else 1
        label_w = 120
        chart_x = x + label_w
        chart_w = width - label_w
        objects = []
        # Header line
        header = Line(x1=chart_x, y1=y, x2=chart_x + chart_w, y2=y,
                      stroke='#555', stroke_width=1, creation=creation, z=z)
        objects.append(header)
        # Time axis ticks
        n_ticks = min(10, int(t_span) + 1) if t_span >= 1 else 2
        for i in range(n_ticks + 1):
            frac = i / max(n_ticks, 1)
            tx = chart_x + frac * chart_w
            tv = t_min + frac * t_span
            tick = Line(x1=tx, y1=y - 5, x2=tx, y2=y + 5,
                        stroke='#666', stroke_width=1, creation=creation, z=z)
            objects.append(tick)
            label = f'{tv:.0f}' if tv == int(tv) else f'{tv:.1f}'
            lbl = Text(text=label, x=tx, y=y - 10,
                       font_size=font_size - 2, fill='#aaa', stroke_width=0,
                       text_anchor='middle', creation=creation, z=z + 0.1)
            objects.append(lbl)
        # Task bars
        self._bars = []
        for i, task in enumerate(tasks):
            task_label = task[0]
            t_start, t_end = task[1], task[2]
            color = task[3] if len(task) > 3 else colors[i % len(colors)]
            by = y + 20 + i * (bar_height + bar_spacing)
            bx = chart_x + (t_start - t_min) / t_span * chart_w
            bw = max(2, (t_end - t_start) / t_span * chart_w)
            rect = Rectangle(width=bw, height=bar_height, x=bx, y=by,
                              fill=color, fill_opacity=0.8, stroke=color,
                              stroke_width=1, rx=4, ry=4,
                              creation=creation, z=z + 0.1)
            self._bars.append(rect)
            objects.append(rect)
            # Label
            lbl = Text(text=task_label, x=x + 5, y=by + bar_height / 2 + font_size * TEXT_Y_OFFSET,
                       font_size=font_size, fill='#ccc', stroke_width=0,
                       text_anchor='start', creation=creation, z=z + 0.1)
            objects.append(lbl)
            # Grid line
            grid = Line(x1=chart_x, y1=by + bar_height + bar_spacing / 2,
                        x2=chart_x + chart_w, y2=by + bar_height + bar_spacing / 2,
                        stroke='#333', stroke_width=0.5, creation=creation, z=z - 0.1)
            objects.append(grid)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'GanttChart()'

class SankeyDiagram(VCollection):
    """Sankey flow diagram showing flows between nodes."""
    def __init__(self, flows, x: float = 100, y: float = 100, width: float = 1200, height: float = 600,
                 node_width: float = 30, node_spacing: float = 20, colors=None,
                 font_size: float = 16, creation: float = 0, z: float = 0):
        if not flows:
            super().__init__(creation=creation, z=z)
            return
        colors = _default_colors(colors)
        sources = list(dict.fromkeys(src for src, _, _ in flows))
        targets = list(dict.fromkeys(tgt for _, tgt, _ in flows))
        src_totals = {s: sum(v for ss, _, v in flows if ss == s) for s in sources}
        tgt_totals = {t: sum(v for _, tt, v in flows if tt == t) for t in targets}
        max_total = max(max(src_totals.values()), max(tgt_totals.values())) or 1

        def _layout(names, totals, left_x):
            sc = (height - (len(names) - 1) * node_spacing) / max_total
            rects, cy = {}, y
            for n in names:
                h = max(totals[n] * sc, 2)
                rects[n] = (left_x, cy, node_width, h)
                cy += h + node_spacing
            return rects, sc

        src_rects, scale = _layout(sources, src_totals, x)
        tgt_rects, tgt_scale = _layout(targets, tgt_totals, x + width - node_width)
        objects = []
        # Flow paths (cubic bezier)
        src_offsets = {s: 0.0 for s in sources}
        tgt_offsets = {t: 0.0 for t in targets}
        for i, (src, tgt, val) in enumerate(flows):
            color = colors[i % len(colors)]
            sx, sy, sw, _ = src_rects[src]
            tx, ty, _, _ = tgt_rects[tgt]
            fhs, fht = val * scale, val * tgt_scale
            y0, y1 = sy + src_offsets[src], ty + tgt_offsets[tgt]
            src_offsets[src] += fhs
            tgt_offsets[tgt] += fht
            x0, x3 = sx + sw, tx
            cx1, cx2 = x0 + (x3 - x0) * 0.4, x0 + (x3 - x0) * 0.6
            d = (f'M{x0:.1f},{y0:.1f} '
                 f'C{cx1:.1f},{y0:.1f} {cx2:.1f},{y1:.1f} {x3:.1f},{y1:.1f} '
                 f'L{x3:.1f},{y1 + fht:.1f} '
                 f'C{cx2:.1f},{y1 + fht:.1f} {cx1:.1f},{y0 + fhs:.1f} '
                 f'{x0:.1f},{y0 + fhs:.1f} Z')
            objects.append(Path(d, x=0, y=0, fill=color, fill_opacity=0.4,
                                stroke=color, stroke_width=0.5, stroke_opacity=0.6,
                                creation=creation, z=z + 0.1))
        # Node rectangles + labels
        def _draw_nodes(names, rects, color_offset, anchor, lbl_dx):
            for i, n in enumerate(names):
                bx, by, bw, bh = rects[n]
                c = colors[(color_offset + i) % len(colors)]
                objects.append(Rectangle(width=bw, height=bh, x=bx, y=by,
                                         fill=c, fill_opacity=0.9, stroke_width=0,
                                         creation=creation, z=z + 0.2))
                objects.append(Text(text=n, x=bx + lbl_dx,
                                    y=by + bh / 2 + font_size * TEXT_Y_OFFSET,
                                    font_size=font_size, fill='#ddd', stroke_width=0,
                                    text_anchor=anchor, creation=creation, z=z + 0.3))
        _draw_nodes(sources, src_rects, 0, 'end', -5)
        _draw_nodes(targets, tgt_rects, len(sources), 'start', node_width + 5)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'SankeyDiagram()'

class FunnelChart(VCollection):
    """Funnel chart showing progressive narrowing stages."""
    def __init__(self, stages, x: float = 100, y: float = 100, width: float = 600, height: float = 500,
                 colors=None, font_size: float = 18, gap: float = 4, creation: float = 0, z: float = 0):
        if not stages:
            super().__init__(creation=creation, z=z)
            return
        colors = _default_colors(colors)
        n = len(stages)
        max_val = max(v for _, v in stages) or 1
        row_h = (height - (n - 1) * gap) / n
        cx = x + width / 2
        objects = []
        for i, (label, val) in enumerate(stages):
            top_w = width if i == 0 else width * stages[i - 1][1] / max_val
            bot_w = width * val / max_val
            ty = y + i * (row_h + gap)
            by = ty + row_h
            pts = [(cx - top_w / 2, ty), (cx + top_w / 2, ty),
                   (cx + bot_w / 2, by), (cx - bot_w / 2, by)]
            color = colors[i % len(colors)]
            trap = Polygon(*pts, fill=color, fill_opacity=0.85, stroke=color,
                           stroke_width=1, creation=creation, z=z)
            objects.append(trap)
            lbl = Text(text=f'{label} ({val})', x=cx, y=ty + row_h / 2 + font_size * TEXT_Y_OFFSET,
                       font_size=font_size, fill='#fff', stroke_width=0,
                       text_anchor='middle', creation=creation, z=z + 0.1)
            objects.append(lbl)
        super().__init__(*objects, creation=creation, z=z)

    @classmethod
    def from_dict(cls, data, **kwargs):
        """Create from dict {label: value}."""
        return cls(list(data.items()), **kwargs)

    def __repr__(self):
        return 'FunnelChart()'

class TreeMap(VCollection):
    """Treemap visualization using squarified layout."""
    def __init__(self, data, x: float = 100, y: float = 100, width: float = 800, height: float = 600,
                 colors=None, font_size: float = 14, padding: float = 2, creation: float = 0, z: float = 0):
        if not data:
            super().__init__(creation=creation, z=z)
            return
        colors = _default_colors(colors)
        total = sum(v for _, v in data) or 1
        # Sort descending by value for squarified layout
        sorted_data = sorted(enumerate(data), key=lambda iv: iv[1][1], reverse=True)
        rects = self._squarify(sorted_data, x, y, width, height, total)
        objects = []
        for orig_idx, (label, _), (rx, ry, rw, rh) in rects:
            color = colors[orig_idx % len(colors)]
            rect = Rectangle(width=max(rw - padding, 1), height=max(rh - padding, 1),
                              x=rx + padding / 2, y=ry + padding / 2,
                              fill=color, fill_opacity=0.8, stroke='#222', stroke_width=1,
                              creation=creation, z=z)
            objects.append(rect)
            if rw > font_size * 2 and rh > font_size * 1.5:
                lbl = Text(text=str(label), x=rx + rw / 2, y=ry + rh / 2 + font_size * TEXT_Y_OFFSET,
                           font_size=min(font_size, rw / max(len(str(label)), 1) * 1.5),
                           fill='#fff', stroke_width=0, text_anchor='middle',
                           creation=creation, z=z + 0.1)
                objects.append(lbl)
        super().__init__(*objects, creation=creation, z=z)

    @classmethod
    def from_dict(cls, data, **kwargs):
        """Create from dict {label: value}."""
        return cls(list(data.items()), **kwargs)

    def __repr__(self):
        return 'TreeMap()'

    @staticmethod
    def _squarify(items, x, y, w, h, total):
        """Squarified treemap layout. Returns list of (orig_idx, (label, val), (rx, ry, rw, rh))."""
        if not items:
            return []
        if len(items) == 1:
            idx, (label, val) = items[0]
            return [(idx, (label, val), (x, y, w, h))]
        area = w * h
        result = []
        remaining = deque(items)
        cx, cy, cw, ch = x, y, w, h
        while remaining:
            if len(remaining) == 1:
                idx, (label, val) = remaining[0]
                result.append((idx, (label, val), (cx, cy, cw, ch)))
                break
            # Lay out along shorter side
            short = min(cw, ch)
            row = [remaining.popleft()]
            row_area = row[0][1][1] / total * area

            def _worst(row_items, side, r_area):
                if side <= 0 or r_area <= 0:
                    return math.inf
                s2 = side * side
                return max(max(s2 * r_area / (itm[1][1] / total * area) ** 2,
                               (itm[1][1] / total * area) ** 2 / (s2 * r_area))
                           for itm in row_items)

            while remaining:
                candidate = remaining[0]
                new_area = row_area + candidate[1][1] / total * area
                if _worst(row + [candidate], short, new_area) <= _worst(row, short, row_area):
                    row.append(remaining.popleft())
                    row_area = new_area
                else:
                    break
            # Place row
            if cw <= ch:  # horizontal strip at top
                strip_h = row_area / max(cw, 1)
                rx = cx
                for idx, (label, val) in row:
                    rw = (val / total * area) / max(strip_h, 1)
                    result.append((idx, (label, val), (rx, cy, rw, strip_h)))
                    rx += rw
                cy += strip_h
                ch -= strip_h
            else:  # vertical strip at left
                strip_w = row_area / max(ch, 1)
                ry = cy
                for idx, (label, val) in row:
                    rh = (val / total * area) / max(strip_w, 1)
                    result.append((idx, (label, val), (cx, ry, strip_w, rh)))
                    ry += rh
                cx += strip_w
                cw -= strip_w
        return result

class GaugeChart(VCollection):
    """Speedometer / gauge chart."""
    def __init__(self, value, min_val: float = 0, max_val: float = 100, x=ORIGIN[0], y=ORIGIN[1],
                 radius: float = 200, start_angle: float = 225, end_angle=-45,
                 colors=None, label=None, font_size: float = 36,
                 tick_count=5, creation: float = 0, z: float = 0):
        if colors is None:
            colors = [('#83C167', 0.0), ('#FFFF00', 0.5), ('#FF6B6B', 1.0)]
        objects = []
        # Background arc segments (colored bands)
        n_segments = 60
        sa_rad = math.radians(start_angle)
        ea_rad = math.radians(end_angle)
        if ea_rad > sa_rad:
            ea_rad -= math.tau
        total_sweep = ea_rad - sa_rad
        for i in range(n_segments):
            frac = i / n_segments
            a0 = sa_rad + total_sweep * frac
            a1 = sa_rad + total_sweep * (frac + 1 / n_segments)
            # Interpolate color
            seg_color = GaugeChart._interp_gauge_color(frac, colors)
            arc = Arc(cx=x, cy=y, r=radius, start_angle=math.degrees(a0),
                      end_angle=math.degrees(a1), stroke=seg_color,
                      stroke_width=20, creation=creation, z=z)
            objects.append(arc)
        # Tick marks + labels
        for i in range(tick_count + 1):
            frac = i / max(tick_count, 1)
            angle = sa_rad + total_sweep * frac
            tick_val = min_val + (max_val - min_val) * frac
            ix = x + (radius + 18) * math.cos(angle)
            iy = y - (radius + 18) * math.sin(angle)
            ox = x + (radius - 15) * math.cos(angle)
            oy = y - (radius - 15) * math.sin(angle)
            tick = Line(x1=ox, y1=oy, x2=ix, y2=iy, stroke='#888',
                        stroke_width=1.5, creation=creation, z=z + 0.1)
            objects.append(tick)
            lx = x + (radius + 35) * math.cos(angle)
            ly = y - (radius + 35) * math.sin(angle)
            tlbl = Text(text=f'{tick_val:.0f}', x=lx, y=ly + font_size * 0.2,
                        font_size=font_size * 0.4, fill='#aaa', stroke_width=0,
                        text_anchor='middle', creation=creation, z=z + 0.1)
            objects.append(tlbl)
        # Needle
        val_frac = _clamp01((value - min_val) / max(max_val - min_val, 1))
        needle_angle = sa_rad + total_sweep * val_frac
        nx = x + (radius - 30) * math.cos(needle_angle)
        ny = y - (radius - 30) * math.sin(needle_angle)
        needle = Line(x1=x, y1=y, x2=nx, y2=ny, stroke='#fff',
                      stroke_width=3, creation=creation, z=z + 0.2)
        objects.append(needle)
        # Center dot
        center = Dot(cx=x, cy=y, r=8, fill='#fff', stroke_width=0,
                     creation=creation, z=z + 0.3)
        objects.append(center)
        # Value label
        val_lbl = Text(text=f'{value:.0f}', x=x, y=y + radius * 0.4,
                       font_size=font_size, fill='#fff', stroke_width=0,
                       text_anchor='middle', creation=creation, z=z + 0.3)
        objects.append(val_lbl)
        if label:
            sub_lbl = Text(text=str(label), x=x, y=y + radius * 0.4 + font_size * 1.2,
                           font_size=font_size * 0.5, fill='#aaa', stroke_width=0,
                           text_anchor='middle', creation=creation, z=z + 0.3)
            objects.append(sub_lbl)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'GaugeChart()'

    @staticmethod
    def _interp_gauge_color(frac, colors):
        """Interpolate gauge color from color stops list [(color, position), ...]."""
        from vectormation.colors import interpolate_color
        if not colors:
            return '#888'
        if frac <= colors[0][1]:
            return colors[0][0]
        if frac >= colors[-1][1]:
            return colors[-1][0]
        for (c0, p0), (c1, p1) in zip(colors, colors[1:]):
            if p0 <= frac <= p1:
                return interpolate_color(c0, c1, (frac - p0) / max(p1 - p0, 1e-9))
        return colors[-1][0]

class SparkLine(VObject):
    """Minimal inline chart (sparkline) rendered as a single SVG path."""
    def __init__(self, data, x: float = 100, y: float = 100, width: float = 120, height: float = 30,
                 stroke='#58C4DD', stroke_width: float = 1.5,
                 show_endpoint=False, creation: float = 0, z: float = 0, **styling_kwargs):
        kw = {'stroke': stroke, 'stroke_width': stroke_width,
              'fill_opacity': 0} | styling_kwargs
        super().__init__(creation=creation, z=z)
        self.styling = style.Styling(kw, creation=creation, stroke='#58C4DD')
        self._data = list(data)
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._show_endpoint = show_endpoint
        self._endpoint_r = 2.5

    def _extra_attrs(self):
        return []

    def path(self, time):  # noqa: ARG002
        data = self._data
        if len(data) < 2:
            return ''
        mn, mx = min(data), max(data)
        rng = mx - mn if mx != mn else 1
        n = len(data)
        dx = self._width / (n - 1)
        pts = []
        for i, v in enumerate(data):
            px = self._x + i * dx
            py = self._y + self._height - (v - mn) / rng * self._height
            pts.append(f'{px:.1f},{py:.1f}')
        return 'M' + 'L'.join(pts)

    def snap_points(self, time):  # noqa: ARG002
        return [(self._x, self._y), (self._x + self._width, self._y + self._height)]

    def to_svg(self, time):
        d = self.path(time)
        if not d:
            return ''
        s = self.styling.svg_style(time)
        svg = f'<path d="{d}"{s}/>'
        if self._show_endpoint and len(self._data) >= 2:
            mn, mx = min(self._data), max(self._data)
            rng = mx - mn if mx != mn else 1
            last = self._data[-1]
            ex = self._x + self._width
            ey = self._y + self._height - (last - mn) / rng * self._height
            sc = self.styling.stroke.time_func(time)
            color = f'rgb({int(sc[0])},{int(sc[1])},{int(sc[2])})' if isinstance(sc, tuple) else str(sc)
            svg += f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{self._endpoint_r}" fill="{color}"/>'
        return svg

    def __repr__(self):
        return 'SparkLine()'

class KPICard(VCollection):
    """Metric card showing a title, large value, optional subtitle and trend sparkline."""
    def __init__(self, title, value, subtitle=None, trend_data=None,
                 x: float = 100, y: float = 100, width: float = 280, height: float = 160,
                 bg_color='#1a1a2e', title_color='#aaa', value_color='#fff',
                 font_size: float = 48, creation: float = 0, z: float = 0):
        objects = []
        # Background card

        bg = RoundedRectangle(width=width, height=height, x=x, y=y,
                               corner_radius=10, fill=bg_color, fill_opacity=0.9,
                               stroke='#333', stroke_width=1,
                               creation=creation, z=z)
        objects.append(bg)
        # Title
        t_lbl = Text(text=str(title), x=x + width / 2, y=y + 30,
                     font_size=font_size * 0.5, fill=title_color, stroke_width=0,
                     text_anchor='middle', creation=creation, z=z + 0.1)
        objects.append(t_lbl)
        # Value
        v_lbl = Text(text=str(value), x=x + width / 2, y=y + height * 0.5 + font_size * TEXT_Y_OFFSET,
                     font_size=font_size, fill=value_color, stroke_width=0,
                     text_anchor='middle', creation=creation, z=z + 0.1)
        objects.append(v_lbl)
        # Subtitle
        if subtitle:
            s_lbl = Text(text=str(subtitle), x=x + width / 2,
                         y=y + height * 0.5 + font_size * TEXT_Y_OFFSET + font_size * CHAR_WIDTH_FACTOR,
                         font_size=font_size * 0.3, fill=title_color, stroke_width=0,
                         text_anchor='middle', creation=creation, z=z + 0.1)
            objects.append(s_lbl)
        # Trend sparkline
        if trend_data and len(trend_data) >= 2:
            sl_w = width * 0.6
            sl_h = height * 0.15
            sl_x = x + (width - sl_w) / 2
            sl_y = y + height - sl_h - 15
            spark = SparkLine(trend_data, x=sl_x, y=sl_y, width=sl_w, height=sl_h,
                              stroke='#58C4DD', stroke_width=1, show_endpoint=True,
                              creation=creation, z=z + 0.1)
            objects.append(spark)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'KPICard()'

class BulletChart(VCollection):
    """Bullet chart: qualitative ranges + actual bar + target marker."""
    def __init__(self, actual, target, ranges=None, label=None,
                 x: float = 100, y: float = 100, width: float = 500, height: float = 40,
                 bar_color='#333', target_color='#fff',
                 font_size: float = 16, max_val=None, creation: float = 0, z: float = 0):
        if ranges is None:
            ranges = [(0.5, '#2a2a3a'), (0.75, '#3a3a4a'), (1.0, '#4a4a5a')]
        if max_val is None:
            max_val = max(actual, target, max(v for v, _ in ranges) if ranges else 1)
            if max_val <= 0:
                max_val = 1
        objects = []
        # Qualitative range backgrounds
        prev = 0
        for val, color in sorted(ranges, key=lambda vc: vc[0]):
            rw = (val - prev) / max_val * width
            rect = Rectangle(width=max(rw, 0), height=height,
                              x=x + prev / max_val * width, y=y,
                              fill=color, fill_opacity=1, stroke_width=0,
                              creation=creation, z=z)
            objects.append(rect)
            prev = val
        # Actual value bar
        bar_h = height * 0.5
        bar_w = max(actual / max_val * width, 0)
        bar = Rectangle(width=bar_w, height=bar_h,
                         x=x, y=y + (height - bar_h) / 2,
                         fill=bar_color, fill_opacity=1, stroke_width=0,
                         creation=creation, z=z + 0.1)
        objects.append(bar)
        # Target marker
        tx = x + target / max_val * width
        marker = Line(x1=tx, y1=y + height * 0.15, x2=tx, y2=y + height * 0.85,
                      stroke=target_color, stroke_width=2.5,
                      creation=creation, z=z + 0.2)
        objects.append(marker)
        # Label
        if label:
            lbl = Text(text=str(label), x=x - 10, y=y + height / 2 + font_size * TEXT_Y_OFFSET,
                       font_size=font_size, fill='#ddd', stroke_width=0,
                       text_anchor='end', creation=creation, z=z + 0.1)
            objects.append(lbl)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'BulletChart()'

class CalendarHeatmap(VCollection):
    """Grid heatmap like a GitHub contribution graph."""
    def __init__(self, data, rows: int = 7, cols: int = 52, x: float = 100, y: float = 100,  # noqa: ARG002 (cols reserved for layout hints)
                 cell_size: float = 14, gap: float = 2, colormap=None,
                 creation: float = 0, z: float = 0):
        if colormap is None:
            colormap = ['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353']
        # Normalize data to dict
        if isinstance(data, dict):
            grid = data
        else:
            grid = {}
            flat = list(data)
            for idx, val in enumerate(flat):
                r = idx % rows
                c = idx // rows
                grid[(r, c)] = val
        if not grid:
            super().__init__(creation=creation, z=z)
            return
        vals = list(grid.values())
        mn, mx = min(vals), max(vals)
        rng = mx - mn if mx != mn else 1
        objects = []
        for (r, c), val in grid.items():
            frac = (val - mn) / rng
            ci = min(int(frac * (len(colormap) - 1) + 0.5), len(colormap) - 1)
            color = colormap[ci]
            rx = x + c * (cell_size + gap)
            ry = y + r * (cell_size + gap)
            rect = Rectangle(width=cell_size, height=cell_size, x=rx, y=ry,
                              fill=color, fill_opacity=1, stroke_width=0,
                              creation=creation, z=z)
            objects.append(rect)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'CalendarHeatmap()'

class WaffleChart(VCollection):
    """Waffle chart: grid of colored squares showing category proportions."""
    def __init__(self, categories, x: float = 100, y: float = 100, grid_size: int = 10,
                 cell_size: float = 20, gap: float = 3, font_size: float = 14, creation: float = 0, z: float = 0):
        total = sum(v for _, v, _ in categories) or 1
        n_cells = grid_size * grid_size
        objects = []
        cell_idx = 0
        legend_objs = []
        for label, val, color in categories:
            count = round(val / total * n_cells)
            for _ in range(count):
                if cell_idx >= n_cells:
                    break
                r = cell_idx // grid_size
                c = cell_idx % grid_size
                rx = x + c * (cell_size + gap)
                ry = y + r * (cell_size + gap)
                rect = Rectangle(width=cell_size, height=cell_size, x=rx, y=ry,
                                  fill=color, fill_opacity=0.9, stroke_width=0,
                                  creation=creation, z=z)
                objects.append(rect)
                cell_idx += 1
            # Legend entry
            lx = x + grid_size * (cell_size + gap) + 15
            ly = y + len(legend_objs) * (font_size * 1.5)
            swatch = Rectangle(width=font_size, height=font_size,
                                x=lx, y=ly, fill=color, fill_opacity=0.9,
                                stroke_width=0, creation=creation, z=z + 0.1)
            lbl = Text(text=f'{label} ({val})', x=lx + font_size + 5,
                       y=ly + font_size * 0.8, font_size=font_size,
                       fill='#ddd', stroke_width=0, text_anchor='start',
                       creation=creation, z=z + 0.1)
            legend_objs += [swatch, lbl]
        # Fill remaining cells with empty color
        while cell_idx < n_cells:
            r = cell_idx // grid_size
            c = cell_idx % grid_size
            rx = x + c * (cell_size + gap)
            ry = y + r * (cell_size + gap)
            rect = Rectangle(width=cell_size, height=cell_size, x=rx, y=ry,
                              fill='#1a1a2e', fill_opacity=0.5, stroke_width=0,
                              creation=creation, z=z)
            objects.append(rect)
            cell_idx += 1
        super().__init__(*(objects + legend_objs), creation=creation, z=z)

    def __repr__(self):
        return 'WaffleChart()'

class CircularProgressBar(VCollection):
    """Circular progress indicator with percentage text."""
    def __init__(self, value, x=ORIGIN[0], y=ORIGIN[1], radius: float = 80, stroke_width: float = 12,
                 track_color='#2a2a3a', bar_color='#58C4DD',
                 font_size: float = 36, show_text=True, creation: float = 0, z: float = 0):
        objects = []
        # Background track (full circle arc)
        track = Arc(cx=x, cy=y, r=radius, start_angle=90, end_angle=90 - 359.99,
                    stroke=track_color, stroke_width=stroke_width,
                    creation=creation, z=z)
        objects.append(track)
        # Progress arc
        pct = max(0, min(100, value))
        sweep = 360 * pct / 100
        if sweep > 0.1:
            prog = Arc(cx=x, cy=y, r=radius, start_angle=90,
                       end_angle=90 - sweep,
                       stroke=bar_color, stroke_width=stroke_width,
                       creation=creation, z=z + 0.1)
            objects.append(prog)
        # Text
        if show_text:
            lbl = Text(text=f'{pct:.0f}%', x=x, y=y + font_size * TEXT_Y_OFFSET,
                       font_size=font_size, fill=bar_color, stroke_width=0,
                       text_anchor='middle', creation=creation, z=z + 0.2)
            objects.append(lbl)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'CircularProgressBar()'

class Scoreboard(VCollection):
    """Score/metric display panel."""
    def __init__(self, entries, x: float = 100, y: float = 100, col_width: float = 200, row_height: float = 60,
                 bg_color='#1a1a2e', label_color='#aaa', value_color='#fff',
                 font_size: float = 28, cols=None, creation: float = 0, z: float = 0):
        self._n_entries = len(entries) if entries else 0
        if not entries:
            super().__init__(creation=creation, z=z)
            return
        if cols is None:
            cols = min(len(entries), 4)
        rows_count = math.ceil(len(entries) / cols)
        total_w = cols * col_width
        total_h = rows_count * row_height

        objects = []
        # Background
        bg = RoundedRectangle(width=total_w + 20, height=total_h + 20,
                               x=x - 10, y=y - 10, corner_radius=10,
                               fill=bg_color, fill_opacity=0.9,
                               stroke='#333', stroke_width=1,
                               creation=creation, z=z)
        objects.append(bg)
        for i, (label, value) in enumerate(entries):
            r = i // cols
            c = i % cols
            cx = x + c * col_width + col_width / 2
            cy = y + r * row_height
            # Value
            v_lbl = Text(text=str(value), x=cx, y=cy + font_size * 0.9,
                         font_size=font_size, fill=value_color, stroke_width=0,
                         text_anchor='middle', creation=creation, z=z + 0.1)
            objects.append(v_lbl)
            # Label
            l_lbl = Text(text=str(label), x=cx,
                         y=cy + font_size * 0.9 + font_size * 0.7,
                         font_size=font_size * 0.4, fill=label_color, stroke_width=0,
                         text_anchor='middle', creation=creation, z=z + 0.1)
            objects.append(l_lbl)
            # Divider (between columns)
            if c < cols - 1 and i < len(entries) - 1:
                dx = x + (c + 1) * col_width
                div = Line(x1=dx, y1=cy + 5, x2=dx, y2=cy + row_height - 5,
                           stroke='#333', stroke_width=1,
                           creation=creation, z=z + 0.05)
                objects.append(div)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return f'Scoreboard({self._n_entries} rows)'

class MatrixHeatmap(VCollection):
    """Labeled matrix heatmap with colored cells."""
    def __init__(self, data, row_labels=None, col_labels=None,
                 x: float = 100, y: float = 100, cell_size: float = 50, gap: float = 2,
                 colormap=None, font_size: float = 14, show_values=True,
                 creation: float = 0, z: float = 0):
        if not data or not data[0]:
            super().__init__(creation=creation, z=z)
            return
        if colormap is None:
            colormap = ['#313695', '#4575b4', '#74add1', '#abd9e9',
                        '#fee090', '#fdae61', '#f46d43', '#d73027']
        n_rows = len(data)
        n_cols = len(data[0])
        # Flatten to find min/max
        flat = [v for row in data for v in row]
        if not flat:
            super().__init__(creation=creation, z=z)
            return
        mn, mx = min(flat), max(flat)
        rng = mx - mn if mx != mn else 1
        objects = []
        label_offset = 0
        if row_labels and len(row_labels) > 0:
            label_offset = max((len(str(l)) for l in row_labels), default=0) * font_size * 0.5 + 10
        col_offset = font_size + 10 if col_labels else 0
        for r in range(n_rows):
            for c in range(n_cols):
                val = data[r][c]
                frac = (val - mn) / rng
                ci = min(int(frac * (len(colormap) - 1) + 0.5), len(colormap) - 1)
                color = colormap[ci]
                rx = x + label_offset + c * (cell_size + gap)
                ry = y + col_offset + r * (cell_size + gap)
                rect = Rectangle(width=cell_size, height=cell_size, x=rx, y=ry,
                                  fill=color, fill_opacity=0.9, stroke='#222',
                                  stroke_width=0.5, creation=creation, z=z)
                objects.append(rect)
                if show_values:
                    vlbl = Text(text=f'{val:.1f}' if isinstance(val, float) else str(val),
                                x=rx + cell_size / 2, y=ry + cell_size / 2 + font_size * TEXT_Y_OFFSET,
                                font_size=font_size * 0.8, fill='#fff', stroke_width=0,
                                text_anchor='middle', creation=creation, z=z + 0.1)
                    objects.append(vlbl)
        # Row labels
        if row_labels:
            for r, label in enumerate(row_labels[:n_rows]):
                ry = y + col_offset + r * (cell_size + gap)
                lbl = Text(text=str(label), x=x + label_offset - 8,
                           y=ry + cell_size / 2 + font_size * TEXT_Y_OFFSET,
                           font_size=font_size, fill='#aaa', stroke_width=0,
                           text_anchor='end', creation=creation, z=z + 0.1)
                objects.append(lbl)
        # Column labels
        if col_labels:
            for c, label in enumerate(col_labels[:n_cols]):
                cx = x + label_offset + c * (cell_size + gap) + cell_size / 2
                lbl = Text(text=str(label), x=cx, y=y + font_size * 0.8,
                           font_size=font_size, fill='#aaa', stroke_width=0,
                           text_anchor='middle', creation=creation, z=z + 0.1)
                objects.append(lbl)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'MatrixHeatmap()'

class BoxPlot(VCollection):
    """Box-and-whisker plot for one or more data groups."""
    def __init__(self, data_groups, positions=None, x: float = 100, y: float = 100,
                 plot_width: float = 400, plot_height: float = 300, box_width: float = 30,
                 box_color='#58C4DD', whisker_color='#aaa', median_color='#FF6B6B',
                 font_size: float = 12, creation: float = 0, z: float = 0):
        if not data_groups:
            super().__init__(creation=creation, z=z)
            return
        if positions is None:
            positions = list(range(1, len(data_groups) + 1))
        # Compute stats for each group
        stats = []
        for grp in data_groups:
            s = sorted(grp)
            n = len(s)
            q1 = s[n // 4] if n >= 4 else s[0]
            med = s[n // 2]
            q3 = s[3 * n // 4] if n >= 4 else s[-1]
            iqr = q3 - q1
            lo = max(s[0], q1 - 1.5 * iqr)
            hi = min(s[-1], q3 + 1.5 * iqr)
            stats.append((lo, q1, med, q3, hi))
        # Determine data range
        all_vals = [v for grp in data_groups for v in grp]
        y_min, y_max = min(all_vals), max(all_vals)
        y_rng = y_max - y_min if y_max != y_min else 1
        x_min, x_max = min(positions) - 0.5, max(positions) + 0.5
        x_rng = x_max - x_min if x_max != x_min else 1
        def to_px(xv, yv):
            px = x + (xv - x_min) / x_rng * plot_width
            py = y + plot_height - (yv - y_min) / y_rng * plot_height
            return px, py
        objects = []
        half = box_width / 2
        for pos, (lo, q1, med, q3, hi) in zip(positions, stats):
            cx, _ = to_px(pos, 0)
            _, py_lo = to_px(0, lo)
            _, py_q1 = to_px(0, q1)
            _, py_med = to_px(0, med)
            _, py_q3 = to_px(0, q3)
            _, py_hi = to_px(0, hi)
            # Box (Q1 to Q3)
            bh = abs(py_q1 - py_q3)
            box = Rectangle(width=box_width, height=bh, x=cx - half, y=min(py_q1, py_q3),
                            fill=box_color, fill_opacity=0.3, stroke=box_color,
                            stroke_width=1.5, creation=creation, z=z)
            objects.append(box)
            # Median line
            ml = Line(x1=cx - half, y1=py_med, x2=cx + half, y2=py_med,
                      stroke=median_color, stroke_width=2, creation=creation, z=z + 0.1)
            objects.append(ml)
            # Whiskers
            for wy in [py_lo, py_hi]:
                cap = Line(x1=cx - half * 0.6, y1=wy, x2=cx + half * 0.6, y2=wy,
                           stroke=whisker_color, stroke_width=1.5, creation=creation, z=z)
                objects.append(cap)
            stem_lo = Line(x1=cx, y1=py_q1, x2=cx, y2=py_lo,
                           stroke=whisker_color, stroke_width=1, creation=creation, z=z)
            stem_hi = Line(x1=cx, y1=py_q3, x2=cx, y2=py_hi,
                           stroke=whisker_color, stroke_width=1, creation=creation, z=z)
            objects.extend([stem_lo, stem_hi])
            # Position label
            _, py_bottom = to_px(0, y_min)
            lbl = Text(text=str(pos), x=cx, y=py_bottom + font_size + 4,
                       font_size=font_size, fill='#888', stroke_width=0,
                       text_anchor='middle', creation=creation, z=z)
            objects.append(lbl)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'BoxPlot()'

class SampleSpace(VCollection):
    """Rectangle representing a probability sample space, divisible into regions."""
    def __init__(self, width: float = 500, height: float = 400, x: float = 710, y: float = 340, creation: float = 0, z: float = 0, **styling_kwargs):
        style_kw = {'fill': '#222', 'fill_opacity': 0.5,
                    'stroke': '#fff', 'stroke_width': 2} | styling_kwargs
        self._rect = Rectangle(width=width, height=height, x=x, y=y,
                               creation=creation, z=z, **style_kw)
        self._width, self._height = width, height
        self._x, self._y = x, y
        self._parts = []
        super().__init__(self._rect, creation=creation, z=z)

    def __repr__(self):
        return 'SampleSpace()'

    def _divide(self, horizontal, proportion, colors, labels, creation, z):
        """Shared logic for divide_horizontally / divide_vertically."""
        if horizontal:
            s1, s2 = self._width * proportion, self._width * (1 - proportion)
            r1 = Rectangle(width=s1, height=self._height, x=self._x, y=self._y,
                           fill=colors[0], fill_opacity=0.4, stroke_width=0,
                           creation=creation, z=z + 0.1)
            r2 = Rectangle(width=s2, height=self._height, x=self._x + s1, y=self._y,
                           fill=colors[1], fill_opacity=0.4, stroke_width=0,
                           creation=creation, z=z + 0.1)
        else:
            s1, s2 = self._height * proportion, self._height * (1 - proportion)
            r1 = Rectangle(width=self._width, height=s1, x=self._x, y=self._y,
                           fill=colors[0], fill_opacity=0.4, stroke_width=0,
                           creation=creation, z=z + 0.1)
            r2 = Rectangle(width=self._width, height=s2, x=self._x, y=self._y + s1,
                           fill=colors[1], fill_opacity=0.4, stroke_width=0,
                           creation=creation, z=z + 0.1)
        self.objects.extend([r1, r2])
        self._parts = [r1, r2]
        if labels:
            for rect, label in zip([r1, r2], labels):
                rcx, rcy = rect.center(creation)
                self.objects.append(
                    _label_text(label, rcx, rcy, 24, creation=creation, z=z + 0.2))
        return self

    def divide_horizontally(self, proportion, colors=('#58C4DD', '#FC6255'), labels=None,
                            creation: float = 0, z: float = 0):
        """Split the space horizontally by proportion (0-1). Left gets first color."""
        return self._divide(True, proportion, colors, labels, creation, z)

    def divide_vertically(self, proportion, colors=('#58C4DD', '#FC6255'), labels=None,
                          creation: float = 0, z: float = 0):
        """Split the space vertically by proportion (0-1). Top gets first color."""
        return self._divide(False, proportion, colors, labels, creation, z)

