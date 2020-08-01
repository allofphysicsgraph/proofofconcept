# simple utility that lists fonts used in given DVI file

import sys
from conv import dviparser
from conv import binfile

if __name__ == '__main__':
	if len(sys.argv) > 1:
		f = binfile.binfile(sys.argv[1])
		(comment, (num, den, mag, u, l), pages, fonts) = dviparser.dviinfo(f)
		for k, (c,s,d,fnt) in fonts.iteritems():
			print "%5d: %s, scale=%d, design size=%0.1f, TFM checksum=0x%08X" % (k, fnt, s, d/65536.0, c)
		f.close()

# vim: ts=4 sw=4
