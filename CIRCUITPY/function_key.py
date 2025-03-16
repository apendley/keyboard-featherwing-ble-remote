##########################################################
# Keys emitted by the keyboard for the function buttons
##########################################################
UP = '\x01'
DOWN = '\x02'
LEFT = '\x03'
RIGHT = '\x04'
SELECT = '\x05'
L1 = '\x06'
R1 = '\x07'
L2 = '\x11'
R2 = '\x12'

################################################
# The type of HID event emitted by the button
################################################
# HID Keyboard event. Ex: KeyCode.RETURN
HID_KEYBOARD = 0

# HID Keyboard layout event. Ex: 'A'
HID_KEYBOARD_LAYOUT = 1

# Consumer control event. Ex: ConsumerControlCode.VOLUME_INCREMENT
HID_CONSUMER_CONTROL = 2

# Mouse button event. Ex: Mouse.LEFT_BUTTON
HID_MOUSE = 3
