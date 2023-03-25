"""
Segments are Lines, Arcs, (Quadratic)BezierCurves
These represent the building blocks of shapes/objects like
    Squares, Circles, TexObjects
Segments do not have styling arguments whereas shapes/objects do.
A path is a collection of segments.

Some thoughts about functionalities are based on "SVG-Morpheus"
See: http://alexk111.github.io/SVG-Morpheus/
See: https://github.com/alexk111/SVG-Morpheus
Copyright (c) 2014 Alex Kaul

This was largely based on "svgpathtools"
See: https://github.com/mathandy/svgpathtools
Copyright (c) 2015 Andrew Allan Port
Copyright (c) 2013-2014 Lennart Regebro

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from abc import ABC
import svgpathtools
import numpy as np
import math
### Local imports
import vectormation.style as style
import vectormation.easings as easings

def sigmoid(x):
  return 1 / (1 + math.exp(-x))

def convert_to_bezier(seg, n_curves=10):
    """Convert svgpathtools segment to Bezier Curve, approximate arcs by n_curves splines"""
    if isinstance(seg, svgpathtools.Line):
        return [Line(start=seg.start, end=seg.end).to_bezier()]
    elif isinstance(seg, svgpathtools.CubicBezier):
        return [CubicBezier(start=seg.start, control1=seg.control1, control2=seg.control2, end=seg.end)]
    elif isinstance(seg, svgpathtools.QuadraticBezier):
        return [QuadraticBezier(start=seg.start, control1=seg.control, end=seg.end)]
    elif isinstance(seg, svgpathtools.Arc):
        # We approximate this arc by n_curves cubic splines, luckily, there is a function for this
        return [convert_to_bezier(bez)[0] for bez in seg.as_cubic_curves(n_curves)]

class Arc(svgpathtools.Arc):
    def to_bezier(self):
        # Split the arc into smaller arcs, then look at
        # https://stackoverflow.com/questions/734076/how-to-best-approximate-a-geometrical-arc-with-a-bezier-curve
        # use self.as_cubic_curves()
        raise NotImplementedError

class CubicBezier(svgpathtools.CubicBezier):
    def to_bezier(self):
        return CubicBezier(start=self.start, control1=self.control1, control2=self.control2, end=self.end)

    def bezier_morph(self, other, easing=easings.smooth):
        """Morphs one bezier curve into the other, returns function of curve with 0<=t<=1"""
        assert isinstance(other, CubicBezier)

        # The curve on [0, 1] that determines the move time is the easing
        cur_s = lambda t: self.start + (other.start - self.start) * easing(t)
        cur_c1 = lambda t: self.control1 + (other.control1 - self.control1) * easing(t)
        cur_c2 = lambda t: self.control2 + (other.control2 - self.control2) * easing(t)
        cur_e = lambda t: self.end + (other.end - self.end) * easing(t)

        return lambda t: CubicBezier(cur_s(t), cur_c1(t), cur_c2(t), cur_e(t))


class QuadraticBezier(svgpathtools.QuadraticBezier):
    def to_bezier(self):
        # https://stackoverflow.com/questions/3162645/convert-a-quadratic-bezier-to-a-cubic-one
        return CubicBezier(
            start=self.start,
            control1=self.start + 2/3*(self.control-self.start),
            control2=self.end + 2/3*(self.control-self.end),
            end=self.end
        )

class Line(svgpathtools.Line):
    def to_bezier(self):
        return CubicBezier(start=self.start, control1=self.start, control2=self.end, end=self.end)

class Path(svgpathtools.Path):
    def adjusted_bbox(self, *transforms):
        """Adjust the bbox of this path to the transforms given in svg-format as strings"""
        if transforms == ('',):
            return self.bbox()
        return self.adjusted_path(*transforms).bbox()

    def adjusted_path(self, *transforms):
        """Adjust the path to the transforms given in svg-format as strings"""
        segs = self._segments

        for transform in transforms[::-1]:
            # Parse the transform into the command and the values
            assert '(' in transform and ')' in transform  # Check for validity
            spl = transform.split('(')
            assert len(spl) == 2
            command, vals = spl
            assert vals[-1] == ')'
            vals = vals[:-1]
            # Split at space or ,
            if vals.count(' ') == 0:
                vals = vals.split(',')
            else:
                vals = vals.split(' ')
            # NOTE: There can be some exceptions to the above rule I believe
            # The below code could result in some errors.
            vals = [float(i) for i in vals]  # See above for details

            # Perform the transformation
            if command == 'scale':
                assert 1 <= len(vals) <= 2  # too little or too much arguments for scale
                x = vals[0]
                if len(vals) == 1:
                    # The y-value is equal to the x-value
                    y = x
                else:
                    y = vals[1]

                # We must scale all of the segments by x, y
                # # The center of the scale is at the center of the current bbox
                # xmin, xmax, ymin, ymax = Path(*segs).bbox()
                # center = (xmin+xmax)/2 + (ymin+ymax)/2 * 1j
                segs = Path(*segs).scaled(x, y, origin=0j)._segments
                # segs = [i.scaled(x, y, origin=0+0j) for i in segs]
                # exit()
            elif command == 'translate':
                assert 1 <= len(vals) <= 2  # too little or too much arguments for translate
                x = vals[0]
                if len(vals) == 1: y = 0
                else: y = vals[1]
                segs = [i.translated(x + y*1j) for i in segs]
            else:
                raise NotImplementedError('Transform not yet implemented')
        return Path(*segs)

class Paths:
    """Is a simple collection of Path objects, e.g. forming two Tex letters"""
    def __init__(self, *args):
        self.paths = []
        self.stylings = []
        for arg in args:
            assert isinstance(arg, tuple)
            assert len(arg) == 2
            assert isinstance(arg[0], svgpathtools.Path)
            assert isinstance(arg[1], style.Styling)
            self.paths.append(arg[0])
            self.stylings.append(arg[1])

    def _morph_prepare(self, other, start_time=0, end_time=1, dist_vs_length=True):
        """Returns the segment pairs in Cubic Bezier form that need be merged
        dist_vs_length is if the subpaths closest in distance or closest in length should be matched"""
        assert isinstance(other, Paths)

        ### General idea
        # Image we have two paths, one being the LaTeX % character and the other a circle.
        # The % has one path with multiple closed subpaths whereas the circle has but one.
        # We circumvent this problem by creating new closed/open paths.
        # All closed subpaths from the starting character are mapped to the closed subpaths
        # of the ending characters, if there are more subpaths to begin with, we add
        # subpaths as closed points with as many segments as needed, if there are less
        # subpaths to begin with we create closed points for the ending characters.
        # The same will be done for the open paths.
        # In this manner we select a matching of closed subpaths before and at the end
        # of the morphing.
        # ADDENDUM: We need to add styling arguments to the shapes that are morphing.
        # If we go from one shape to the other we interpolate the styling between both shapes.
        # However, new closed/open paths do not have any styling. We must thus give these
        # the styling from which shape they came or which they become. The styling is constant.

        # First we list all subpaths of both objects
        closed_subpaths_start = []
        open_subpaths_start = []
        # for path, st in zip(self.paths, self.stylings):
        #     for p in path.continuous_subpaths():
        #         p = Path(*p._segments)
        #         if p.isclosed(): closed_subpaths_start.append((p, st))
        #         else: open_subpaths_start.append((p, st))
        for path, st in zip(self.paths, self.stylings):
            # Note that the subpaths must be non-intersecting
            # NOTE: TODO: loop through all non-intersecting continuous subpaths of the path
            # for the start and end figures.
            if path.iscontinuous() and path.isclosed(): closed_subpaths_start.append((path, st))
            else: open_subpaths_start.append((path, st))

        closed_subpaths_end = []
        open_subpaths_end = []
        for path, st in zip(other.paths, other.stylings):
            # for p in path.continuous_subpaths():
            #     p = Path(*p._segments)
            #     if p.isclosed(): closed_subpaths_end.append((p, st))
            #     else: open_subpaths_end.append((p, st))
            if path.iscontinuous() and path.isclosed(): closed_subpaths_end.append((path, st))
            else: open_subpaths_end.append((path, st))

        # Then we match the closest ones with each other
        subpath_matches = []
        for start, end in [(open_subpaths_start, open_subpaths_end), (closed_subpaths_start, closed_subpaths_end)]:
            mat_dist = np.zeros((len(start), len(end)))
            for i, (path, path_style) in enumerate(start):
                if dist_vs_length:
                    transforms = path_style.transform_style(start_time)
                    transforms = transforms[1:].split(' ')
                    xmin, xmax, ymin, ymax = path.adjusted_bbox(*transforms)
                    path_center = ((xmin+xmax)/2, (ymin+ymax)/2)

                for j, (match, match_style) in enumerate(end):
                    if dist_vs_length:
                        # NOTE: TODO: cache these adjusted bbox results.
                        transforms = match_style.transform_style(end_time)
                        transforms = transforms[1:].split(' ')
                        xmin, xmax, ymin, ymax = match.adjusted_bbox(*transforms)
                        match_center = ((xmin+xmax)/2, (ymin+ymax)/2)

                        dist = ((match_center[0]-path_center[0])**2 + (match_center[1]-path_center[1])**2)**(1/2)

                        mat_dist[i,j] = dist
                    else:
                        mat_dist[i,j] = abs(path.length() / match.length() - 1)

            ls, le = len(start), len(end)
            matches = []
            # Pre-compute the largest value in the matrix
            for _ in range(min(ls, le)):
                match_idx = np.unravel_index(np.nanargmin(mat_dist, axis=None), mat_dist.shape)
                # Remove objects from matrix
                # mat_dist = np.delete(mat_dist, match_idx[0], axis=0)
                # mat_dist = np.delete(mat_dist, match_idx[1], axis=1)
                # Set objects in matrix to zero to prevent from making double matches (-1 < min(mat_dist))
                mat_dist[match_idx[0],:] = np.nan
                mat_dist[:,match_idx[1]] = np.nan
                matches.append(match_idx)

            # We now need to add the new subpaths for the matches
            if ls >= le:  # We must create extra open ending points
                for idx in {i for i in range(ls)} - {m[0] for m in matches}:
                    path, path_style = start[idx]
                    subpath_matches.append((start[idx], (Path(), path_style)))  # The same styling
            else:  # We must create extra open starting points
                for idx in {i for i in range(le)} - {m[1] for m in matches}:
                    path, path_style = end[idx]
                    subpath_matches.append(((Path(), path_style), end[idx]))  # The same styling
            # Add all correctly matched pairs
            for i, j in matches:
                subpath_matches.append((start[i], end[j]))

        # Now that all subpaths are matched we match all segments in the subpaths
        subpath_segment_pairs = []
        for (path_from, style_from), (path_to, style_to) in subpath_matches:
            segment_pairs = []
            # We have only implemented the morphing of cubic bezier thus we need to convert
            # all shapes to these (an arc is split into multiple smaller arcs before converting).
            segs_from = []
            for seg in path_from:
                segs_from += convert_to_bezier(seg)
            segs_to = []
            for seg in path_to:
                segs_to += convert_to_bezier(seg)

            lf, lt = len(segs_from), len(segs_to)
            if min(lf, lt) == 0:
                # We have to create this path from nothing
                if lf == 0:
                    xmin, xmax, ymin, ymax = path_to.bbox()
                    center = (xmin+xmax)/2 + (ymin+ymax)/2 * 1j
                    for i in segs_to:
                        segment_pairs.append((Line(start=center, end=center).to_bezier(), i))
                    subpath_segment_pairs.append((segment_pairs, style_from, style_to))
                    continue
                else:
                    xmin, xmax, ymin, ymax = path_from.bbox()
                    center = (xmin+xmax)/2 + (ymin+ymax)/2 * 1j
                    for i in segs_from:
                        segment_pairs.append((i, Line(start=center, end=center).to_bezier()))
                    subpath_segment_pairs.append((segment_pairs, style_from, style_to))
                    continue

            # Split the longest lines in half
            while len(segs_from) < len(segs_to):
                max_idx = max(enumerate(segs_from), key=lambda x: x[1].length())[0]
                new1, new2 = segs_from[max_idx].split(0.5)
                new1, new2 = convert_to_bezier(new1), convert_to_bezier(new2)
                segs_from = segs_from[:max_idx] + new1 + new2 + segs_from[max_idx+1:]
            # Split the longest lines in half
            while len(segs_to) < len(segs_from):
                max_idx = max(enumerate(segs_to), key=lambda x: x[1].length())[0]
                new1, new2 = segs_to[max_idx].split(0.5)
                new1, new2 = convert_to_bezier(new1), convert_to_bezier(new2)
                segs_to = segs_to[:max_idx] + new1 + new2 + segs_to[max_idx+1:]

            segment_pairs += list(zip(segs_from, segs_to))
            subpath_segment_pairs.append((segment_pairs, style_from, style_to))

        # Save all information
        self.subpath_segment_pairs = subpath_segment_pairs

        return subpath_segment_pairs


    def morph(self, other, start_time=0, end_time=1, easing=easings.smooth):
        # Store the morph prepare output (by id of other) so processing only happens once
        if hasattr(self, 'segment_pairs'):
            subpath_segment_pairs = self.subpath_segment_pairs
        else:
            subpath_segment_pairs = self._morph_prepare(other, start_time, end_time, dist_vs_length=True)

        objects = []
        for segment_pairs, style_from, style_to in subpath_segment_pairs:
            path = []
            for f, t in segment_pairs:
                seg_func = f.bezier_morph(t, easing=easing)
                path.append(seg_func)

            # Define the subpath we need to draw as a function of time (with 0<=t<=1)
            def f(path):  # We need to avoid a direct lambda function because of locality of path
                return lambda t: Path(*[s(t) for s in path]).d()
            object = (f(path), style_from, style_to)
            # The object has styling style_from and style_to, we need to interpolate
            # these style objects and add the interpolation to the path data
            # This is done in the __init__ of the Morph class
            objects.append(object)

        return objects



if __name__ == '__main__':
    # p1 = svgpathtools.Path('M0,1 L100,200 L400,200 Z')
    # p2 = svgpathtools.Path('M1000,1 L200,200 L900,500 Z')
    p1 = svgpathtools.Path('M0,1 L100,200 L400,200 Z')
    # p2 = svgpathtools.Path('M0,2 L300,300 C100,200 110,210 340,230 A100,200 200,300 300,400 400')
    p2 = svgpathtools.Path('M0,2 L300,300 C100,200 110,210 340,230')
    p3 = svgpathtools.Path('M0,1 L100,200 L400,200 Z M0,2 L100,200 L400,200 Z M0,3 L20,30 M0,4 L40,50')
    # p1.morph(p2)

    f = Paths(p1, p2).morph(Paths(p3))
    print(f(0))
    # TODO: add close parameter Z to svg path
    # TODO: add morphobject in script
    # TODO: add rotation (360 degrees) as transform to that morphobject
    # TODO: Return as same collection of subpaths for rotation?
