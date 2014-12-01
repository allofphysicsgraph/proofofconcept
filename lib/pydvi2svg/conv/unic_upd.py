# utility to produce/update unicode.py 

import findfile
import xml.dom.minidom as dom

d = {}
for filename in findfile.find_all_files('fonts', lambda p,f: f.endswith('.svg')):
	print "Processing", filename

	doc = dom.parse(filename)
	for glyph in doc.getElementsByTagName('glyph'):
		name = glyph.getAttribute('glyph-name')
		if not name:
			continue

		unic = glyph.getAttribute('unicode')
		if name not in d:
			d[name] = [unic]
		else:
			if unic not in d[name]:
				d[name].append(unicode)
				print "duplicated '%s'" % name
	#rof
#rof

f = open('tmp', 'w');
for name, unic in d.iterkeys():
	f.write(" '%s'\t: %s\n" % (name, repr(unic[0])))
f.close
