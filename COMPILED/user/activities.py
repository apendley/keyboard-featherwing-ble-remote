from function_key import *
from sprites import *
from activity import Action, Activity, ActivityList
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.mouse import Mouse

# See https://docs.circuitpython.org/projects/hid/en/latest/api.html#adafruit_hid.keycode.Keycode
# for a handy reference of valid Keycode values.

# See https://docs.circuitpython.org/projects/hid/en/latest/api.html#adafruit_hid.mouse.Mouse
# for a list of valid mouse button values

# See https://docs.circuitpython.org/projects/hid/en/latest/api.html#adafruit_hid.consumer_control_code.ConsumerControlCode
# for an abbreviated list of consumer control codes. There are tons of codes, so if you don't see one here that you'd like to use,
# check https://www.usb.org/sites/default/files/hut1_21_0.pdf#page=118

# You can add any custom codes you'd like that aren't defined in ConsumerControlCode below (see CC_MENU for an example).

# AppleTV uses this code for "home"
CC_MENU = 0x40

# The list of activity presets.
# Assign None to a function button to make it do nothing (e.g. R2=None)
ACTIVITIES = ActivityList(
    ACTIVITY_1=Activity(
        name="Media",
        show_mouse_message=True,

        L1=Action(
            hid_type=HID_MOUSE, 
            code=Mouse.LEFT_BUTTON, 
            icon=LEFT_MOUSE
        ),

        L2=Action(
            hid_type=HID_CONSUMER_CONTROL, 
            code=ConsumerControlCode.MUTE, 
            icon=MUTE
        ),

        R1=Action(
            hid_type=HID_CONSUMER_CONTROL,
            code=ConsumerControlCode.VOLUME_DECREMENT, 
            icon=SPEAKER_MINUS
        ),

        R2=Action(
            hid_type=HID_CONSUMER_CONTROL, 
            code=ConsumerControlCode.VOLUME_INCREMENT,
            icon=SPEAKER_PLUS
        ),

        UP=Action(
            hid_type=HID_KEYBOARD, 
            code=Keycode.UP_ARROW,
            icon=UP_ARROW
        ),

        DOWN=Action(
            hid_type=HID_KEYBOARD, 
            code=Keycode.DOWN_ARROW,
            icon=DOWN_ARROW
        ),

        LEFT=Action(
            hid_type=HID_KEYBOARD, 
            code=Keycode.LEFT_ARROW, 
            icon=LEFT_ARROW
        ),

        RIGHT=Action(
            hid_type=HID_KEYBOARD, 
            code=Keycode.RIGHT_ARROW,
            icon=RIGHT_ARROW
        ),

        SELECT=Action(
            hid_type=HID_CONSUMER_CONTROL, 
            code=ConsumerControlCode.PLAY_PAUSE, 
            icon=PLAY_PAUSE
        )
    ),

    ACTIVITY_2=Activity(
        name="Photo Booth",
        show_mouse_message=True,
        
        L1=Action(
            hid_type=HID_MOUSE, 
            code=Mouse.LEFT_BUTTON,
            icon=LEFT_MOUSE
        ),
        
        L2=Action(
            hid_type=HID_CONSUMER_CONTROL, 
            code=ConsumerControlCode.PLAY_PAUSE,
            icon=PLAY_PAUSE
        ),
        
        R1=Action(
            hid_type=HID_KEYBOARD, 
            code=Keycode.RETURN, 
            icon=RETURN,
        ),
        
        R2=Action(
            hid_type=HID_KEYBOARD, 
            code=Keycode.ESCAPE,
            icon="ESC"
        ),
        
        UP=Action(
            hid_type=HID_KEYBOARD, 
            code=Keycode.UP_ARROW,
            icon=UP_ARROW
        ),
        
        DOWN=Action(
            hid_type=HID_KEYBOARD, 
            code=Keycode.DOWN_ARROW,
            icon=DOWN_ARROW
        ),
        
        LEFT=Action(
            hid_type=HID_KEYBOARD, 
            code=Keycode.LEFT_ARROW,
            icon=LEFT_ARROW
        ),
        
        RIGHT=Action(
            hid_type=HID_KEYBOARD, 
            code=Keycode.RIGHT_ARROW,
            icon=RIGHT_ARROW
        ),
        
        SELECT=Action(
            hid_type=HID_KEYBOARD, 
            code=Keycode.RETURN,
            icon=RETURN
        )
    ),

   ACTIVITY_3=Activity(
        name="Mac",
        show_mouse_message=True,

        L1=Action(
            hid_type=HID_MOUSE, 
            code=Mouse.LEFT_BUTTON,
            icon=LEFT_MOUSE
        ),

        L2=Action(
            hid_type=HID_MOUSE, 
            code=Mouse.RIGHT_BUTTON,
            icon=RIGHT_MOUSE
        ),
        
        R1=Action(
            hid_type=HID_KEYBOARD, 
            code=Keycode.OPTION,
            icon=OPTION
        ),
        
        R2=Action(
            hid_type=HID_KEYBOARD, 
            code=Keycode.COMMAND,
            icon=COMMAND
        ),
        
        UP=Action(
            hid_type=HID_KEYBOARD, 
            code=Keycode.UP_ARROW,
            icon=UP_ARROW
        ),
        
        DOWN=Action(
            hid_type=HID_KEYBOARD, 
            code=Keycode.DOWN_ARROW,
            icon=DOWN_ARROW
        ),
        
        LEFT=Action(
            hid_type=HID_KEYBOARD, 
            code=Keycode.LEFT_ARROW,
            icon=LEFT_ARROW
        ),

        RIGHT=Action(
            hid_type=HID_KEYBOARD, 
            code=Keycode.RIGHT_ARROW,
            icon=RIGHT_ARROW
        ),

        SELECT=Action(
            hid_type=HID_KEYBOARD, 
            code=Keycode.RETURN,
            icon=RETURN)
    ),

    ACTIVITY_4=Activity(
        name="Apple TV",
        show_mouse_message=False,

        L1=Action(
            hid_type=HID_CONSUMER_CONTROL, 
            code=ConsumerControlCode.VOLUME_DECREMENT, 
            icon=SPEAKER_MINUS
        ),

        L2=Action(
            hid_type=HID_CONSUMER_CONTROL, 
            code=ConsumerControlCode.VOLUME_INCREMENT, 
            icon=SPEAKER_PLUS
        ),

        R1=Action(
            hid_type=HID_KEYBOARD, 
            code=Keycode.ESCAPE, 
            icon=BACK
        ),

        R2=Action(
            hid_type=HID_CONSUMER_CONTROL, 
            code=CC_MENU, 
            icon=HOME
        ),

        UP=Action(
            hid_type=HID_KEYBOARD, 
            code=Keycode.UP_ARROW, 
            icon=UP_ARROW
        ),

        DOWN=Action(
            hid_type=HID_KEYBOARD, 
            code=Keycode.DOWN_ARROW, 
            icon=DOWN_ARROW
        ),

        LEFT=Action(
            hid_type=HID_KEYBOARD, 
            code=Keycode.LEFT_ARROW, 
            icon=LEFT_ARROW
        ),
        
        RIGHT=Action(
            hid_type=HID_KEYBOARD, 
            code=Keycode.RIGHT_ARROW, 
            icon=RIGHT_ARROW
        ),
        
        SELECT=Action(
            hid_type=HID_KEYBOARD, 
            code=Keycode.RETURN, 
            icon=RETURN
        )
    )
)