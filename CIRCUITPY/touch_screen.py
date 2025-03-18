from adafruit_simplemath import map_range
from filters import XYSampleFilter
from user.config import CONFIG

##############################
# Touch screen state
##############################
TOUCH_STATE_IDLE = 0
TOUCH_STATE_START = 1
TOUCH_STATE_PRESS = 2

##############################
# TouchScreen class
##############################
class TouchScreen:
    def __init__(
        self, 
        is_touched_fn,
        read_data_fn,
        display_width, 
        display_height
    ):
        self._is_touched_fn = is_touched_fn
        self._read_data_fn = read_data_fn
        self._display_width = display_width
        self._display_height = display_height
        self._filter = XYSampleFilter(6, 10)
        self._touch_state = TOUCH_STATE_IDLE

        self._last_sample = None
        self._touch_delta = (0, 0)

    @property
    def touched(self):
        return self._touch_state == TOUCH_STATE_PRESS

    @property
    def touch_moved(self):
        return self._touch_delta != (0, 0)

    @property 
    def touch_delta(self):
        return self._touch_delta

    @property
    def touch_point(self):
        return self._last_sample

    def update(self):
        self._touch_delta = (0, 0)

        if self._is_touched_fn():
            y_sample, x_sample, _ = self._read_data_fn()

            x_sample = map_range(x_sample, CONFIG.touch_calibration.min_x, CONFIG.touch_calibration.max_x, 0, self._display_width)

            # invert Y axis if necessary
            if CONFIG.touch_calibration.invert_y:
                y_sample = map_range(y_sample, CONFIG.touch_calibration.min_y, CONFIG.touch_calibration.max_y, self._display_height, 0)
            else:
                y_sample = map_range(y_sample, CONFIG.touch_calibration.min_y, CONFIG.touch_calibration.max_y, 0, self._display_height)

            # The very first reading can be very erratic, so throw it away.
            if self._touch_state == TOUCH_STATE_IDLE:
                self._touch_state = TOUCH_STATE_START
                self._last_sample = None

            # Now we'll start reading samples. Reset the filter and get the first one.
            elif self._touch_state == TOUCH_STATE_START:
                self._touch_state = TOUCH_STATE_PRESS
                self._last_sample = self._filter(x_sample, y_sample, reset=True)

            # Continue reading and filtering samples until the screen isn't touched anymore.
            elif self._touch_state == TOUCH_STATE_PRESS:
                x_filtered, y_filtered = self._filter(x_sample, y_sample, reset=False)
                x_last, y_last = self._last_sample

                x_diff = int(x_filtered - x_last)
                y_diff = int(y_filtered - y_last)

                self._last_sample = (x_filtered, y_filtered)
                self._touch_delta = (x_diff, y_diff)
        else:
            self._touch_state = TOUCH_STATE_IDLE
            self._last_sample = None
