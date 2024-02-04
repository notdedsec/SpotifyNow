from colour import Color

from app.imager.styles import *
from app.imager.styles.base import Style

styles = {x.__name__:x for x in Style.__subclasses__()}

colors = {
    'Auto': Color('#1ed760'), # TODO handle this in the style
    'Classic': Color('#1ed760'),
    'Red': Color('red'),
    'Blue': Color('blue'),
}

accents = colors


def get_styles():
    styles = 'generate an image of all the supported style/layouts'
    caption = 'Modern is the new default. Classic was the old style. Try out other styles to find what fits you best!'
    ...

def get_colors():
    colors = 'generate an image of all the supported colors' # auto icon: rainbow
    caption = 'When set to Auto, it takes the most dominant color from the cover artwork.'
    ...

def get_accents():
    accents = get_colors()  # auto icon: b|w
    caption = 'When set to Auto, it uses a brighter or darker version of the primary color.'
    ...

