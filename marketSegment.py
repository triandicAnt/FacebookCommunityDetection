import sys
import os
import igraph as ig
from igraph import *
from itertools import izip
import csv
import numpy as np 
import time
from scipy import spatial

alpha = 0
g= ig.Graph.Read_Ncol('./data/fb_caltech_small_edgelist.txt',directed=False)
#ig.plot(g)
edgeList = []
#print summary(g)
for e in g.es:
	edgeList.append(e.tuple)
#print edgeList

vertices = []
dict = {}
for v in g.vs:
	vertices.append(int(v["name"]))
	dict[int(v["name"])] = v
# print sorted(vertices)

attrList = []
i=0
file = open('./data/fb_caltech_small_attrlist.csv')
reader = csv.reader(file)
header = reader.next()
noOfAttrs = header
# print header
for row in reader:
	attrList.append(row)
	for attrName, attrVal in izip(header,row):
		g.vs[i][attrName] = attrVal
	i=i+1	
# print attrList	
# print g.vs[1]

# calculate cosine similarity of graph matrix
# Cosine Similarity (d1, d2) =  Dot product(d1, d2) / ||d1|| * ||d2||
# ref : https://janav.wordpress.com/2013/10/27/tf-idf-and-cosine-similarity/
sim = []
def getSimilarityMatrix():
	for i in range(0,len(vertices)):
		temp = []
		for j in range(0,len(vertices)):
			# temp.append(cosineSimilarity(dict[i],dict[j]))
			temp.append(spatial.distance.cosine(np.array(attrList[i],dtype=int), np.array(attrList[j],dtype=int)))
		sim.append(temp)

def getDotProduct(v1,v2):
	sum =0
	for i in noOfAttrs:
		sum = sum + int(v1[i])*int(v2[i])
	return sum

def getModOfVertexAttr(v):
	sum = 0
	for i in noOfAttrs:
		sum = sum + math.pow(int(v[i]),2)
	return sum		

def cosineSimilarity(v1,v2):
	# dotProduct = getDotProduct(v1,v2)
	# modv1 = getModOfVertexAttr(v1)
	# modv2 = getModOfVertexAttr(v2)
	dot = 0
	mod1 = 0
	mod2 = 0
	for i in noOfAttrs:
		mod1 = mod1 + math.pow(int(v1[i]),2)
		mod2 = mod2 + math.pow(int(v2[i]),2)
		dot = dot + int(v1[i])*int(v2[i])
	consineSim = dot/(mod1*mod2)
	return consineSim
def findSimilarity(idx,mem,val):
	matchings_indices = [ i for i, x in enumerate(mem) if x == val ]
	print(matchings_indices)
	l = len(matchings_indices)
	sum = 0
	for n in matchings_indices:
		sum = sum + sim[idx][matchings_indices[n]]
	return sum	

# calculate QNewman
def getQAttrDiff(idx):
	qarrt = 0
	for i in vertices:
		qarrt = qarrt + cosineSimilarity(dict[idx],dict[i])
	return qarrt	
	
def delQAttrCalculate(idx, c_list):
	sum = 0
	for i in c_list:
		sum = sum + sim[idx][i]
	return sum
	
compare = lambda a,b: len(a)==len(b) and len(a)==sum([1 for i,j in zip(a,b) if i==j])
membership = range(0,len(vertices))
communities= {node:[node] for node in vertices}
def algorithm():
	# print noOfAttrs
	# print g.get_adjlist()
	x = 1
	for m in range(0,15):
		x = x +1
		print x
		old_m = list(membership)
		print old_m
		for i in range(0,len(vertices)):
		# for i in range(0,5):	
			QNewman_Old = g.modularity(np.array(membership))
			max = -5
			index = i
			mem_ini = membership[i]
			# print QNewman_Old
			ts = time.time()
			# print ts
			cl_list = list(Clustering(membership))
			for j in range(0,len(vertices)):
				if i!=j:
					if len(cl_list[membership[j]]) > 0:
						membership[i] = membership[j]
						QNewman_new = g.modularity(np.array(membership))
						qarrt = delQAttrCalculate(j, cl_list[membership[j]])
						qarrt = qarrt/(len(cl_list[membership[j]])*len(cl_list[membership[j]]))
						qarrt = qarrt/len(set(membership))
						# qarrt = findSimilarity(i,membership,membership[j])
						delQNew = (QNewman_new-QNewman_Old)
						delQAttr = alpha*delQNew + (1-alpha)*qarrt
						# print delQAttr
						if delQAttr>max:
							index = j
							max = delQAttr
			if 	max > 0:
				membership[i] = membership[index]
			else:
				membership[i] = mem_ini
			cl_list = list(Clustering(membership))
			# print cl_list				
			# print ts	
		print membership
		# print membership	
		if compare(old_m,membership) == True:
			print "Breaking Bad!"
			break
	d=0		
	for x in list(Clustering(membership)):
		if len(x)!=0:
			d = d+1
			print x
			print d
	# a = g.clusters
def phase2():
	algorithm()
	g2 = g.contract_vertices(membership)
	print g2.vs

def main():
	getSimilarityMatrix()
	# print sim
	phase2()
# display some lines

if __name__ == "__main__": main()		

