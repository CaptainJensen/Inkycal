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

def get_piHole_stats_data(url):

    if internet_available():
        logger.debug('Connection test passed')
    else:
        logger.error("Network not reachable. Please check your connection.")
        raise NetworkNotReachableError

    logger.info(f'getting PiHole stats...')
    # Get stats from URL
    piholeStats_data = get_json_from_url(url)
    logger.info(f'acquired PiHole stats')

    return piholeStats_data

class PiHole(inkycal_module):
    """Generic base class for inkycal modules"""

    def __init__(self, config):
        """Initialize module with given config"""

        super().__init__(config)

        # Initializes base module
        # sets properties shared amongst all sections
        self.config = conf = config['config']
        self.width, self.height = conf['size']
        self.url_pihole = conf['url']

        self.padding_left = self.padding_right = conf["padding_x"]
        self.padding_top = self.padding_bottom = conf['padding_y']

        self.fontsize = conf["fontsize"]
        self.font = ImageFont.truetype(fonts['NotoSansUI-Regular'], size=self.fontsize)
        self.icon_font = ImageFont.truetype(fonts['MaterialIcons'], size=self.fontsize)

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
        col_width = im_width // 2 # Two columns
        row_height = im_height // 4 # Four rows

        logger.debug(f"row_height: {row_height} | col_width: {col_width}")

        spacing_top = int((im_width % col_width) / 2)
        spacing_left = int((im_height % row_height) / 2)

        # Calculate the x-axis position of each col
        col1 = spacing_top
        col2 = col1 + col_width

        line_gap = int((im_height - spacing_top - 3 * row_height) // 4)

        # Calculate the position of each row
        row1 = line_gap
        row2 = row1 + line_gap + row_height
        row3 = row2 + line_gap + row_height
        row4 = row3 + line_gap + row_height

        box_size = (col_width, row_height)

        # Define sizes for icons
        icon_small = int(col_width / 3)

        # Position for Total
        tot_text_pos = (col1 + icon_small, row1)
        tot_icon_pos = (col1, row1)
        tot_value_pos = (col1, row2)

        # Position for Blocked
        blocked_text_pos = (col2 + icon_small, row1)
        blocked_icon_pos = (col2, row1)
        blocked_value_pos = (col2, row2)

        # Position for Percent
        percent_text_pos = (col1 + icon_small, row3)
        percent_icon_pos = (col1, row3)
        percent_value_pos = (col1, row4)

        # Position for Unique domains
        unique_text_pos = (col2 + icon_small, row3)
        unique_icon_pos = (col2, row3)
        unique_value_pos = (col2, row4)

        piholeStats_data = get_piHole_stats_data(self.url_pihole)

        # Parse stats
        total_value = piholeStats_data["queries"]["total"]
        blocked_value = piholeStats_data["queries"]["blocked"]
        percent_value = piholeStats_data["queries"]["percent_blocked"]
        unique_value = piholeStats_data["queries"]["unique_domains"]

        # Draw Total queries box
        write(im_colour, tot_text_pos, box_size, "Queries", font=self.font, alignment="right")
        write(im_colour, tot_icon_pos, box_size, "\ue80b", self.icon_font, alignment="left", autofit=True)
        write(im_black, tot_value_pos, box_size, f'{total_value:,}', font=self.font)

        # Draw total blocked box
        write(im_colour, blocked_text_pos, box_size, "Blocked", font=self.font, alignment="right")
        write(im_colour, blocked_icon_pos, box_size, "\ue764", self.icon_font, alignment="left", autofit=True)
        write(im_black, blocked_value_pos, box_size, f'{blocked_value:,}', font=self.font)

        # Draw percent blocked box
        write(im_colour, percent_text_pos, box_size, "Blocked", font=self.font, alignment="right")
        write(im_colour, percent_icon_pos, box_size, "\ue6c4", self.icon_font, alignment="left", autofit=True)
        write(im_black, percent_value_pos, box_size, f'{round(percent_value, 2)}%', font=self.font)

        # Draw unique domains box
        write(im_colour, unique_text_pos, box_size,"Domains", font=self.font, alignment="right")
        write(im_colour, unique_icon_pos, box_size, "\ue896", self.icon_font, alignment="left", autofit=True)
        write(im_black, unique_value_pos, box_size, f'{unique_value:,}', font=self.font)

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
