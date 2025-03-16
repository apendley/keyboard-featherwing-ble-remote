import time
import displayio
import sprites
from bbq10keyboard import STATE_PRESS, STATE_RELEASE, STATE_LONG_PRESS
import function_key
from user import colors
import brightness
from user.activities import ACTIVITIES
from sprite_sheet import SpriteInstance

from mode import Mode

class ConfigMode(Mode):
    def __init__(self, device, on_activity_selected):
        super().__init__(device)
        self._on_activity_selected = on_activity_selected

    def enter(self):
        print("ConfigMode")

        display = self.device.display_controller

        self._group = displayio.Group()
        self._labels = []
        self._button_icon_views = []

        # Title
        new_label = display.add_label(
            to_group=self._group,
            text="Select Activity",
            x=0,
            y=0,
            h_align=display.ALIGN_LEADING,
            v_align=display.ALIGN_LEADING,
            padding=True,
            scale=2
        )
        self._labels.append(new_label)

        # Activity title labels
        ACTIVITY_Y = display.layout.height // 2 - 50
        ACTIVITY_SPACING = 30

        for i in range(4):
            new_label = display.add_label(
                to_group=self._group,
                text=f"{i + 1}: {ACTIVITIES[i].name}",
                x=display.layout.DBUTTON_X,
                y=ACTIVITY_Y + i * ACTIVITY_SPACING,
                scale=2
            )
            self._labels.append(new_label)

        # L1 button icon
        new_icon = display.add_icon(
            to_group=self._group,
            content="1",
            x=display.layout.L1_X, 
            y=display.layout.BUTTON_ICON_Y,
            h_align=display.ALIGN_LEADING
        )
        self._button_icon_views.append(new_icon.view)

        # L2 button icon
        new_icon = display.add_icon(
            to_group=self._group,
            content="2",
            x=display.layout.L2_X, 
            y=display.layout.BUTTON_ICON_Y,
            h_align=display.ALIGN_LEADING
        )
        self._button_icon_views.append(new_icon.view)

        # R1 button icon
        new_icon = display.add_icon(
            to_group=self._group,
            content="3",
            x=display.layout.R1_X, 
            y=display.layout.BUTTON_ICON_Y,
            h_align=display.ALIGN_TRAILING
        )
        self._button_icon_views.append(new_icon.view)

        # R2 button icon
        new_icon = display.add_icon(
            to_group=self._group,
            content="4",
            x=display.layout.R2_X, 
            y=display.layout.BUTTON_ICON_Y,
            h_align=display.ALIGN_TRAILING
        )
        self._button_icon_views.append(new_icon.view)

        # Finally, add our group to the root group
        display.root_group.append(self._group)

    def update(self):
        device = self.device
        touch_screen = device.touch_screen
        display = device.display_controller

        # Update the touch pad
        touch_screen.update()

        # Read keys from the keyboard
        key_count, key_events = device.read_keys()

        # Keep device from idling if input is received
        if touch_screen.touched or (key_count > 0):
            device.did_interact()

        # We'll set this to true if the UI color changes
        update_ui_color = False

        for key_state, key_code in key_events:
            if key_state == STATE_PRESS:
                # Function button pressed; select activity and return.
                if key_code == function_key.L1:
                    self._select_activity(0)
                    return
                elif key_code == function_key.L2:
                    self._select_activity(1)
                    return
                elif key_code == function_key.R1:
                    self._select_activity(2)
                    return
                elif key_code == function_key.R2:
                    self._select_activity(3)
                    return

                # LEFT/RIGHT to adjust color
                elif key_code == function_key.RIGHT:
                    color_index = display.color_index + 1

                    if color_index >= len(colors.ALL):
                        color_index = 0

                    self._set_color(color_index)
                elif key_code == function_key.LEFT:
                    color_index = display.color_index - 1

                    if color_index < 0:
                        color_index = len(colors.ALL) - 1

                    self._set_color(color_index)

                # UP/DOWN to adjust brightness
                elif key_code == function_key.UP:
                    brightness_index = device.brightness_index + 1

                    if brightness_index > brightness.MAX_INDEX:
                        brightness_index = brightness.MAX_INDEX

                    self._set_brightness(brightness_index)
                elif key_code == function_key.DOWN:
                    brightness_index = device.brightness_index - 1

                    if brightness_index < brightness.MIN_INDEX:
                        brightness_index = brightness.MIN_INDEX

                    self._set_brightness(brightness_index)

    def exit(self):
        display = self.device.display_controller

        display.root_group.remove(self._group)
        self._group = None
        self._labels = None
        self._sprites = None

    def _set_color(self, color_index):
        device = self.device
        display = device.display_controller

        display.color_index = color_index

        # Redraw the battery indicator
        device.invalidate_battery()
        device.update()

        # Change all the label colors
        for label in self._labels:
            label.color = display.foreground_color

        # Change all of the button icon colors
        for view in self._button_icon_views:
            if isinstance(view, SpriteInstance):
                view.tilegrid.pixel_shader = display.palette
            else:
                view.color = display.background_color
                view.background_color = display.foreground_color

    def _set_brightness(self, brightness_index):
        device = self.device
        device.brightness_index = brightness_index

    def _select_activity(self, activity_index):
        self.device.activity_index = activity_index

        if self._on_activity_selected:
            self._on_activity_selected()
            self._on_activity_selected = None