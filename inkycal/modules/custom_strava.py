"""PIHOLE Module"""
from inkycal.custom import *
from inkycal.modules.template import inkycal_module

from stravalib.client import Client
from stravalib import unit_helper
from stravalib import model

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

        self.initial_access_token = conf["initial_access_token"]
        self.initial_refresh_token = conf["initial_refresh_token"]
        self.client_id = conf["client_id"]
        self.client_secret = conf["client_secret"]
        self.strava_client = Client(access_token=self.initial_access_token, refresh_token=self.initial_refresh_token)

        logger.info(f'Custom Strava module loaded')

    def generate_image(self):

        logger.info(f'Generating strava image...')

        try:
            logger.info(f'Attempting to refresh Strava token...')

            self.strava_client.refresh_access_token(self.client_id, self.client_secret, self.strava_client.refresh_token)

            athlete = self.strava_client.get_athlete()
            stats = self.strava_client.get_athlete_stats()

            logger.info(f'Connected to athlete: {athlete.firstname} {athlete.lastname}')
        except:
            stats = model.AthleteStats()
            logger.critical('Could not connect to strava!')

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
        dist_text_pos = (col1, row1)
        dist_icon_pos = (col1, row1)
        dist_value_pos = (col1, row2)

        # Position for top right
        count_text_pos = (col2, row1)
        count_icon_pos = (col2, row1)
        count_value_pos = (col2, row2)

        # Position for bottom left
        achievement_text_pos = (col2, row3)
        achievement_icon_pos = (col2, row3)
        achievement_value_pos = (col2, row4)

        # Position for bottom right
        time_text_pos = (col1, row3)
        time_icon_pos = (col1, row3)
        time_value_pos = (col1, row4)

        # Parse stats

        ytd_distance =  stats.ytd_ride_totals.distance
        ytd_count =  stats.ytd_ride_totals.count
        all_achievement_count =  stats.all_ride_totals.achievement_count
        ytd_time =  stats.ytd_ride_totals.elapsed_time

        # Adjust units
        ytd_distance = unit_helper.mile(ytd_distance)
        ytd_time = unit_helper.hours(ytd_time)

        logger.info(f"ytd_distance : {ytd_distance}")
        logger.info(f"ytd_count : {ytd_count}")
        logger.info(f"all_achievement_count : {all_achievement_count}")
        logger.info(f"ytd_time : {ytd_time}")

        # Draw distance box
        write(im_colour, dist_text_pos, box_size, "Distance", font=self.font)
        write(im_colour, dist_icon_pos, box_size, "\ue80b", self.icon_font, alignment="left", autofit=True)
        write(im_black, dist_value_pos, box_size, f'{ytd_distance or -1:,.1f}', font=self.font, autofit=True)

        # Draw total count box
        write(im_colour, count_text_pos, box_size, "Rides", font=self.font)
        write(im_colour, count_icon_pos, box_size, "\ue764", self.icon_font, alignment="left", autofit=True)
        write(im_black, count_value_pos, box_size, f'{ytd_count or -1:,}', font=self.font, autofit=True)

        # Draw achievements box
        write(im_colour, achievement_text_pos, box_size, "Achievements", font=self.font)
        write(im_colour, achievement_icon_pos, box_size, "\ue6c4", self.icon_font, alignment="left", autofit=True)
        write(im_black, achievement_value_pos, box_size, f'{all_achievement_count or -1:,}', font=self.font, autofit=True)

        # Draw time box
        write(im_colour, time_text_pos, box_size,"Time", font=self.font)
        write(im_colour, time_icon_pos, box_size, "\ue896", self.icon_font, alignment="left", autofit=True)
        write(im_black, time_value_pos, box_size, f'{ytd_time or -1:,.1f}', font=self.font, autofit=True)

        # return the images ready for the display
        logger.info("Done generating Strava image")
        return im_black, im_colour