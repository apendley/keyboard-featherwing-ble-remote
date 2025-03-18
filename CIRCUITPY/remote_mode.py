import displayio
from adafruit_ticks import ticks_ms, ticks_diff
from user import colors
import sprites
import function_key
from activity import dict_from_activity
from sprite_sheet import SpriteSheet
from bbq10keyboard import STATE_PRESS, STATE_RELEASE, STATE_LONG_PRESS

from mode import Mode

CONFIG_HOLD_DURATION = 1500

MOUSE_SENSITIVITY_X = 3.0
MOUSE_SENSITIVITY_Y = 3.0

BLUETOOTH_ANIMATION_FRAME_DELAY = 500
BLUETOOTH_ANIMATION_FRAMES = [sprites.BT_01, sprites.BT_02, sprites.BT_03, sprites.BT_04]
BLUETOOTH_ANIMATION_FRAME_COUNT = len(BLUETOOTH_ANIMATION_FRAMES)

class RemoteMode(Mode):
    def __init__(self, device, on_goto_prefs):
        super().__init__(device)
        self._on_goto_prefs = on_goto_prefs

        # Title-label-as-config-button
        self._title_label = None
        self._was_touched = False
        self._is_title_pressed = False
        self._title_press_start_time = None

        # Bluetooth connecting animation
        self._bt_sprite_frame = 0
        self._bt_animation_timer = 0
        self._bt_sprite = None

    def enter(self):
        print("RemoteMode")

        device = self.device
        display = self.device.display_controller

        # Set up connected group
        self._connected_group = displayio.Group()
        self._connected_group.hidden = True
        display.root_group.append(self._connected_group)

        # Activity label
        self._title_label = display.add_label(
            to_group=self._connected_group,
            text=f"{device.activity.name}",
            x=0,
            y=0,
            h_align=display.ALIGN_LEADING,
            v_align=display.ALIGN_LEADING,
            padding=True,
            scale=2
        )

        # Touch label and icon
        if device.activity.show_mouse_message:
            touch_label = display.add_label(
                to_group=self._connected_group,
                text="Touch screen to move mouse",
                x=display.layout.DBUTTON_X + SpriteSheet.SPRITE_WIDTH // 2,
                y=display.layout.TOUCH_SCREEN_LABEL_Y                
            )

            display.add_sprite(
                to_group=self._connected_group, 
                sprite_frame=sprites.TOUCH_SCREEN,
                x=display.layout.DBUTTON_X - (touch_label.width - SpriteSheet.SPRITE_WIDTH) // 2,
                y=display.layout.TOUCH_SCREEN_LABEL_Y + 2,
                h_align=display.ALIGN_TRAILING
            )

        # L1 button icon
        event = device.activity.L1
        if event:
            display.add_icon(
                to_group=self._connected_group,
                content=event.icon, 
                x=display.layout.L1_X, 
                y=display.layout.BUTTON_ICON_Y,
                h_align=display.ALIGN_LEADING
            )

        # L2 button icon
        event = device.activity.L2
        if event:
            display.add_icon(
                to_group=self._connected_group,
                content=event.icon, 
                x=display.layout.L2_X, 
                y=display.layout.BUTTON_ICON_Y,
                h_align=display.ALIGN_LEADING
            )

        # R1 button icon
        event = device.activity.R1
        if event:
            display.add_icon(
                to_group=self._connected_group,
                content=event.icon, 
                x=display.layout.R1_X, 
                y=display.layout.BUTTON_ICON_Y,
                h_align=display.ALIGN_TRAILING

            )

        # R2 button icon
        event = device.activity.R2
        if event:
            display.add_icon(
                to_group=self._connected_group,
                content=event.icon, 
                x=display.layout.R2_X, 
                y=display.layout.BUTTON_ICON_Y,
                h_align=display.ALIGN_TRAILING
            )

        # DBUTTON Select button icon
        select_button_size = None
        event = device.activity.SELECT
        if event:
            select_icon = display.add_icon(
                to_group=self._connected_group,
                content=event.icon, 
                x=display.layout.DBUTTON_X,
                y=display.layout.DBUTTON_Y
            )

        # Uniformly space the icon in the dpad icon map
        DBUTTON_ICON_SPACE_X = None
        DBUTTON_ICON_SPACE_Y = None

        if select_icon is None:
            DBUTTON_ICON_SPACE_X = 24
            DBUTTON_ICON_SPACE_Y = 24
        else:
            DBUTTON_ICON_SPACE_X = select_icon.width // 2 + 8
            DBUTTON_ICON_SPACE_Y = select_icon.height // 2 + 8

        # DBUTTON up icon
        event = device.activity.UP
        if event:
            display.add_icon(
                to_group=self._connected_group,
                content=event.icon, 
                x=display.layout.DBUTTON_X,
                y=display.layout.DBUTTON_Y - DBUTTON_ICON_SPACE_Y,
                v_align=display.ALIGN_TRAILING
            )

        # DBUTTON right icon
        event = device.activity.RIGHT
        if event:
            display.add_icon(
                to_group=self._connected_group,
                content=event.icon, 
                x=display.layout.DBUTTON_X + DBUTTON_ICON_SPACE_X, 
                y=display.layout.DBUTTON_Y,
                h_align=display.ALIGN_LEADING
            )

        # DBUTTON down icon
        event = device.activity.DOWN
        if event:
            display.add_icon(
                to_group=self._connected_group,
                content=event.icon, 
                x=display.layout.DBUTTON_X,
                y=display.layout.DBUTTON_Y + DBUTTON_ICON_SPACE_Y,
                v_align=display.ALIGN_LEADING
            )

        # DBUTTON left icon
        event = device.activity.LEFT
        if event:
            display.add_icon(
                to_group=self._connected_group,
                content=event.icon, 
                x=display.layout.DBUTTON_X - DBUTTON_ICON_SPACE_X, 
                y=display.layout.DBUTTON_Y,
                h_align=display.ALIGN_TRAILING
            )

        # Set up disconnected group
        self._disconnected_group = displayio.Group()
        self._disconnected_group.hidden = True
        display.root_group.append(self._disconnected_group)        

        # Bluetooth connecting animation in disconnected group
        self._bt_sprite = display.add_sprite(
            to_group=self._disconnected_group,
            sprite_frame=BLUETOOTH_ANIMATION_FRAMES[0],
            x=display.layout.DBUTTON_X,
            y=display.layout.height // 2,
            palette=colors.make_palette(colors.BLUE),
            scale=2
        )

        # Display the appropriate group based on BLE connection status
        self._update_group_visibility()

    def update(self):
        device = self.device
        touch_screen = self.device.touch_screen        

        # Update group visibility if connection status changes
        if device.connection_status_changed:
            self._update_group_visibility()

        # Update the touch pad
        touch_screen.update()

        # Read keys from the keyboard
        key_count, key_events = device.read_keys()

        # Keep device from idling if input is received
        if touch_screen.touched or (key_count > 0):
            device.did_interact()

        # Nothing else to do if we aren't connected.
        if not device.is_connected:
            self._update_bt_animation()
            return

        # Check to see if the title label is touched and held.
        # If so, call the "goto config" callback and return
        if self._check_config_selected():
            if self._on_goto_prefs:
                self._on_goto_prefs()
                self._on_goto_prefs = None
            return

        # Move the mouse, if the title button is not currently pressed.
        if touch_screen.touch_moved and not self._is_title_pressed:
            delta_x, delta_y = touch_screen.touch_delta
            delta_x = int(delta_x * MOUSE_SENSITIVITY_X)
            delta_y = int(delta_y * MOUSE_SENSITIVITY_Y)
            device.hid_mouse.move(delta_x, delta_y)

        # convert activity into a dictionary so we can query for the activity's keys
        config_dict = dict_from_activity(device.activity)

        # Translate hardware keyboard/button events into HID keyboard, consumer control, or mouse button events.
        for key_state, key_code in key_events:
            # If this is a function key
            if key_code in config_dict:
                event = config_dict[key_code]

                if event:
                    if event.hid_type == function_key.HID_KEYBOARD:
                        if key_state == STATE_PRESS:
                            device.hid_keyboard.press(event.code)
                        elif key_state == STATE_RELEASE:
                            device.hid_keyboard.release(event.code)

                    elif event.hid_type == function_key.HID_KEYBOARD_LAYOUT:
                        self._emit_keyboard_layout_keys(key_state, event.code)

                    elif event.hid_type == function_key.HID_CONSUMER_CONTROL:
                        if key_state == STATE_PRESS:
                            device.hid_cc.press(event.code)
                        elif key_state == STATE_RELEASE:
                            device.hid_cc.release()

                    elif event.hid_type == function_key.HID_MOUSE:
                        if key_state == STATE_PRESS:
                            device.hid_mouse.press(event.code)
                        elif key_state == STATE_RELEASE:
                            device.hid_mouse.release(event.code)

            # Should be a standard key from the keyboard
            else:
                self._emit_keyboard_layout_keys(key_state, key_code)

    def exit(self):
        display = self.device.display_controller

        display.root_group.remove(self._connected_group)
        self._connected_group = None

        display.root_group.remove(self._disconnected_group)
        self._disconnected_group = None

        self._bt_sprite = None
        self._title_label = None

    def _update_group_visibility(self):
        if self.device.is_connected:
            self._connected_group.hidden = False
            self._disconnected_group.hidden = True
        else:
            self._connected_group.hidden = True
            self._disconnected_group.hidden = False
            self._start_bt_animation()

    def _emit_keyboard_layout_keys(self, key_state, layout_key):
        device = self.device
        keycodes = None

        try:
            keycodes = device.hid_keyboard_layout.keycodes(layout_key)
        except Exception as e:
            print(e)

        if keycodes:
            if key_state == STATE_PRESS:
                device.hid_keyboard.press(*keycodes)
            elif key_state == STATE_RELEASE:
                device.hid_keyboard.release(*keycodes)

    def _set_label_color_inverted(self, label, inverted):
        display = self.device.display_controller

        if inverted:
            label.color = display.background_color
            label.background_color = display.foreground_color
        else:
            label.color = display.foreground_color
            label.background_color = display.background_color

    def _label_contains_point(self, label, point):
        x, y = label.anchored_position
        return (x <= point[0] <= x + label.width * label.scale) and (y <= point[1] <= y + label.height * label.scale)

    def _check_config_selected(self):
        touch_screen = self.device.touch_screen

        touch_point = touch_screen.touch_point
        is_touched = touch_point is not None

        if is_touched:
            if self._was_touched:
                if self._is_title_pressed:
                    if self._label_contains_point(self._title_label, touch_point):
                        now = ticks_ms()

                        if ticks_diff(now, self._title_press_start_time) > CONFIG_HOLD_DURATION:
                            return True
                    else:
                        self._is_title_pressed = False
                        self._set_label_color_inverted(self._title_label, False)
            else:
                if self._label_contains_point(self._title_label, touch_point):
                    self._is_title_pressed = True
                    self._set_label_color_inverted(self._title_label, True)
                    self._title_press_start_time = ticks_ms()
        else:
            if self._is_title_pressed:
                self._is_title_pressed = False
                self._set_label_color_inverted(self._title_label, False)

        self._was_touched = is_touched        

        return False

    def _start_bt_animation(self):
        self._bt_sprite_frame = 0
        self._bt_animation_last_update = ticks_ms()

    def _update_bt_animation(self):
        if self._bt_sprite is None:
            return

        now = ticks_ms()

        if ticks_diff(now, self._bt_animation_last_update) < BLUETOOTH_ANIMATION_FRAME_DELAY:
            return

        self._bt_animation_last_update = now

        self._bt_sprite_frame += 1

        if self._bt_sprite_frame >= BLUETOOTH_ANIMATION_FRAME_COUNT:
            self._bt_sprite_frame = 0

        self._bt_sprite.tilegrid[0] = BLUETOOTH_ANIMATION_FRAMES[self._bt_sprite_frame]