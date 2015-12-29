import urllib
import urllib.request
import xml.etree.ElementTree as ET # http://stackoverflow.com/questions/15442130/python-xml-parsing-for-wolfram-api

f=open('wolfram_app_id','r')
appid=f.read()
f.close()
appid=appid.rstrip() # http://effbot.org/pyfaq/is-there-an-equivalent-to-perl-s-chomp-for-removing-trailing-newlines-from-strings.htm

xml_data=urllib.request.urlopen("http://api.wolframalpha.com/v2/query?input=sqrt+2&appid=APLTT9-9WG78GYE65").read()
root = ET.fromstring(xml_data)

for pod in root.findall('.//pod'):
    print(pod.attrib['title'])
    for pt in pod.findall('.//plaintext'):
        if pt.text:
            print('-', pt.text)

