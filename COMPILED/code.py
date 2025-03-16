from adafruit_ticks import ticks_ms, ticks_diff
START = ticks_ms()

from run import update

END = ticks_ms()
print("Launch time:", ticks_diff(END, START))

while True:
    update()