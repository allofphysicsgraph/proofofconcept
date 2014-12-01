# -*- coding: iso-8859-2 -*-
# $Id: __init__.py,v 1.6 2007-03-13 21:03:19 wojtek Exp $
#
# SVGfrags - auxilary functions & classes
#
# license: BSD
#
# author: Wojciech Muła
# e-mail: wojciech_mula@poczta.onet.pl
# WWW   : http://wmula.republika.pl/

# changelog
"""
13.03.2007
	+ istextnode
	+ get_text
	+ get_anchor
10.03.2007
	+ remove_file
	+ Dict
	+ CSS_value
 9.03.2007
	+ safe_float
	+ get_bbox/get_width/get_height
	+ collect_Id
"""

import os

def safe_float(string, default=0.0):
	try:
		return float(string)
	except ValueError:
		return default
	

def remove_file(filename):
	try:
		os.remove(filename)
	except OSError, error:
		if error.errno != 2: # 2 is file not found (we pass it silently)
			raise error
		

def get_bbox(object):
	"Returns BBox of given object (rect/circle/ellipse are supported)"

	tag = object.tagName

	def safe_get(object, attribute):
		return safe_float(object.getAttribute(attribute))
	if tag == 'rect':
		Xmin = safe_get(object, 'x')
		Ymin = safe_get(object, 'y')
		Xmax = Xmin + safe_get(object, 'width')
		Ymax = Ymin + safe_get(object, 'height')
	elif tag == 'circle':
		cx = safe_get(object, 'cx')
		cy = safe_get(object, 'cy')
		rx = ry = safe_get(object, 'r')

		Xmin = cx - rx
		Ymin = cy - ry
		Xmax = cx + rx
		Ymax = cy + ry

	elif tag == 'ellipse':
		cx = safe_get(object, 'cx')
		cy = safe_get(object, 'cy')
		rx = safe_get(object, 'rx')
		ry = safe_get(object, 'ry')

		Xmin = cx - rx
		Ymin = cy - ry
		Xmax = cx + rx
		Ymax = cy + ry
	else:
		raise ValueError("Can't deal with tag <%s>" % tag)

	return (Xmin, Ymin, Xmax, Ymax)


def get_width(object):
	"Returns width of object"
	xmin, ymin, xmax, ymax = get_bbox(object)
	return xmax-xmin


def get_height(object):
	"Returns width of object"
	xmin, ymin, xmax, ymax = get_bbox(object)
	return ymax-ymin


def collect_Id(XML, d={}):
	# hack
	for object in XML.childNodes:
		try:
			v = object.getAttribute('id')
			if v: d.update([(v, object)])
		except AttributeError: # no hasAttr
			pass
		collect_Id(object, d)


def istextnode(node):
	try:
		return node.nodeName == 'text'
	except AttributeError:
		return False


def get_text(node, strip=False):
	if node.nodeName != 'text':
		raise ValueError("Not a text node")
	
	# use only raw text
	if len(node.childNodes) != 1:
		raise ValueError("Text node has more then one child.")
		
	# one tspan is allowed
	if node.firstChild.nodeType == node.ELEMENT_NODE and \
	   node.firstChild.tagName == 'tspan':
		textitem = node.firstChild
	else:
		textitem = node

	# text node needed
	if textitem.firstChild.nodeType != node.TEXT_NODE:
		raise ValueError("Text node has no raw-text child.")

	# strip whitespaces (if enabled)
	if strip:
		return textitem.firstChild.wholeText.strip()
	else:
		return textitem.firstChild.wholeText


def get_anchor(node):
	val = node.getAttribute("text-anchor") or \
	      CSS_value(node, "text-anchor")
	
	px_lookup = {"start": 0.0, "middle": 0.5, "end": 1.0}
	return px_lookup.get(val, 0.0) # default: "start"


def CSS_value(object, property):
	css_string = object.getAttribute('style')
	for pair in css_string.split(';'):
		prop, value = pair.split(':', 2)
		if prop.strip() == property:
			return value.strip()


class Dict(dict):
	"Ocaml-like dict"
	def __setitem__(self, key, value):
		try:
			L = super(Dict, self).__getitem__(key)
		except KeyError:
			L = []
			super(Dict, self).__setitem__(key, L)

		L.append(value)

# vim: ts=4 sw=4 noexpandtab nowrap
