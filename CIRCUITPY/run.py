# Import the bare minimum to get started.
# We'll import everything else as we need it so we can prioritize
# getting something on the screen ASAP, as it can take 7-10 seconds
# to import and initialize everything.
import board
import time

##############################
# I2C
############################## 
import busio

# Speed up the I2C port instead of using default board.I2C(), 
# for slightly faster touch screen communication.
i2c = busio.I2C(board.SCL, board.SDA, frequency=400_000)


##############################
# BBQ10 Keyboard
##############################
from bbq10keyboard import BBQ10Keyboard
import function_key
import brightness

# The keyboard
keyboard = BBQ10Keyboard(i2c)

# Sleep for a bit because sometimes the keyboard throws if we start referencing it immediately
time.sleep(0.1)

# Set keyboard backlight brightness to default value
keyboard.keyboard_backlight = brightness.DEFAULT_KEYBOARD

# Turn off display backlight while we set everything up.
# This helps hide display startup artifacts as well as lets
# us know when our program has control.
keyboard.display_backlight = 0.0


#################################
# Front-facing Neopixel
#################################
from neopixel import NeoPixel
neopixel = NeoPixel(board.D11, 1)

# Sometimes the NeoPixel starts up with random values, so make sure it's turned off.
neopixel.fill(0)


##############################
# SPI
############################## 
# IMPORTANT: Allocate but don't use SPIM3. SPIM3 doesn't work when not powered by USB.
# Reference: https://learn.adafruit.com/introducing-the-adafruit-nrf52840-feather/caution-using-spi-on-battery-power
do_not_use_this_spi = busio.SPI(clock=board.A0, MOSI=board.A1)

# Our main SPI should use one fo the low-speed peripehrals so it will work on battery power.
spi = board.SPI()

# Should be 8000000
print("SPI frequency:", spi.frequency)


##############################
# Display
##############################
from adafruit_ili9341 import ILI9341
from adafruit_display_text import label
import displayio

# Release any resources currently in use for the displays
displayio.release_displays()

# Create the display bus and display
display_bus = displayio.FourWire(spi, command=board.D10, chip_select=board.D9)
display = ILI9341(display_bus, width=320, height=240)

# Display controller
from display_controller import DisplayController
display_controller = DisplayController(display=display)


##############################
# Show loading label
##############################
loading_label = display_controller.add_label(
    to_group=display_controller.root_group,
    text="Loading...",
    x = display.width // 2,
    y = display.height // 2,
    color=0xFFFFFF,
    scale = 2
)

# Turn on display backlight at default brightness
keyboard.display_backlight = brightness.DEFAULT_DISPLAY


##############################
# SD Card/File system
##############################
import digitalio
import sdcardio
import storage
import os

sd_detect = keyboard.get_pin(1)
sd_detect.switch_to_input(pull=digitalio.Pull.UP)

sd_card_detected = not sd_detect.value

if sd_card_detected:
    try:
        sdcard = sdcardio.SDCard(spi, board.D5)
        vfs = storage.VfsFat(sdcard)
        storage.mount(vfs, '/sd')
    except:
        sd_card_detected = False

# Turn neopixel back off in case it was turned on for activity select indication
neopixel.fill(0)


##############################
# Load configuration
##############################
from collections import namedtuple
import struct
from user import colors
from user.activities import ACTIVITIES

# Simple type representing our config data structure
Config = namedtuple('Config', [
    'activity_index', 
    'color_index',
    'brightness_index'
])

# Our config info is saved here
CONFIG_FILE = 'sd/config.dat'

# Handy in case we need to delete it for some reason
# try:
#     os.remove(CONFIG_FILE)
# except:
#     pass

# Load config from SD card into current config
def load_config():
    global sd_card_detected

    if sd_card_detected:
        try:
            with open(CONFIG_FILE, 'rb') as f:
                packed = f.read(3)
                unpacked = struct.unpack('BBB', packed)

                config = Config(
                    activity_index=min(unpacked[0], len(ACTIVITIES) - 1),
                    color_index=min(unpacked[1], len(colors.ALL) - 1),
                    brightness_index=min(unpacked[2], brightness.MAX_INDEX)
                )

                print(f"Loaded {config}")
                return config

        except Exception as e:
            print("Error loading config:", e)

    return Config(activity_index=0, color_index=0, brightness_index=brightness.DEFAULT_INDEX)

# Save current config to SD card
def save_config(activity_index, color_index, brightness_index):
    global sd_card_detected

    if sd_card_detected:
        try:
            with open(CONFIG_FILE, 'wb') as f:
                packed = struct.pack('BBB', activity_index, color_index, brightness_index)
                f.write(packed)
                print("Saved config")
        except Exception as e:
            print("Failed to save config:", e)

# Attempt to load the last saved configuration from the SD card.
loaded_config = load_config()

# Set the UI color for the display controller
display_controller.color_index = loaded_config.color_index
loading_label.color = display_controller.foreground_color

# Update the display, keyboard, and neopixel brightness.
# When we create the Device object we'll hand over the brightness duties,
# but since we haven't made the Device yet we'll update the hardware directly now.
keyboard.display_backlight = brightness.get_display_brightness(loaded_config.brightness_index)
keyboard.keyboard_backlight = brightness.get_keyboard_brightness(loaded_config.brightness_index)
neopixel.brightness = brightness.get_neopixel_brightness(loaded_config.brightness_index)


##############################
# Touch screen
##############################
# First try TSC2004 from Rev2
try:
    from tsc2004 import TSC2004
    touch_input = TSC2004(i2c)

    def is_touched_fn():
         return touch_input.touched
except:
    # If not found, try Rev1 STMPE610
    try:
        from adafruit_stmpe610 import Adafruit_STMPE610_SPI
        touch_input = Adafruit_STMPE610_SPI(spi, digitalio.DigitalInOut(board.D6))

        def is_touched_fn(): 
            return not touch_input.buffer_empty
    except:
        raise Exception("Touch screen input device not found")

# Create touch screen handler
from touch_screen import TouchScreen
touch_screen = TouchScreen(
    is_touched_fn=is_touched_fn,
    read_data_fn=touch_input.read_data,
    min_x=200,
    max_x=3600,
    min_y=250,
    max_y=3700,
    display_width=display.width, 
    display_height=display.height,
    invert_y=True
)


##############################
# Device
##############################
from device import Device

device = Device(
    name="Keyboard Featherwing Remote",
    display_controller=display_controller,
    keyboard=keyboard,
    touch_screen=touch_screen,
    neopixel=neopixel,
    activity_index=loaded_config.activity_index,
    brightness_index=loaded_config.brightness_index
)

# Hide the loading label
display_controller.root_group.remove(loading_label)
loading_label = None

##############################
# Mode handling
##############################
import gc
from remote_mode import RemoteMode
from config_mode import ConfigMode

current_mode = None

# Set the current mode
def set_mode(mode):
    global current_mode

    if current_mode is not None:
        current_mode.exit()

    current_mode = mode

    if mode is not None:
        mode.enter()

    gc.collect()
    print(f"free memory: {gc.mem_free()}")

# Callback for remote mode; called when user chooses to go to config mode
def on_goto_config():
    goto_config_mode()

# Go to remote mode
def goto_remote_mode():
    remote_mode = RemoteMode(device=device, on_goto_config=on_goto_config)
    set_mode(remote_mode)

# Callback for config mode; called when user makes activity selection
def on_activity_selected():
    save_config(
        activity_index=device.activity_index, 
        color_index=display_controller.color_index,
        brightness_index=device.brightness_index
    )

    goto_remote_mode()

# Go to config mode
def goto_config_mode():
    config_mode = ConfigMode(device=device, on_activity_selected=on_activity_selected)
    set_mode(config_mode)

# Start in remote mode
goto_remote_mode()

##############################
# Main loop
##############################
def update():
    device.update()
    current_mode.update()
    time.sleep(0.001)
