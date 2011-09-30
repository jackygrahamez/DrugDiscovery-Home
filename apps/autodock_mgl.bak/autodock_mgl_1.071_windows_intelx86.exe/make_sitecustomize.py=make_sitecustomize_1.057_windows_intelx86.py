import sys
for path in sys.argv[1:]:
	mglroot = path
list=[]
list.append("# specify mglroot here")
list.append("import sys, os")
list.append("path = os.path.join(\"" + mglroot + "\", \"MGLToolsPckgs\")")
list.append("sys.path.insert(0,path)")
list.append("")
list.append("from Support.path import setSysPath")
list.append("setSysPath(path)")
list.append("#sys.path.insert(0,'.')")
index=0
while index<len(list):
	list[index]=list[index]+"\n"
	index+=1
file = open(mglroot + "\Python25\Lib\sitecustomize.py","w")
file.writelines(list)
file.close()

while index<len(list):
	list[index]=list[index]+"\n"
	index+=1
file = open(mglroot + "\MGLToolsPckgs\Support\sitecustomize.py","w")
file.writelines(list)
file.close()

