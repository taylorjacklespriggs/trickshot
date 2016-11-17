#################################################
# These tools were built by Taylor Jackle Spriggs
#################################################
from __future__ import division

def smaller(*args):
	return sorted(args)[0]

def length(vect):
	return reduce(lambda x,y:x+y,[z**2 for z in vect])**0.5

def dot(vect1,vect2):
	pot=0
	for x in range(len(vect1)):
		if x<len(vect2): pot+=vect1[x]*vect2[x]
	return pot

def perp(v):
	return [-v[1],v[0]]

def vectDisplacement(d,v,a,t):
	ret=[]
	for x in range(len(d)):
		ret.append(d[x]+v[x]*t+a[x]*t**2/2)
	return ret

def vectVelocity(v,a,t):
	ret=[]
	for x in range(len(v)):
		ret.append(v[x]+a[x]*t)
	return ret

def vectAdd(*args):
	s=[0 for z in range(len(args[0]))]
	for x in args:
		for y in range(len(x)):
			s[y]+=x[y]
	return s

def vectMult(vect,mult):
	return [x*mult for x in vect]

def matrixMult(mat1,mat2):
	ret=[[0 for columns in range(len(mat2[0]))] for rows in range(len(mat1))]
	for row in range(len(ret)):
		for column in range(len(ret[0])):
			ret[row][column]=dot(mat1[row],[mat2[x][column]\
			for x in range(len(mat2))])
	return ret

def vectDelta(a,b):
	return vectAdd(b,vectMult(a,-1))

def intersect(p1,d1,p2,d2):
	dp=vectDelta(p1,p2)
	if dp[0]*d1[1]-dp[1]*d1[0]!=0:
		s=(dp[0]*d1[1]-dp[1]*d1[0])/(d2[1]*d1[0]-d2[0]*d1[1])
		inter=vectAdd(p2,vectMult(d2,s))
	elif dp[0]*d2[1]-dp[1]*d2[0]!=0:
		s=(dp[0]*d2[1]-dp[1]*d2[0])/(d1[1]*d2[0]-d1[0]*d2[1])
		inter=vectAdd(p1,vectMult(d1,s))
	else: return 'no solution'
	return inter

def vectDir(v):
	return vectMult(v,1/length(v))

def proj(v1,v2):
	return vectMult(v2,dot(v1,v2)/length(v2)**2)

def checkBounds(point,pos1,pos2):
	for x in range(len(point)):
		if pos1[x]>pos2[x]:
			if point[x]<pos2[x]: return False
			elif point[x]>pos1[x]: return False
		else:
			if point[x]>pos2[x]: return False
			elif point[x]<pos1[x]: return False
	else: return True
