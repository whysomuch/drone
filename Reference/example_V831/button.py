import time
class BUTTON:
    def __init__(self, line, bank, chip=1, mode=2):
        from maix import gpio
        self.button = gpio.gpio(line, bank, chip, mode)
    def is_pressed(self):
        if self.button.get_value() != 1:
            return True
    def __del__(self):
        self.button.release()

global key
key = BUTTON(6, "H")
print(key.button.source)


while True:
    if key.is_pressed():
        print("pressed!!")
