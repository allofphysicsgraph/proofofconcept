import re
import  requests
print("input a query")
expression=input()
print(expression)
data=requests.get("http://api.wolframalpha.com/v2/query?input={}&appid=APLTT9-9WG78GYE65".format(expression)).text
for line in  re.findall('plaintext>(.*?)</plaintext>\n',data):
	print(line)




