import re
import  requests
expression=raw_input("input expression eg What time is it in London? : ")
print expression
data=requests.get("http://api.wolframalpha.com/v2/query?input={}&appid=APLTT9-9WG78GYE65".format(expression)).text
for line in  re.findall('plaintext>(.*?)</plaintext>\n',data):
	print line




