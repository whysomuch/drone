from maix import i2c
i2c = i2c.I2CDevice('/dev/i2c-2', 0x26)
i2c.write(0x1, b'\xAA')
print(i2c.read(0x1, 1))
