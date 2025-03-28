from math import pow
from adafruit_simplemath import constrain, map_range
from user.config import CONFIG

# Default brightness values for backlight LEDs
INDEX_COUNT = 10
DEFAULT_INDEX = INDEX_COUNT // 2
MIN_INDEX = 0
MAX_INDEX = INDEX_COUNT - 1

NEOPIXEL_MIN_BRIGHTNESS = 0.01172
NEOPIXEL_MAX_BRIGHTNESS = constrain(CONFIG.neopixel_max_brightness, NEOPIXEL_MIN_BRIGHTNESS, 1.0)

def gamma(value, gamma=1.6):
	return pow(value, gamma)

def get_display_brightness(index):
	b = gamma(index / MAX_INDEX)
	return constrain(b, 0.01, 1.0)

def get_keyboard_brightness(index):
	b = gamma(index / MAX_INDEX * 0.25)
	return constrain(b, 0.005, 1.0)

def get_neopixel_brightness(index):
	# No need to gamma correct at such low brightness values
	b = index / MAX_INDEX
	return map_range(b, 0.0, 1.0, NEOPIXEL_MIN_BRIGHTNESS, NEOPIXEL_MAX_BRIGHTNESS)

DEFAULT_DISPLAY = get_display_brightness(DEFAULT_INDEX)
DEFAULT_KEYBOARD = get_keyboard_brightness(DEFAULT_INDEX)
DEFAULT_NEOPIXEL = get_neopixel_brightness(DEFAULT_INDEX)