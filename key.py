import json,re

t = json.load(open("outputs.json","r"))
k = "!stockx jordan 1 mid smoke grey -gs -kids -shabi"
kw = re.findall(r"-(\w+)",k)
#["gs","kids","shabi"]
def filter(n,kw):
	match = None
	if any(re.findall(k.lower(),n.lower()) for k in kw):
		match = False
	else:
		match = True
	return match	
for index,i in enumerate(t["hits"]):
	#print(i["name"])
	j = mat(i["name"],kw)
	if j:
		print(i["name"])
		z = index

p = t["hits"][z]
print(p)

