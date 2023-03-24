"""
NOTE: The color names to hex are copied from the color sheets from manim

MIT License

Copyright (c) 2018 3Blue1Brown LLC
Copyright (c) 2021, the Manim Community Developers

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

colors = {
    'WHITE': '#FFFFFF',
    'GRAY_A': '#DDDDDD',
    'GREY_A': '#DDDDDD',
    'GRAY_B': '#BBBBBB',
    'GREY_B': '#BBBBBB',
    'GRAY_C': '#888888',
    'GREY_C': '#888888',
    'GRAY_D': '#444444',
    'GREY_D': '#444444',
    'GRAY_E': '#222222',
    'GREY_E': '#222222',
    'BLACK': '#000000',
    'LIGHTER_GRAY': '#DDDDDD',
    'LIGHTER_GREY': '#DDDDDD',
    'LIGHT_GRAY': '#BBBBBB',
    'LIGHT_GREY': '#BBBBBB',
    'GRAY': '#888888',
    'GREY': '#888888',
    'DARK_GRAY': '#444444',
    'DARK_GREY': '#444444',
    'DARKER_GRAY': '#222222',
    'DARKER_GREY': '#222222',
    'BLUE_A': '#C7E9F1',
    'BLUE_B': '#9CDCEB',
    'BLUE_C': '#58C4DD',
    'BLUE_D': '#29ABCA',
    'BLUE_E': '#236B8E',
    'PURE_BLUE': '#0000FF',
    'BLUE': '#58C4DD',
    'DARK_BLUE': '#236B8E',
    'TEAL_A': '#ACEAD7',
    'TEAL_B': '#76DDC0',
    'TEAL_C': '#5CD0B3',
    'TEAL_D': '#55C1A7',
    'TEAL_E': '#49A88F',
    'TEAL': '#5CD0B3',
    'GREEN_A': '#C9E2AE',
    'GREEN_B': '#A6CF8C',
    'GREEN_C': '#83C167',
    'GREEN_D': '#77B05D',
    'GREEN_E': '#699C52',
    'PURE_GREEN': '#00FF00',
    'GREEN': '#83C167',
    'YELLOW_A': '#FFF1B6',
    'YELLOW_B': '#FFEA94',
    'YELLOW_C': '#FFFF00',
    'YELLOW_D': '#F4D345',
    'YELLOW_E': '#E8C11C',
    'YELLOW': '#FFFF00',
    'GOLD_A': '#F7C797',
    'GOLD_B': '#F9B775',
    'GOLD_C': '#F0AC5F',
    'GOLD_D': '#E1A158',
    'GOLD_E': '#C78D46',
    'GOLD': '#F0AC5F',
    'RED_A': '#F7A1A3',
    'RED_B': '#FF8080',
    'RED_C': '#FC6255',
    'RED_D': '#E65A4C',
    'RED_E': '#CF5044',
    'PURE_RED': '#FF0000',
    'RED': '#FC6255',
    'MAROON_A': '#ECABC1',
    'MAROON_B': '#EC92AB',
    'MAROON_C': '#C55F73',
    'MAROON_D': '#A24D61',
    'MAROON_E': '#94424F',
    'MAROON': '#C55F73',
    'PURPLE_A': '#CAA3E8',
    'PURPLE_B': '#B189C6',
    'PURPLE_C': '#9A72AC',
    'PURPLE_D': '#715582',
    'PURPLE_E': '#644172',
    'PURPLE': '#9A72AC',
    'PINK': '#D147BD',
    'LIGHT_PINK': '#DC75CD',
    'ORANGE': '#FF862F',
    'LIGHT_BROWN': '#CD853F',
    'DARK_BROWN': '#8B4513',
    'GRAY_BROWN': '#736357',
    'GREY_BROWN': '#736357'
}


class LinearGradient:
    def __init__(self):
        # Multiple types, linear, etc, this must be defined in the preamble/defs region of the svg
        # Hence this must be an object that must be added to the canvas (automatically added maybe)

        # NOTE: SEE: https://www.w3schools.com/graphics/svg_grad_linear.asp

        print('hi')
        print(canvas)
        raise NotImplementedError

    def to_svg(self, time):
        raise NotImplementedError


class RadialGradient:
    def __init__(self):
        # Multiple types, linear, etc, this must be defined in the preamble/defs region of the svg
        # Hence this must be an object that must be added to the canvas (automatically added maybe)
        raise NotImplementedError

    def to_svg(self, time):
        raise NotImplementedError


def color_from_name(name):
    if name not in colors:
        raise ValueError(f'Color {name} is unknown')

    return colors[name]
