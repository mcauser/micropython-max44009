"""
MicroPython MAX44009 Ambient Light Sensor
https://github.com/mcauser/micropython-max44009

MIT License
Copyright (c) 2019 Mike Causer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__version__ = '0.0.1'

# registers
_MAX44009_INT_STATUS  = const(0x00) # Interrupt status
_MAX44009_INT_ENABLE  = const(0x01) # Interrupt enable
_MAX44009_CONFIG      = const(0x02) # Configuration
_MAX44009_LUX_HI      = const(0x03) # Lux high byte
_MAX44009_LUX_LO      = const(0x04) # Lux low byte
_MAX44009_UP_THRES    = const(0x05) # Upper threshold high byte
_MAX44009_LO_THRES    = const(0x06) # Lower threshold high byte
_MAX44009_THRES_TIMER = const(0x07) # Threshold timer

class MAX44009:
	def __init__(self, i2c, address=0x4A):
		self._i2c = i2c
		self._address = address # 0x4A-0x4B
		self._config = 0x03 # power on reset state
		self._buf = bytearray(1)
		#self.check()

	def check(self):
		if self._i2c.scan().count(self._address) == 0:
			raise OSError('MAX44009 not found at I2C address {:#x}'.format(self._address))

	def config(self, continuous=None, manual=None, current_division_ratio=None, integration_time=None):
		if continuous is not None:
			self._config = (self._config & ~128) | ((continuous << 7) & 128)
		if manual is not None:
			self._config = (self._config & ~64) | ((manual << 6) & 64)
		if current_division_ratio is not None:
			self._config = (self._config & ~8) | ((current_division_ratio << 3) & 8)
		if integration_time is not None:
			self._config = (self._config & ~7) | (integration_time & 7)
		self._buf[0] = self._config
		self._i2c.writeto_mem(self._address, _MAX44009_CONFIG, self._buf)

	def lux(self):
		self._i2c.readfrom_mem_into(self._address, _MAX44009_LUX_HI, self._buf)
		exponent = self._buf[0] >> 4
		mantissa = ((self._buf[0] & 0x0F) << 4)
		self._i2c.readfrom_mem_into(self._address, _MAX44009_LUX_LO, self._buf)
		mantissa |= (self._buf[0] & 0x0F)
		return ((2 ** exponent) * mantissa) * 0.045

	def int_status(self):
		self._i2c.readfrom_mem_into(self._address, _MAX44009_INT_STATUS, self._buf)
		return self._buf[0] & 1

	def int_enable(self):
		self._i2c.readfrom_mem_into(self._address, _MAX44009_INT_ENABLE, self._buf)
		return self._buf[0] & 1

	def set_int_enable(self, en):
		self._buf[0] = en & 1
		self._i2c.writeto_mem(self._address, _MAX44009_INT_ENABLE, self._buf)

	def upper_threshold(self):
		self._i2c.readfrom_mem_into(self._address, _MAX44009_UP_THRES, self._buf)
		exponent = self._buf[0] >> 4
		mantissa = ((self._buf[0] & 0x0F) << 4) | 15
		return ((2 ** exponent) * mantissa) * 0.045

	def set_upper_threshold(self, lux):
		(exponent, mantissa) = self._lux_to_exponent_mantissa(lux)
		self._buf[0] = (exponent << 4) | (mantissa >> 4)
		self._i2c.writeto_mem(self._address, _MAX44009_UP_THRES, self._buf)

	def lower_threshold(self):
		self._i2c.readfrom_mem_into(self._address, _MAX44009_LO_THRES, self._buf)
		exponent = self._buf[0] >> 4
		mantissa = ((self._buf[0] & 0x0F) << 4)
		return ((2 ** exponent) * mantissa) * 0.045

	def set_lower_threshold(self, lux):
		(exponent, mantissa) = self._lux_to_exponent_mantissa(lux)
		self._buf[0] = (exponent << 4) | (mantissa >> 4)
		self._i2c.writeto_mem(self._address, _MAX44009_LO_THRES, self._buf)

	def threshold_timer(self):
		self._i2c.readfrom_mem_into(self._address, _MAX44009_THRES_TIMER, self._buf)
		return self._buf[0] * 100

	def set_threshold_timer(self, ms):
		self._buf[0] = int(ms) // 100
		self._i2c.writeto_mem(self._address, _MAX44009_THRES_TIMER, self._buf)

	def _lux_to_exponent_mantissa(self, lux):
		mantissa = int(lux * 1000) // 45
		exponent = 0
		while (mantissa > 255):
			mantissa >>= 1
			exponent += 1
		return (exponent, mantissa)
