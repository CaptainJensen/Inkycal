"""PIHOLE Module"""
from inkycal.custom import *
from inkycal.custom.functions import internet_available
from inkycal.custom.inkycal_exceptions import NetworkNotReachableError
from inkycal.modules.template import inkycal_module

import json
import requests

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

logger = logging.getLogger(__name__)

def get_json_from_url(request_url):
    response = requests.get(request_url, verify=False)
    if not response.ok:
        raise AssertionError(
            f"Failure getting the current weather: code {response.status_code}. Reason: {response.text}"
        )
    return json.loads(response.text)

class PiHole(inkycal_module):
    """Generic base class for inkycal modules"""

    def __init__(self, config):
        """Initialize module with given config"""

        super().__init__(config)

        # Initializes base module
        # sets properties shared amongst all sections
        self.config = conf = config['config']
        self.width, self.height = conf['size']

        self.padding_left = self.padding_right = conf["padding_x"]
        self.padding_top = self.padding_bottom = conf['padding_y']

        self.fontsize = conf["fontsize"]
        self.font = ImageFont.truetype(
            fonts['NotoSansUI-Regular'], size=self.fontsize)

        # give an OK message
        logger.debug(f'Custom PIHOLE module loaded')

    def generate_image(self):

        logger.info(f'generating PiHole image...')

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

        if internet_available():
            logger.debug('Connection test passed')
        else:
            logger.error("Network not reachable. Please check your connection.")
            raise NetworkNotReachableError

        logger.info(f'getting PiHole stats...')
        # Get stats from URL
        piholeStats_data = get_json_from_url("https://pi.hole:443/api/stats/summary")

        # Parse stats
        total_value = piholeStats_data["queries"]["total"]
        blocked_value = piholeStats_data["queries"]["blocked"]
        percent_value = piholeStats_data["queries"]["percent_blocked"]
        unique_value = piholeStats_data["queries"]["unique_domains"]

        logger.info(f'acquired PiHole stats')

        write(im_colour, tot_text_pos, box_size, "Total Queries", font=self.font)
        write(im_black, tot_value_pos, box_size, str(total_value), font=self.font)

        write(im_colour, blocked_text_pos, box_size, "Total Blocked", font=self.font)
        write(im_black, blocked_value_pos, box_size, str(blocked_value), font=self.font)

        write(im_colour, percent_text_pos, box_size, "Percent Blocked", font=self.font)
        write(im_black, percent_value_pos, box_size, str(round(percent_value, 2)) + "%", font=self.font)

        write(im_colour, unique_text_pos, box_size, "Unique Domains", font=self.font)
        write(im_black, unique_value_pos, box_size, str(unique_value), font=self.font)

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
