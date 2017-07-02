import re
f=open('test')
g=open('ast_output','w')
data=f.read()
for item in re.split('\s{2,}',data):
    match=re.findall('^<.*|label.*',item)
    if len(match)>0:
        g.write(match[0])
        
    
g.close()

h=open('ast_output')
data_2=h.read()

data_3=re.sub('_ast.|object at','',data_2)

data_4=re.sub(',<','\n<',data_3)

print(data_4)


i=open('parsed_ast_output','w')
i.write(data_4)
i.write('\n')
for label in re.findall('label.*',data_4):
	print(label)
	i.write(label)
	i.write('\n')

i.close()
