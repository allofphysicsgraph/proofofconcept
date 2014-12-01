# -*- coding: iso-8859-2 -*-
# $Id: colors.py,v 1.5 2007-03-13 21:04:15 wojtek Exp $
#
# pydvi2svg - process color.sty special
#
# license: BSD
#
# author: Wojciech Muła
# e-mail: wojciech_mula@poczta.onet.pl
# WWW   : http://wmula.republika.pl

# changelog
"""
 3.10.2006
 	- added support for "color gray v"
	- added function is_colorspecial & execute
 2.10.2006
 	- initial version
"""

def is_colorspecial(special):
	return special.startswith('color ')

color_stack = []
background  = None

def execute(special):
	global color_stack, background

	fields = special.split()
	assert fields[0] == 'color'
	command = fields[1]

	if command == 'pop':
		color_stack.pop(0)
	elif command == 'push':
		if len(fields) == 3:	# "color push dvipsname"
			r,g,b = dvicolornames[fields[2]]
		elif len(fields) == 4 and fields[2] == 'gray':	# "color push gray v"
			v = float(fields[3])
			r,g,b = v,v,v
		elif len(fields) == 6 and fields[2] == 'rgb':	# "color push rgb r g b"
			r = float(fields[3])
			g = float(fields[4])
			b = float(fields[5])
		elif len(fields) == 7 and fields[2] == "cmyk":	# "color push cmyk c m k"
			c = float(fields[3])
			m = float(fields[4])
			y = float(fields[5])
			k = float(fields[6])
			
			r = (1-c)*(1-k)
			g = (1-m)*(1-k)
			b = (1-y)*(1-k)
		else:
			raise NotImplementedError("push command (color package): %s" % special)
		
		color = "#%02x%02x%02x" % (int(r*255), int(g*255), int(b*255))
		color_stack.insert(0, color)
	
	else:
		raise NotImplementedError("color command: %s" % special)


	if color_stack:
		return color_stack[0], background
	else:
		return None, background

dvicolornames = {
"Red"			: (1,0,0),
"Tan"			: (0.86,0.58,0.44),
"Blue"			: (0,0,1),
"Cyan"			: (0,1,1),
"Gray"			: (0.5,0.5,0.5),
"Plum"			: (0.5,0,1),
"Black"			: (0,0,0),
"Brown"			: (0.4,0,0),
"Green"			: (0,1,0),
"Melon"			: (1,0.54,0.5),
"Peach"			: (1,0.5,0.3),
"Sepia"			: (0.3,0,0),
"White"			: (1,1,1),
"Maroon"		: (0.68,0,0),
"Orange"		: (1,0.39,0.13),
"Orchid"		: (0.68,0.36,1),
"Purple"		: (0.55,0.14,1),
"Salmon"		: (1,0.47,0.62),
"Violet"		: (0.21,0.12,1),
"Yellow"		: (1,1,0),
"Apricot"		: (1,0.68,0.48),
"Emerald"		: (0,1,0.5),
"Fuchsia"		: (0.45,0.01,0.92),
"Magenta"		: (1,0,1),
"SkyBlue"		: (0.38,1,0.88),
"Thistle"		: (0.88,0.41,1),
"BrickRed"		: (0.72,0,0),
"Cerulean"		: (0.06,0.89,1),
"Lavender"		: (1,0.52,1),
"Mahogany"		: (0.65,0,0),
"Mulberry"		: (0.64,0.08,0.98),
"NavyBlue"		: (0.06,0.46,1),
"SeaGreen"		: (0.31,1,0.5),
"TealBlue"		: (0.12,0.98,0.64),
"BlueGreen"		: (0.15,1,0.67),
"CadetBlue"		: (0.38,0.43,0.77),
"Dandelion"		: (1,0.71,0.16),
"Goldenrod"		: (1,0.9,0.16),
"LimeGreen"		: (0.5,1,0),
"OrangeRed"		: (1,0,0.5),
"PineGreen"		: (0,0.75,0.16),
"RawSienna"		: (0.55,0,0),
"RedOrange"		: (1,0.23,0.13),
"RedViolet"		: (0.59,0,0.66),
"Rhodamine"		: (1,0.18,1),
"RoyalBlue"		: (0,0.5,1),
"RubineRed"		: (1,0,0.87),
"Turquoise"		: (0.15,1,0.8),
"VioletRed"		: (1,0.19,1),
"Aquamarine"		: (0.18,1,0.7),
"BlueViolet"		: (0.1,0.05,0.96),
"DarkOrchid"		: (0.6,0.2,0.8),
"OliveGreen"		: (0,0.6,0),
"Periwinkle"		: (0.43,0.45,1),
"Bittersweet"		: (0.76,0.01,0),
"BurntOrange"		: (1,0.49,0),
"ForestGreen"		: (0,0.88,0),
"GreenYellow"		: (0.85,1,0.31),
"JungleGreen"		: (0.01,1,0.48),
"ProcessBlue"		: (0.04,1,1),
"RoyalPurple"		: (0.25,0.1,1),
"SpringGreen"		: (0.74,1,0.24),
"YellowGreen"		: (0.56,1,0.26),
"MidnightBlue"		: (0,0.44,0.57),
"YellowOrange"		: (1,0.58,0),
"CarnationPink"		: (1,0.37,1),
"CornflowerBlue"	: (0.35,0.87,1),
"WildStrawberry"	: (1,0.04,0.61),
}

# vim: ts=4 sw=4
