import linecache 
import sys

score = 0
E = []
P = [0.224, 0.249]
i=1
for arg in sys.argv[1:]:
	if linecache.getline(sys.argv[i], 2).split(" ")[4].split(",")[0].split(",").pop(0) == "":
		E.append(float(linecache.getline(sys.argv[i], 2).split(" ")[5].split(",")[0].split(",").pop(0)))
	else:
     		linecache.getline(sys.argv[i], 2).split(" ")[4].split(",")[0].split(",").pop(0)
		E.append(float(linecache.getline(sys.argv[i], 2).split(" ")[4].split(",")[0].split(",").pop(0)))
	print score, " + (", E[i-1], " * ", P[i-1], ") = ", score + E[i-1] * P[i-1]
	score = score + (E[i-1] * P[i-1])
	i = i + 1

f = open('score.txt', 'w')
f.write(str(score))
