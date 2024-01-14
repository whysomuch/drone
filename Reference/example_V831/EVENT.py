ffrom maix import evdev
from select import select
dev = evdev.InputDevice('/dev/input/event9')

while True:
  select([dev], [], [])
  for event in dev.read():
    print(event.code, event.value)
