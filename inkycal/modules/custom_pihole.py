"""PIHOLE Module"""
import abc

from inkycal.custom import *
from inkycal.custom.functions import internet_available
from inkycal.custom.inkycal_exceptions import NetworkNotReachableError

import arrow
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

class PiHole(metaclass=abc.ABCMeta):
    """Generic base class for inkycal modules"""

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'generate_image') and
                callable(subclass.generate_image) or
                NotImplemented)

    def __init__(self, config):
        """Initialize module with given config"""

        # Initializes base module
        # sets properties shared amongst all sections
        self.config = conf = config['config']
        self.width, self.height = conf['size']

        self.padding_left = self.padding_right = conf["padding_x"]
        self.padding_top = self.padding_bottom = conf['padding_y']

        self.fontsize = conf["fontsize"]
        self.font = ImageFont.truetype(
            fonts['NotoSansUI-Regular'], size=self.fontsize)

    def set(self, help=False, **kwargs):
        """Set attributes of class, e.g. class.set(key=value)
        see that can be changed by setting help to True
        """
        lst = dir(self).copy()
        options = [_ for _ in lst if not _.startswith('_')]
        if 'logger' in options: options.remove('logger')

        if help == True:
            print('The following can be configured:')
            print(options)

        for key, value in kwargs.items():
            if key in options:
                if key == 'fontsize':
                    self.font = ImageFont.truetype(self.font.path, value)
                    self.fontsize = value
                else:
                    setattr(self, key, value)
                    print(f"set '{key}' to '{value}'")
            else:
                print(f'{key} does not exist')
                pass

        # Check if validation has been implemented
        try:
            self._validate()
        except AttributeError:
            print('no validation implemented')

    @abc.abstractmethod
    def generate_image(self):

        # Define new image size with respect to padding
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))
        im_size = im_width, im_height
        logger.debug(f'Image size: {im_size}')

        # Create an image for black pixels and one for coloured pixels
        im_black = Image.new('RGB', size=im_size, color='white')
        im_colour = Image.new('RGB', size=im_size, color='white')

        # Calculate size rows and columns
        col_width = im_width // 4 # Four columns
        row_height = im_height // 2 # Two rows

        logger.debug(f"row_height: {row_height} | col_width: {col_width}")

        spacing_top = int((im_width % col_width) / 2)
        spacing_left = int((im_height % row_height) / 2)

        # Calculate the x-axis position of each col
        col1 = spacing_top
        col2 = col1 + col_width
        col3 = col2 + col_width
        col4 = col3 + col_width

        line_gap = int((im_height - spacing_top - 3 * row_height) // 4)

        row1 = line_gap
        row2 = row1 + line_gap + row_height

        box_size = (col_width, row_height)

        # Position for Total
        tot_text_pos = (col1, row1)
        tot_value_pos = (col1, row2)

        # Position for Blocked
        blocked_text_pos = (col2, row1)
        blocked_value_pos = (col2, row2)

        # Position for Percent
        percent_text_pos = (col3, row1)
        percent_value_pos = (col3, row2)

        # Position for Unique domains
        unique_text_pos = (col4, row1)
        unique_value_pos = (col4, row2)

        write(im_colour, tot_text_pos, box_size, "TESTCOL1ROW1", font=self.font)
        write(im_colour, blocked_text_pos, box_size, "TESTCOL2ROW1", font=self.font)
        write(im_colour, percent_text_pos, box_size, "TESTCOL3ROW1", font=self.font)
        write(im_colour, unique_text_pos, box_size, "TESTCOL4ROW1", font=self.font)
        write(im_colour, tot_value_pos, box_size, "TESTCOL1ROW2", font=self.font)
        write(im_colour, unique_value_pos, box_size, "TESTCOL4ROW2", font=self.font)

        # return the images ready for the display
        return im_black, im_colour

    @classmethod
    def get_config(cls):
        # Do not change
        # Get the config of this module for the web-ui
        try:

            if hasattr(cls, 'requires'):
                for each in cls.requires:
                    if not "label" in cls.requires[each]:
                        raise Exception(f"no label found for {each}")

            if hasattr(cls, 'optional'):
                for each in cls.optional:
                    if not "label" in cls.optional[each]:
                        raise Exception(f"no label found for {each}")

            conf = {
                "name": cls.__name__,
                "name_str": cls.name,
                "requires": cls.requires if hasattr(cls, 'requires') else {},
                "optional": cls.optional if hasattr(cls, 'optional') else {},
            }
            return conf
        except:
            raise Exception(
                'Ohoh, something went wrong while trying to get the config of this module')
