# keyboard-featherwing-ble-remote
Firmware for a universal BLE keyboard/mouse/remote powered by the Keyboard Featherwing and CircuitPython

![](https://github.com/apendley/keyboard-featherwing-ble-remote/blob/main/images/hero.jpeg)

# Overview
One of the coolest things about [Solder Party's](https://www.solder.party/) [Keyboard Featherwing](https://www.solder.party/docs/keyboard-featherwing/) is its versatility. While it offers a fully-featured hardware package all on its own, the ability to pair it with any Feather board allows it to be extended to do pretty incredible things. In this project, I'm pairing it with a Feather nRF52840 Express to create a universal Bluetooth Low Energy (BLE) keyboard/mouse/remote control, programmed in CircuitPython. 

Using the nRF52840, CircuitPython has the ability to send BLE keyboard, mouse, and consumer control HID events to a host BLE device, such as a computer. This firmware combines the ability to send all 3 from a single device in an easily configurable way, adding yet another of versatility!

Some possible applications:
- Control a laptop connected to a TV remotely, with physical keyboard and full mouse support
- Control an Apple TV, including navigation. Use a physical keyboard when searching!
- Remotely trigger the camera shutter on iPhone/iPad
- Use the 9 programmable buttons to make a BLE "macro pad"
- Practically anything that could benefit from a BLE keyboard, mouse, and/or consumer control remote

Another nice thing about the nRF52840 for this application is its excellent energy efficiency. When using a 2000mAh LiPo battery, I've been able to get between 70-80 hours of active use on a single charge! The Keyboard Featherwing's built-in on/off switch allows extending the battery life even further.

# Firmware features
- Compact physical keyboard makes it easy to type wirelessly on device like laptops/desktops, Raspberry Pis, or anything else that can connect to BLE keyboards.
- Touch screen behaves as a trackpad/mouse when connected to a host device that supports pointer devices.
- 4 activity presets, selectable through an on-screen configuration menu. Further configuration is possible by connecting device to a computer via USB and editing the activities configuration file.
  - Each activity allows you to customize the 4 function buttons and the 5-way direction button to send keyboard, consumer control, and mouse button events 
- Adjustable display/keyboard/NeoPixel brightness
- Adjustable primary user interface color
- Power-saving feature: auto-dim keyboard, screen, and NeoPixel after 30 seconds of inactivity, significantly increasing battery life.
- Battery voltage monitoring and "needs charge" indicator.

# Hardware
- [Keyboard Featherwing Rev2](https://www.solder.party/docs/keyboard-featherwing/rev2/) by Solder Party. In theory the [Rev1](https://www.solder.party/docs/keyboard-featherwing/rev1/) should work too, but I don't have a way to test it. If you do and are willing to, feel free to ping me on Bluesky([apendley.bsky.social](https://bsky.app/profile/apendley.bsky.social)) or Discord (squid.jpg) and let me know if it works or if there are any issues (you can also file an issue here).
- [Feather nRF52840 Express](https://www.adafruit.com/product/4062)
- [3.7V 2000 mAh LiPo battery](https://www.adafruit.com/product/2011)

# Known issues
- Currently, as far as I'm aware, there is no way to force an unpairing from the remote (Keyboard Featherwing) side. You must force unpair/forget from the host side if you wish to pair the Keyboard Featherwing remote with another device.
- Long startup time: it takes ~3 seconds before our program gains control from the boot loader, and another 5-7 seconds to load and initialize libraries.
- Since there is no way to shut off power to the display, touch screen, and keyboard in deep sleep mode, the lowest power draw possible is around ~20 mA. Also, there seems to be a bug causing the touch screen and keyboard to become unresponsive after awaking from deep sleep. As such, deep sleep is not implemented.
- Limited amount of RAM on the nRF52840 puts a lot of pressure on the garbage collector, which can result in slightly hitchy mouse movement when using the touch screen as a trackpad/mouse.
- There seems to be an issue where the name we assign the device in CircuitPython doesn't always "stick". Sometimes it appears to other devices as something similar to "CIRCUITPY0930".
- The shift and alt keys on the Keyboard Featherwing's keyboard do not report shift and alt key presses to CircuitPython (this is by design). However, you can assign the shift, alt, or other inaccesible keys to one of the configurable buttons, and they will be sent as keyboard events.

# Installation
## Install CircuitPython
Install the latest version of CircuitPython 9 onto your Feather nRF52840 according to the instructions [here](https://learn.adafruit.com/introducing-the-adafruit-nrf52840-feather/circuitpython).

## Install source
There are two options for installing the CircuitPython source on your Feather. You can use the pre-compiled source, or the raw source. Using the compiled .mpy files reduces the remote startup time by as much as 1.5 seconds vs. uncompiled files. The tradeoff is that you can't tinker with the core code as easily. If you just want to use the firmware, and aren't interested in the inner workings, this is probably the option you want. NOTE: both options still allow for customizing the activities, since the activities and colors config files are non-compiled python files.

### Raw source
1. Delete all files on your Feather's CIRCUITPY drive.
2. If you haven't done so already, download or clone this repository
3. Once downloaded, copy the contents of the downloaded CIRCUITPY directory onto your Feather's CIRCUITPY drive. Overwrite any existing files if necessary.
   
### Compiled source
1. Delete all files on your Feather's CIRCUITPY drive.
2. If you haven't done so already, download or clone this repository
3. Once downloaded, copy the contents of the downloaded COMPILED directory onto your Feather's CIRCUITPY drive. Overwrite any existing files if necessary.

# Usage
The Keyboard Featherwing Remote uses "activities" to assign commands/events to the 4 function buttons (labeled L1, L2, R1, and R2 below) and the 5-way directional button (D-BUTTON). The main UI consists of the battery indicator and two sub-screens: the pairing/connecting screen, and the remote control screen.

![](https://github.com/apendley/keyboard-featherwing-ble-remote/blob/main/images/buttons-labeled.jpeg)

## Battery indicator
The Feather nRF52840 provides a voltage divider connected to a GPIO pin, allowing us to monitor the battery voltage from our program. The battery indicator is in the top-right corner of the screen. It displays the current battery voltage, and has 2 states: "OK" and "Needs charging". The "OK" state is indicated by the "full battery" icon, whereas the "Needs charging" state is indicated by the "low battery" icon. Additionally, in the "Needs charging" state, the battery icon and voltage text are colored red, and an exclamation point is appended to the voltage text.

![](https://github.com/apendley/keyboard-featherwing-ble-remote/blob/main/images/ss-mac.jpeg)
![](https://github.com/apendley/keyboard-featherwing-ble-remote/blob/main/images/ss-low-battery.jpeg)

## Pairing/Connecting
After booting, if the remote has been previously paired, it will immediately go to the remote control screen, ready to control the paired device. Otherwise, an animation of the Bluetooth logo will display and the NeoPixel will slowly blink blue. The remote will remain in this state until a host device is paired.

![](https://github.com/apendley/keyboard-featherwing-ble-remote/blob/main/images/ss-connecting.jpeg)

## Remote control
This is the main remote control screen. Once connected/paired to a host device, the NeoPixel will stop blinking and remain solid blue. In the top-left corner of the screen shows the name of the current remote activity.

At the bottom of the screen there are 4 icons representing the events mapped to each of the 4 function buttons below them. Above that there are icons arranged in a "plus" configuration representing the events mapped to the D-BUTTON.

![](https://github.com/apendley/keyboard-featherwing-ble-remote/blob/main/images/ss-media.jpeg)

For host devices that support it, the touch screen will behave as a trackpad/mouse. In other words, touching and moving your finger or a stylus to the screen will move the mouse cursor on the host device.

One other thing about that activity label in the top-left corner of the screen: it is the only touch-screen button in the firmware. If you tap this label, you'll notice that it becomes highlighted. If you continue to hold the button for about 1.5 seconds, the remote transitions to the configuration/activity select screen.

![](https://github.com/apendley/keyboard-featherwing-ble-remote/blob/main/images/ss-config-button-idle.jpeg)
![](https://github.com/apendley/keyboard-featherwing-ble-remote/blob/main/images/ss-config-button-pressed.jpeg "Notice that when pressed, the activity text is highlighted")

Because I chose to use the touch screen primarily as a trackpad/mouse, I generally didn't want to implement touch screen buttons-like controls for this firmware. I made an exception here because I did not want to sacrifice any of the physical buttons/keys that could be used to control the host device. Hopefully the title label is out-of-the-way enough that its presence won't interfere with the trackpad/mouse capability.

## Configuration/Activity select
In this screen, you can choose which activity to assign to the remote screen, as well as adjust the display/keyboard/NeoPixel brightness and the main UI color.
- Change brightness
  - Pressing the UP/DOWN directions on the D-BUTTON will increase/decrease the system brightness, respectively. This affects the display brightness, the keyboard brightness, and the overall brightness of the NeoPixel.
- Change UI Color
  - Pressing the LEFT/RIGHT directions on the D-BUTTON will cycle through the available UI colors.
- Select Activity
  - Each of the 4 function buttons below the screen are labeled with the numbers 1-4. Above that is a list of activities, also labeled 1-4. Pressing any of the 4 function buttons will select the corresponding activity, save the configuration (including brightness and color settings) to the SD card, and return to the remote screen configured to use the selected activity.
 
![](https://github.com/apendley/keyboard-featherwing-ble-remote/blob/main/images/ss-config.jpeg)

## "Auto-sleep"
While I didn't implement deep sleep as mentioned in the CAVEATS section, it was still worthwhile to adopt another power-saving technique: turn the display and keyboard backlights off when the remote is "idle". We consider "idle" to mean that the user has not touched the screen or pressed any keys/buttons for about 30 seconds. Once "asleep", if the user touches the touch screen or presses a key/button, the backlight LEDs are turned back on.

With the display brightness at 50% and keyboard brightness at10%, the remote uses ~50 mA. With those backlights turned completely off, the power draw is reduced to ~25 mA. A significant reduction!

# Customization
## Customize activities
Before we get into how to configure the activities, it's helpful to explain a few other concepts first. To start, an "activity" is simple the mapping of the 9 configurable buttons (4 function buttons + D-BUTTON) to "actions". An action consists of 3 pieces of information:
1. The type of HID event the button will emit (defined in function_key.py)
  - HID_KEYBOARD
  - HID_KEYBOARD_LAYOUT
  - HID_CONSUMER_CONTROL
  - HID_MOUSE
2. A compatible event code for that HID event to emit upon pressing/releasing the button. The value of the code depends on the type of HID event:
  - HID_KEYBOARD: The code should be a [Keycode](https://docs.circuitpython.org/projects/hid/en/latest/api.html#adafruit-hid-keycode-keycode)
  - HID_KEYBOARD_LAYOUT: The code should be a typeable character, e.g. 'A', 'g', or '3'
  - HID_CONSUMER_CONTROL: The code should be a [ConsumerControlCode](https://docs.circuitpython.org/projects/hid/en/latest/api.html#adafruit_hid.consumer_control_code.ConsumerControlCode). For an extended list of consumer control codes, see [this page](https://www.usb.org/sites/default/files/hut1_21_0.pdf#page=118).
  - HID_MOUSE: One of the mouse buttons [defined here](https://docs.circuitpython.org/projects/hid/en/latest/api.html#adafruit_hid.mouse.Mouse)
3. An icon to visually represent the action for the button on the Keyboard Featherwing remote display. In the context of an activity, an "icon" can either be an integer value representing a sprite index into the icons sprite sheet, or, if suitable icon does not exist in the sprite sheet, a string that will be displayed as black text on an inverted background. As a handy convenience, all of the sprites in the icons sprite sheet have constants defined in sprites.py.

Here is an example of defining an action for an activity for when the "L1" key is pressed/released that simulates clicking the left mouse button:
```python
    L1=Action(
        hid_type=HID_MOUSE, 
        code=Mouse.LEFT_BUTTON, 
        icon=LEFT_MOUSE
    )

```
This example assigns the "Volume increment" consumer control code to the "UP" key on the D-BUTTON:
```python
UP=Action(
    hid_type=HID_CONSUMER_CONTROL, 
    code=ConsumerControlCode.VOLUME_INCREMENT, 
    icon=SPEAKER_PLUS
)
```

Finally, we get to the ActivityList, which is the overall list of the 4 activities selectable via configuration screen at run-time. An activity list contains an Action (as shown above) for each customizable button, as well as two other pieces of information:
1. The activity's name, e.g. "Media" or "Apple TV"
2. Whether or not we should display the message indicating that the touch screen will behave as a mouse. When paired with some devices that do not use mouse control, it can be helpful to disable this message (note however that currently the mouse events are still sent. This may change in a future update).

Each of the 4 activites can be configured by editing the user/activities.py file on the Feather's CIRCUITPY drive.

A fully-configured activity might look something like this:
```python
    ACTIVITY_2=Activity(
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
    ),
```

Notice that in the case of the Apple TV, standard keyboard key codes are used for directional navigation (the arrow keys), and the use of the return key for selection. This is part of what makes the Keyboard Featherwing remote so versatile!

## Customize color list
One other simple point of customization for the remote is the ability to add/remove/edit the colors that can be selected in the configuration screen. Many default named colors are provided, as well as an array of ALL colors. You can customize this list of colors by editing the user/activities.py file on the Feather's CIRCUITPY drive.

Note that you should not remove the built-in named colors, as there is code elsewhere in the firmware that may depend on them. You may, however:
- Change the actual color value for the built-in colors
- Add additional named colors
- Add/remove colors to the ALL array, which defines the colors that can be selected from the configuration screen.

```python
# Any color in this array is selectable to be the
# primary UI color from the configuration screen
ALL = [
    WHITE,
    ORANGE, 
    AMBER,
    YELLOW,
    GREEN,
    CYAN,
    BLUE,
    PURPLE,
    MAGENTA,
    RED,    
]
```

# Source code walkthrough
If you came across this and thought "Hey, I have a Keyboard Featherwing and an nRF52840 Feather, lemme try this out!", and do not care at all about the code in more detail, you can stop here. You know everything you need to know to use the firmware as-designed! Otherwise, for some of the gory details, read on.
## code.py
For this project, code.py is basically just used to "boot strap" our main program, which is defined in ...
## run.py
run.py is responsible for importing and setting up the hardware drivers and other libraries we need for the rest of the firmware to do its job. Normally this code might live in code.py, but since a lot of work happens here, I wanted to be able to pre-compile this process into an .mpy file.

One perhaps interesting thing about this file is that we don't import all of the libraries at the top of the file as is common in many CircuitPython programs. Instead, run.py lays out a startup process that tries to prioritize things like gaining control of the system's backlight LEDs as soon as possible, and getting something on the display quickly after booting. Importing large libraries can take a significant amount of time, so if we import them all at once at the top of the file, it could be several seconds before our firmware actually gets control of the program flow.

run.py is also responsible for setting up and managing:
- Creation of the DisplayController object, used for most tasks involving the display. This is explained in further detail in the display_controller.py section below.
- Creation of the Device object, which is used by other objects in the application to interface with the remote's hardware and other systems. The Device object is explained in a little more detail in the device.py section below.
- Application flow. This is explained further detail below in the mode.py section below.

## display_controller.py
The DisplayController object is the main interface to the display for other objects. It defines handy constants for things like UI layout, methods to access the underlying display hardware and the displayio root group, and methods that make it simple to create and add sprites and labels to UI groups.

### Sprite sheet
The display controller contains the main sprite sheet, which is used to create sprites/icons by our firmware. The SpriteSheet object is defined in sprite_sheet.py. All sprites are 32x32 pixels wide, as defined by the constants SpriteSheet.SPRITE_WIDTH and .SPRITE_HEIGHT. The sprite sheet also provides the add_sprite method, which creates a sprite using the given sprite index, and adds it to the specified group.

As a convenience, named constants for the sprite indices can be found in sprites.py. This allows our code to reference the sprite indices by memorable names, rather than arbitrary integer values.

### Palette
All of the graphics in this firmware are effectively 1-bit palettized images and text. This means we only have 2 colors, 0 and 1. The actual values that these colors display on the screen is defined by a Palette. The actual colors used are customizable, and can be found in user/colors.py. For this firmware, color 0 is generally always black, and color 1 is the "primary" color.

colors.py contains constants for common colors, as well as an array named ALL which contains a list of colors. Any elements in the ALL array are available to be selected as the primary UI color in the remote's configuration screen.

### Alignment
To make basic layout more convenient, DisplayController's add_sprite, add_label, and add_icon methods all accept two alignment parameters, h_align and v_align. There are 3 possible values for these parameters:
1. ALIGN_LEADING
  - When assigned to h_align, this indicates to position the element so that its left edge is the reference for the x position when laying out the element.
  - When assigned to v_align, this indicates to position the element such that its top edge is the reference for the y position when layout out the element.
2. ALIGN_CENTER
  - When assigned to both h_align and v_align, this indicates to position the element such that its x/y position is centered long the horiztonal/vertical axis, respectively
3. ALIGN_TRAILING
  - When assigned to h_align, this indicates to position the element so that its right edge is the reference for the x position when laying out the element.
  - When assigned to v_align, this indicates to position the element such that its bottom edge is the reference for the y position when layout out the element.

## touch_screen.mpy
The TouchScreen object provides a handy abstraction for easy access to the information our firmware needs from the touch screen, namely:
  - Is the touch screen being touched right now?
  - Where it is being touched?
  - How much has the touch point moved since the last time we checked?

### Calibration
In run.py, when creating the TouchScreen object, four parameters are provided that are used for touch screen calibration: min_x, min_y, max_x, max_y, and invert_y. While the default values provided are probably okay, you can edit their values in run.py if fine tuning is necessary.

### Filtering/Smoothing
One of the other handy things TouchScreen provides is filtering, as touch screen input tends to be pretty noisy. You can find the code for the filters in filters.py. A more in-depth explanation of the filters used can be found [here](https://dlbeer.co.nz/articles/tsf.html), but the short version is that we are applying a combination of 2 filters to compensate for the noise in the touch screen input. The first is a median filter, which smooths out the worst spikes, and the second is an IIR (infinite impulse response) filter to remove low-level noise over a longer sample period. The TouchScreen object also handles a form of debouncing the touch screen. It seems when first touched, the next sample read from the tsc2004 touch screen can be wildly innaccurate. So...we just ignore it, and only process the subsequent samples. With these layers of processing applied, the touch screen now becomes more reliable as a simple track pad.

## device.py
Once run.py has finished setting up all of the hardware and libraries, the Device object is created. From this point on, the Device object is the main interface for the rest of our firmware to access device- and hardware- specific functionality. The Device object exposes properties for all hardware like the keyboard, touch screen, display controller, neopixel, etc. It is also responsible for some more global functionality, such as setting up the BLE stack, managing the NeoPixel to display BLE status, reading the battery voltage monitor/updating the battery UI, controlling the device backlight brightness, etc.

By itself the Device object doesn't do much. Most of the remaining program logic is contained one of two types of Mode object.

## mode.py
In the context of this firmware, generally speaking a "Mode" is a UI "screen". More specifically, each mode can be though of as a state in a finite state machine. In our case, our state machine contains two states, or modes, that determine how the program behaves:
1. "Remote control" mode
2. "Configuration" mode

The Mode class defined in mode.py is used as the superclass for our two modes. Its initializer takes the device object as a parameter. Without access to the device object, our modes/states can't really do much.

The Mode class also provides our concrete subclasses with a common lifetime interface. The 3 key pieces are the enter(), update() , and the exit() methods.

The enter() method is responsible for setting up the mode right before it becomes active. This includes intitializing its UI, etc.

The update() method is resposible for processing input and taking appropriate action, such as sending HID events, as well as updating the UI to reflect the current device state.

The exit() method is responsible for cleaning up right before the mode is about to become inactive. Here we tear down our UI and perform any other necessary cleanup tasks.

The two concrete mode implementations are discussed below.

## remote_mode.py
The RemoteMode object contains the core remote control logic for the firmware. 

When not paired with a host BLE device, the UI consists of an animated Bluetooth icon. 

Once a connection is made, the "remote control" UI is shown, which displays a mapping of the 9 customizable buttons and their actions. When connected, pressing keys on the keyboard, pressing the customizable buttons, and touching the touch screen all send HID events to the paired host, based on the selected activity. The activity label in the top-left corner also behaves as a touch screen "button" that, when held for about 1.5 seconds, will transition the firmware to ConfigMode.

## config_mode.py
The ConfigMode object is responsible for selecting the current activity from the 4 activity presets, as well as adjusting the device brightness and primary UI color. Once an activity selection is made, control is returned back to the RemoteMode.


# Special thanks
## [Kenney assets](https://kenney.nl/)
Many of the sprites used in this firmware are from the excellent [1-bit input prompts](https://kenney.nl/assets/1-bit-input-prompts-pixel-16) asset pack at Kenney.
## [Solder Party](https://www.solder.party/)
Thanks for both the excellent Keyboard Featherwing hardware, as well as for the image from the documentation that I borrowed to frame my screenshots. You can also find them on Bluesky at [@solder.party](https://bsky.app/profile/solder.party)
