#################################################
# These tools were built by Taylor Jackle Spriggs
#################################################
from __future__ import division
from math import *
from physics import *
from time import *

class physObject(object):
	def __init__(self,pos,velocity=[0,0],acceleration=[0,0],angle=0,angV=0,\
	angA=0,mass=1.0,cFriction=0.5,cDrag=0.5,cElastic=1000.0,hard=0.1):
		self.pos=list(pos)
		self.velocity=list(velocity)
		self.constantAcceleration=list(acceleration)
		self.angle=angle
		self.mass=mass
		self.cFriction=cFriction
		self.cDrag=cDrag
		self.cElastic=cElastic
		self.hard=hard
		self.acceleration=list(self.constantAcceleration)
		self.netForce=[0,0]
		self.t=time()

	def addForce(self,f):
		self.netForce=vectAdd(f,self.netForce)

	def move(self):
		dt=time()-self.t
		if dt==0:
			dt=0.0001
		self.t=time()
		m=self.mass
		self.acceleration=vectAdd(vectMult(self.netForce,1/m),self.acceleration)
		self.pos=vectDisplacement(self.pos,self.velocity,self.acceleration,dt)
		self.velocity=vectVelocity(self.velocity,self.acceleration,dt)
		self.collisionRadius=vectDisplacement([self.radius],\
		[length(self.velocity)],[length(self.acceleration)],dt)
		self.acceleration=list(self.constantAcceleration)
		self.netForce=[0,0]

	def collide(self,other): other.collide(self)

	def getNormal(self,other):
		return vectDelta(other.pos,self.pos)

	def getVertex(self,other):
		try:
			dpos=vectDelta(self.pos,other.pos)
			r=length(dpos)
			return vectAdd(vectMult(dpos,self.radius/r),self.pos)
		except ZeroDivisionError:
			self.pos=vectAdd(self.pos,[1,1])
			return self.getVertex(other)


class circle(physObject):
	def __init__(self,pos,radius,velocity=[0,0],acceleration=[0,0],angle=0,\
	angV=0,angA=0,mass=1.0,cFriction=0.1,cDrag=0.5,cElastic=800.0,hard=0.7):
		super(circle,self).__init__(pos,velocity,acceleration,angle,angV,angA,\
		mass,cFriction,cDrag,cElastic,hard=hard)
		self.radius=radius
		self.collisionRadius=self.radius

	def checkCollision(self,other):
		if length(vectDelta(self.pos,other.getVertex(self)))<=self.radius:
			return True
		return False

	def collide(self,other):
		vert=other.getVertex(self)
		dpos=vectDelta(self.pos,vert)
		r=length(dpos)
		if r-self.radius>0:
			pass
		else:
			try:
				normal=other.getNormal(self)
				if dot(dpos,normal)<0:
					X=self.radius+r
				else: X=self.radius-r
				f=vectMult(dpos,2*self.cElastic*other.cElastic*X/r/\
				(self.cElastic+other.cElastic))
				deltaV=vectDelta(self.velocity,other.velocity)
				vnorm=proj(deltaV,normal)
				vfric=vectDelta(vnorm,deltaV)
				mult=-2*atan(dot(vnorm,normal)/length(normal))/pi+1
				power=-log(self.hard*other.hard)
				mult2=-log(1-(X/self.radius/2)**3)-(X/self.radius/2)**3+1
				f=vectMult(f,mult**power*mult2)
				#print mult,power
				self.addForce(vectMult(f,-1))
				other.addForce(f)
				#print 'Normal velocity is [%.1f,%.1f] and force is [%.1f,%.1f]'\
				#%(vnorm[0],vnorm[1],f[0],f[1])
				try:
					friction=vectMult(vfric,length(perp(f))*\
					self.cFriction*other.cFriction/length(vfric))
					self.addForce(friction)
					other.addForce(vectMult(friction,-1))
					#print vfric
				except ZeroDivisionError: pass
			except SyntaxError:
				self.pos=vectAdd(self.pos,[1,1])
				self.collide(other)


class border(physObject):
	def __init__(self,pos,pos2,cFriction=0.3,cElastic=100000.0,hard=0.9):
		super(border,self).__init__(pos=vectMult(vectAdd(pos,pos2),1/2),\
		velocity=[0,0],acceleration=[0,0],angle=None,angV=None,angA=None,\
		mass=None,cFriction=cFriction,cDrag=None,cElastic=cElastic,hard=hard)
		self.point1=list(pos)
		self.point2=list(pos2)
		self.normal=perp(vectDelta(self.point1,self.point2))

	def move(self): pass

	def getVertex(self,other):
		point=intersect(other.pos,self.normal,self.point1,\
		vectDelta(self.point1,self.point2))
		if checkBounds(point,self.point1,self.point2):
			return point
		else: return self.point1

	def getNormal(self,other):
		return self.normal


class stuckCircle(circle):
	def __init__(self,pos,radius,cFriction=0.3,cElastic=100000.0,hard=0.9):
		super(stuckCircle,self).__init__(pos=pos,radius=radius,velocity=[0,0],\
		acceleration=[0,0],angle=None,angV=None,angA=None,mass=None,\
		cFriction=cFriction,cDrag=None,cElastic=cElastic,hard=hard)

	def move(self): pass

'''class vanishCircle(circle):
	def __init__(self,pos,radius,velocity=[0,0],acceleration=[0,0],angle=0,\
	angV=0,angA=0,mass=1.0,cFriction=0.1,cDrag=0.5,cElastic=800.0,hard=0.7):
		super(vanishCircle,self).__init__(pos=pos,radius=radius,velocity=[0,0],\
		acceleration=[0,0],angle=angle,angV=angV,angA=angA,mass=mass,\
		cFriction=cFriction,cDrag=cDrag,cElastic=cElastic,hard=hard)
		self.exist=True

	def move(self): pass

	def collide(self,other):
		if self.exist:
			other.velocity=vectMult(vectAdd(vectMult(self.velocity*self.mass),\
			vectMult(other.velocity*other.mass)),1/(self.mass+other.mass))
			self.exist=False'''


