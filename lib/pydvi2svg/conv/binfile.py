# -*- coding: iso-8859-2 -*-
# $Id: binfile.py,v 1.5 2007-05-20 12:20:44 wojtek Exp $
#
# pydvi2svg - extension to built-in file
#
# license: BSD
#
# author: Wojciech Muła
# e-mail: wojciech_mula@poczta.onet.pl
# WWW   : http://wmula.republika.pl

# changelog
"""
 20.05.2007
    - imporoper method called - fixed
  6.10.2006
 	- moved from dviparser.py
 xx.09.2006
 	- first version
"""

from struct import unpack

class binfile(file):
	def _read(self, n=-1):
		data = self.read(n)
		if n > 0 and len(data) != n:
			raise EOFError("Expeced to read %d bytes, got %d" % (n, len(data)))
		else:
			return data
	
	def uint8(self):
		x = unpack('B', self._read(1))[0]
		return x

	def uint16(self):
		x = unpack('>H', self._read(2))[0]
		return x

	def uint24(self):
		x = unpack('>I', '\0' + self._read(3))[0]
		return x

	def uint32(self):
		x = unpack('>L', self._read(4))[0]
		return x

	def int8(self):
		x = unpack('b', self._read(1))[0]
		return x

	def int16(self):
		x = unpack('>h', self._read(2))[0]
		return x

	def int24(self):
		x = unpack('>i', self._read(3) + '\0')[0] >> 8
		return x

	def int32(self):
		x = unpack('>l', self._read(4))[0]
		return x

# vim: ts=4 sw=4
