MicroPython MAX44009 Ambient Light Sensor

```
import max44009
from machine import I2C, Pin
i2c = I2C(scl=Pin(22), sda=Pin(21))

sensor = max44009.MAX44009(i2c)

sensor.lux()
136.8
```
