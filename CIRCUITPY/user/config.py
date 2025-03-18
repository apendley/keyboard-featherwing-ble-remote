from collections import namedtuple

# Calibration for touch screen
TouchCalibration = namedtuple("TouchCalibration", [
	"min_x", 
	"max_x", 
	"min_y", 
	"max_y", 
	"invert_y"]
)

# Device config settings
DeviceConfig = namedtuple("DeviceConfig", [
	"ble_name", 
	"neopixel_color", 
	"neopixel_max_brightness", 
	"low_voltage_warning", 
	"touch_calibration"]
)

# Feel free to edit these seetings as needed/desired.
CONFIG = DeviceConfig(
	ble_name="Keyboard Featherwing Remote",
	neopixel_color=0x0000FF,
	neopixel_max_brightness=0.04,
	low_voltage_warning=3.6,

	touch_calibration=TouchCalibration(
    	min_x=200,
    	max_x=3600,
    	min_y=250,
    	max_y=3700,    
    	invert_y=True		
	)
)