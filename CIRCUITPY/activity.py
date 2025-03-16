from function_key import *
from collections import namedtuple

# Type used to define a button's action and visual information
Action = namedtuple("Action", ['hid_type', 'code', 'icon'])

# Type used to describe the configuration of all the buttons
Activity = namedtuple("Activity", ['name', 'show_mouse_message', 'L1', 'L2', 'R1', 'R2', 'UP', 'RIGHT', 'DOWN', 'LEFT', 'SELECT'])

# Type used to define the list of all activities
ActivityList = namedtuple("ActivityList", ['ACTIVITY_1', "ACTIVITY_2", "ACTIVITY_3", "ACTIVITY_4"])

# namedtuple._asdict() and ._fields are not available in CircuitPython,
# so provide a function to convert a given activity to a dictionary.
def dict_from_activity(c):
    return {
        "name": c.name,
        "show_mouse_message": c.show_mouse_message,
        L1: c.L1,
        L2: c.L2,
        R1: c.R1,
        R2: c.R2,
        UP: c.UP,
        RIGHT: c.RIGHT,
        DOWN: c.DOWN,
        LEFT: c.LEFT,
        SELECT: c.SELECT
    }