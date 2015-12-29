import wolframalpha # https://pypi.python.org/pypi/wolframalpha

f=open('wolfram_app_id','r')
appid=f.read()
f.close()
appid=appid.rstrip() # http://effbot.org/pyfaq/is-there-an-equivalent-to-perl-s-chomp-for-removing-trailing-newlines-from-strings.htm

client = wolframalpha.Client(appid) # http://products.wolframalpha.com/api/documentation.html


