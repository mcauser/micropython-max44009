# MicroPython MAX44009 Ambient Light Sensor

A MicroPython driver for the MAX44009 ambient light sensor with I2C Interface.

```
import max44009
from machine import I2C, Pin
i2c = I2C(scl=Pin(22), sda=Pin(21))

sensor = max44009.MAX44009(i2c)

sensor.continuous
0

sensor.continuous = 1

sensor.manual = 0

sensor.current_division_ratio = 0

sensor.integration_time = 3

sensor._read_config()
sensor._config
131

sensor.lux
136.8

sensor.lux_fast
126.72

sensor.int_status
0

sensor.int_enable
0

sensor.int_enable = 1

sensor.upper_threshold
188006.4

sensor.upper_threshold = 200

sensor.lower_threshold
0.0

sensor.lower_threshold = 100

sensor.threshold_timer
25500

sensor.threshold_timer = 1000
```

## License

Licensed under the [MIT License](http://opensource.org/licenses/MIT).

Copyright (c) 2020 Mike Causer
