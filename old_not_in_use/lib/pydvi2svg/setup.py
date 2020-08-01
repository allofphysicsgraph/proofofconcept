from os.path import dirname, join

def path(p):
	return join(dirname(__file__), p)
	
encoding_path	= path('enc/')
tex_paths	= ['/usr/share/texmf/', '/usr/share/texmf-tetex']

svg_font_path	= path('fonts/')
cache_path	= path('cache/')
font_lookup	= path('enc/font.info')
enc_lookup	= path('enc/enc.info')

class Options: pass
options = Options()

del path 
