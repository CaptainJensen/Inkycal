"""PIHOLE Module"""
from inkycal.custom import *
from inkycal.modules.template import inkycal_module

from stravalib.client import Client
from stravalib.unithelper import UnitsQuantity

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

logger = logging.getLogger(__name__)

class Strava(inkycal_module):
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
        self.font = ImageFont.truetype(fonts['NotoSansUI-Regular'], size=self.fontsize)
        self.icon_font = ImageFont.truetype(fonts['MaterialIcons'], size=self.fontsize)

        self.initial_token = conf["initial_token"]
        self.strava_client = Client(self.initial_token)

        logger.debug(f'Custom Strava module loaded')

    def generate_image(self):

        logger.info(f'Generating strava image...')

        athlete = self.strava_client.get_athlete()
        stats = self.strava_client.get_athlete_stats()

        logger.debug(f'Connected to athlete: {athlete.firstname} {athlete.lastname}')

        # Define new image size with respect to padding
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))
        im_size = im_width, im_height
        logger.debug(f'Image size: {im_size}')

        # Create an image for black pixels and one for coloured pixels
        im_black = Image.new('RGB', size=im_size, color='white')
        im_colour = Image.new('RGB', size=im_size, color='white')

        # Define n rows and cols
        n_cols = 2
        n_rows = 4

        logger.debug(f"n_cols: {n_cols} | n_rows: {n_rows}")

        # Calculate size rows and columns
        col_width = im_width // n_cols
        row_height = im_height // n_rows

        logger.debug(f"row_height: {row_height} | col_width: {col_width}")

        spacing_top = int((im_width % col_width) / 2)

        # Calculate the x-axis position of each col
        col1 = spacing_top
        col2 = col1 + col_width

        line_gap = int((im_height - spacing_top - (n_rows * row_height)) // (n_rows + 1))

        # Calculate the position of each row
        row1 = line_gap
        row2 = row1 + line_gap + row_height
        row3 = row2 + line_gap + row_height
        row4 = row3 + line_gap + row_height

        box_size = (col_width, row_height)

        # Position for top left
        tot_text_pos = (col1, row1)
        tot_icon_pos = (col1, row1)
        tot_value_pos = (col1, row2)

        # Position for top right
        blocked_text_pos = (col2, row1)
        blocked_icon_pos = (col2, row1)
        blocked_value_pos = (col2, row2)

        # Position for bottom left
        percent_text_pos = (col2, row3)
        percent_icon_pos = (col2, row3)
        percent_value_pos = (col2, row4)

        # Position for bottom right
        unique_text_pos = (col1, row3)
        unique_icon_pos = (col1, row3)
        unique_value_pos = (col1, row4)

        # Parse stats
        ytd_distance =  stats.ytd_ride_totals.distance
        ytd_count =  stats.ytd_ride_totals.count
        ytd_achievement_count =  stats.ytd_ride_totals.achievement_count
        ytd_time =  stats.ytd_ride_totals.elapsed_time

        # Draw distance box
        write(im_colour, tot_text_pos, box_size, "Distance", font=self.font)
        write(im_colour, tot_icon_pos, box_size, "\ue80b", self.icon_font, alignment="left", autofit=True)
        write(im_black, tot_value_pos, box_size, f'{ytd_distance:,}', font=self.font, autofit=True)

        # Draw total count box
        write(im_colour, blocked_text_pos, box_size, "Rides", font=self.font)
        write(im_colour, blocked_icon_pos, box_size, "\ue764", self.icon_font, alignment="left", autofit=True)
        write(im_black, blocked_value_pos, box_size, f'{ytd_count:,}', font=self.font, autofit=True)

        # Draw achievements box
        write(im_colour, percent_text_pos, box_size, "Achievements", font=self.font)
        write(im_colour, percent_icon_pos, box_size, "\ue6c4", self.icon_font, alignment="left", autofit=True)
        write(im_black, percent_value_pos, box_size, f'{round(ytd_achievement_count, 2)}%', font=self.font, autofit=True)

        # Draw time box
        write(im_colour, unique_text_pos, box_size,"Time", font=self.font)
        write(im_colour, unique_icon_pos, box_size, "\ue896", self.icon_font, alignment="left", autofit=True)
        write(im_black, unique_value_pos, box_size, f'{ytd_time:,}', font=self.font, autofit=True)

        # return the images ready for the display
        return im_black, im_colour