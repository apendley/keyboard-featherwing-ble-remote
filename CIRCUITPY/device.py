import board
from adafruit_ticks import ticks_ms, ticks_diff
from analogio import AnalogIn
from user.activities import ACTIVITIES
from user import colors
import brightness
import sprites
from display_controller import DisplayController
import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.mouse import Mouse
from adafruit_simplemath import constrain
from user.config import CONFIG

BATTERY_UPDATE_INTERVAL = 1000
BLE_SCANNING_BLINK_INTERVAL = 500
IDLE_BACKLIGHT_SHUTOFF_DURATION = 30 * 1000
LOW_VOLTAGE = constrain(CONFIG.low_voltage_warning, 3.2, 4.0)

class Device:
    def __init__(self, display_controller, keyboard, touch_screen, neopixel, activity_index, brightness_index):
        self._display_controller = display_controller
        self._keyboard = keyboard
        self._touch_screen = touch_screen
        self._neopixel = neopixel

        # Brightness settings
        self._set_brightness(brightness_index)

        # Battery tracking
        self._vbat_pin = AnalogIn(board.VOLTAGE_MONITOR)
        self._vbat_ref = self._vbat_pin.reference_voltage
        self._last_battery = None
        self._last_battery_update_time = None

        # Battery UI
        self._battery_label = display_controller.add_label(
            to_group=display_controller.root_group, 
            text=self._get_voltage_text(self._get_voltage()),
            x=display_controller.layout.width - 2, 
            y=0,
            h_align=DisplayController.ALIGN_TRAILING,
            v_align=DisplayController.ALIGN_LEADING,
            padding=True,
            scale=2
        )
        self._battery_label.hidden = True

        self._battery_sprite = display_controller.add_sprite(
            to_group=display_controller.root_group, 
            sprite_frame=sprites.BATTERY_FULL, 
            x=0, 
            y=-2,
            h_align=DisplayController.ALIGN_TRAILING,
            v_align=DisplayController.ALIGN_LEADING
        )
        self._battery_sprite.group.hidden = True
        self._update_battery()

        self._battery_sprite.group.hidden = False
        self._battery_label.hidden = False

        # Current activity index
        self._activity_index = activity_index

        # BLE Device info
        self._device_info = DeviceInfoService(software_revision="1.1.0", manufacturer="Aaron Pendley")

        # BLE HID service
        self._ble_hid = HIDService()

        # Advertise as "Keyboard" (0x03C1) icon when pairing
        # https://www.bluetooth.com/specifications/assigned-numbers/
        self._advertisement = ProvideServicesAdvertisement(self._ble_hid)
        self._advertisement.appearance = 961

        self._scan_response = Advertisement()
        self._scan_response.complete_name = CONFIG.ble_name

        self._ble_radio = adafruit_ble.BLERadio()
        self._ble_radio.name = CONFIG.ble_name

        # Track connection state transtitions
        self._is_connected = self._ble_radio.connected
        self._was_connected = False

        if self._is_connected:
            print("Connected")
        else:
            print("Advertising...")
            self._ble_radio.start_advertising(self._advertisement, self._scan_response)

        # HID
        self._hid_keyboard = Keyboard(self._ble_hid.devices)
        self._hid_keyboard_layout = KeyboardLayoutUS(self._hid_keyboard)
        self._hid_cc = ConsumerControl(self._ble_hid.devices)
        self._hid_mouse = Mouse(self._ble_hid.devices)

        # BLE status display via NeoPixel
        self._neopixel.brightness = brightness.get_neopixel_brightness(self._brightness_index)
        self._last_ble_scanning_blink_time = None
        self._ble_scanning_blink_state = True

        # Idle handler
        self._last_interaction = None
        self._is_idle = False

    @property
    def display_controller(self):
        return self._display_controller

    @property
    def keyboard(self):
        return self._keyboard

    @property
    def touch_screen(self):
        return self._touch_screen

    @property
    def neopixel(self):
        return self._neopixel
    
    @property
    def is_connected(self):
        return self._is_connected

    @property
    def was_connected(self):
        return self._was_connected

    @property
    def connection_status_changed(self):
        return self._is_connected != self._was_connected

    @property
    def activity_index(self):
        return self._activity_index

    @activity_index.setter
    def activity_index(self, i):
        self._activity_index = i

    @property
    def activity(self):
        return ACTIVITIES[self._activity_index]

    @property
    def brightness_index(self):
        return self._brightness_index

    @brightness_index.setter
    def brightness_index(self, i):
        if self._brightness_index != i:
            self._set_brightness(i)

    @property
    def display_brightness(self):
        return brightness.get_display_brightness(self._brightness_index)

    @property
    def keyboard_brightness(self):
        return brightness.get_keyboard_brightness(self._brightness_index)

    @property
    def hid_keyboard(self):
        return self._hid_keyboard

    @property
    def hid_keyboard_layout(self):
        return self._hid_keyboard_layout

    @property
    def hid_cc(self):
        return self._hid_cc
    
    @property
    def hid_mouse(self):
        return self._hid_mouse

    def did_interact(self):
        if self._is_idle:
            self._keyboard.keyboard_backlight = self.keyboard_brightness
            self._keyboard.display_backlight = self.display_brightness
            self._neopixel.brightness = brightness.get_neopixel_brightness(self._brightness_index)

        self._is_idle = False
        self._last_interaction = ticks_ms()

    def invalidate_battery(self):
        self._last_battery_update_time = None
        self._last_battery = None

    def read_keys(self):
        key_count = self._keyboard.key_count

        if key_count > 0:
            key_events = self._keyboard.keys
        else:
            key_events = []

        return (key_count, key_events)      

    def update(self):
        self._was_connected = self._is_connected
        self._is_connected = self._ble_radio.connected

        if self.was_connected and not self.is_connected:
            print("Disconnected")
            self._ble_radio.start_advertising(self._advertisement, self._scan_response)
            self.did_interact()
        elif self.is_connected and not self.was_connected:
            print("Connected")
            self.did_interact()

        self._update_battery()
        self._update_ble_neopixel()
        self._update_idle_controller()

    def _get_voltage(self):
        v = (self._vbat_pin.value * self._vbat_ref) / 65536 * 2
        return round(v, 1)        

    def _get_voltage_text(self, voltage):
        if voltage <= LOW_VOLTAGE:
            return f"{voltage:.1f}V!"
        else:
            return f"{voltage:.1f}V"

    def _update_battery(self):
        now = ticks_ms()

        if self._last_battery_update_time is None or ticks_diff(now, self._last_battery_update_time) >= BATTERY_UPDATE_INTERVAL:
            self._last_battery_update_time = now
            battery_voltage = self._get_voltage()
 
            if battery_voltage != self._last_battery:
                self._last_battery = battery_voltage
                self._battery_label.text = self._get_voltage_text(battery_voltage)

                if battery_voltage <= LOW_VOLTAGE:
                    battery_color = colors.RED
                    self._battery_sprite.tilegrid[0] = sprites.BATTERY_LOW
                else:
                    battery_color = self._display_controller.foreground_color
                    self._battery_sprite.tilegrid[0] = sprites.BATTERY_FULL

                self._battery_label.color = battery_color
                self._battery_sprite.tilegrid.pixel_shader = colors.make_palette(battery_color)

                # Reposition battery sprite based on label's new width
                label_x = self._battery_label.anchored_position[0]
                label_width = self._battery_label.width * self._battery_label.scale
                sprite_width = self._display_controller._sprite_sheet.SPRITE_WIDTH
                battery_sprite_x = label_x - label_width - sprite_width - 6
                self._battery_sprite.group.x = battery_sprite_x

    def _update_idle_controller(self):
        # Kick off the interaction idle timer if there hasn't been an interaction yet
        if self._last_interaction is None:
            self.did_interact()

        now = ticks_ms()

        if not self._is_idle and (ticks_diff(now, self._last_interaction) >= IDLE_BACKLIGHT_SHUTOFF_DURATION):
            self._is_idle = True
            self._keyboard.keyboard_backlight = 0.0
            self._keyboard.display_backlight = 0.0
            self._neopixel.brightness = brightness.get_neopixel_brightness(0)

    def _update_ble_neopixel(self):
        if self.is_connected:
            self.neopixel.fill(CONFIG.neopixel_color)
        else:
            if self._last_ble_scanning_blink_time is None or ticks_diff(ticks_ms(), self._last_ble_scanning_blink_time) >= 500:
                self._last_ble_scanning_blink_time = ticks_ms()            
                self._ble_scanning_blink_state = not self._ble_scanning_blink_state

                if self._ble_scanning_blink_state:
                    self.neopixel.fill(CONFIG.neopixel_color)
                else:
                    self.neopixel.fill(0)

    def _set_brightness(self, i):
        self._brightness_index = i
        self._keyboard.display_backlight = brightness.get_display_brightness(i)
        self._keyboard.keyboard_backlight = brightness.get_keyboard_brightness(i)
        self._neopixel.brightness = brightness.get_neopixel_brightness(i)
