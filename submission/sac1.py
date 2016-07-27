import sys
import os
import igraph as ig
from igraph import *
from itertools import izip
import csv
import numpy as np 
import time
from scipy import spatial
import scipy
from sklearn.metrics.pairwise import cosine_similarity
import itertools

g = Graph.Read_Edgelist('data/fb_caltech_small_edgelist.txt', directed=False)
# g= ig.Graph.Read_Ncol('./data/fb_caltech_small_edgelist.txt',directed=False)

arg_list = sys.argv
if len(arg_list)<=0 or len(arg_list)>2:
	print "Invalid number of arguments."
	sys.exit(0)
global alpha
alpha = int(arg_list[1])
# alpha = 0
attrList = []
with open("data/fb_caltech_small_attrlist.csv") as fileCSV:
	reader = csv.reader(fileCSV)
	attrList = list(reader)[1:]

edgeList = []
edgeList = g.get_edgelist()

vertices = g.vcount()

membership = []
for v in range(0,g.vcount()):
	membership.append(v)


communities = list(Clustering(membership))

def simplifyMembership(membership):
	dict = {}
	ml = []
	i=0
	for j in membership:
		if j in dict.keys():
			ml.append(dict[j])
		else:
			ml.append(j)
			dict[j] = i
			i+=1
	return ml

def refreshCommunities(c1,c2):
	r = []
	for i in c2:
		temp = []
		for j in i:
			temp.append(c1[j])
		r.append(temp)
	return r

def getSimMatrix ():
	# sim = np.zeros(shape=(len(attrList),len(attrList)))
	sim = [[0]*len(attrList)]*len(attrList)
	for i in range(len(attrList)):
		for j in range(len(attrList)):
			# print cosine_similarity(attrList[i],attrList[j])[0][0]
			sim[i][j] = (cosine_similarity(attrList[i],attrList[j])[0][0]).reshape(1,-1)
	return sim			

def getSimilarityMatrix():
	sim = []
	for i in range(0,vertices):
		temp = []
		for j in range(0,vertices):
			# temp.append(cosineSimilarity(dict[i],dict[j]))
			temp.append(spatial.distance.cosine(np.array(attrList[i],dtype=int), np.array(attrList[j],dtype=int)))
		sim.append(temp)
	return sim	

def updateSimMatrix (newNodes, sim):
	newSim = [[0]*len(newNodes)]*len(newNodes)
	for n1,i in enumerate(newNodes):
		for n2 ,j in enumerate(newNodes):
			temp =0
			count = 0
			for k in i:
				for l in j:
					temp+=sim[k][l]
					count+=1
			newSim[n1][n2] = temp
	return newSim				

global sim 
sim = getSimMatrix()
copy_sm = sim

def phase1(membership):
	ver = len(set(membership))
	for k in range(15):
		print k
		for i in range(ver):
			m_g = 0.0
			old_newman = g.modularity(membership)
			del_newman = 0.0
			max = -1
			temp = membership[i]
			for j in range(ver):
				if (j!=i) and membership[i]!=membership[j]:
					membership[i] = membership[j]
					new_newman = g.modularity(membership)
					del_newman = new_newman - old_newman
					delattr = 0.0
					x = 0
					for k in membership:
						if(k==membership[j]):
							x+=1
					for v, e in enumerate(membership):
						if(membership[j]==e):
							delattr+=sim[i][v]
					delattr/=x**2
					delattr/=len(set(membership))
					delQ = alpha*del_newman+(1-alpha)*delattr
					if delQ>m_g:
						m_g = delQ				
						max = j
					membership[i] = temp
			if m_g >0 and max >1:
				membership[i] = membership[max]
	return membership
	
def phase2(c, membership):
	membership = simplifyMembership(membership)
	g.contract_vertices(membership)
	g.simplify(multiple = True)
	c1 = list(Clustering(membership))
	c = refreshCommunities(c,c1)

	sim	= updateSimMatrix(c1,copy_sm)
	vertices = g.vcount()
	membership = []
	for i in range(vertices):
		membership.append(i)
	# membership = [j for j in ]	
	return membership		

# def setDefaults():
membership = phase1(membership)
membership = phase2(communities,membership)
membership = phase1(membership)
membership = simplifyMembership(membership)
communities = list(Clustering(membership))
file = open("communities.txt", "w+")
for l in list(g.clusters()):
		if len(g.clusters())!=0:
			file.write("\n".join(str(x)+"," for x in l))
file.close()

def main():
	# sim = getSimilarityMatrix()
	# print sim
	if __name__ == "__main__": main()		

