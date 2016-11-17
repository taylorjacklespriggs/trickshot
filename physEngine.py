from __future__ import division
from Tkinter import *
from physicsObjects import *
from physics import *
from random import *
from time import *

class physEngine(object):
	def __init__(self):
		self.root=Tk()
		self.root.title('Phys Engine 1.0')
		self.root.geometry('800x800')
		self.canvas=Canvas(self.root,height=800,width=800)
		self.canvas.pack()
		self.canvas.bind('<Button-1>',self.createCircle)
		self.boundaries=[border([0,0],[0,800]),border([0,800],[800,800]),\
		border([800,800],[800,0]),border([800,0],[0,0])]
		self.dt=int(1000/120)
		self.r=60
		self.slowTime=1
		self.physObjects={}
		self.collisions=[]
		self.ti=time()
		self.root.after(self.dt,self.move)
		self.root.mainloop()

	def move(self):
		if len(self.physObjects.keys())>0:
			items=self.physObjects.keys()
			for z in items:
				for t in self.boundaries:
					if self.physObjects[z].checkCollision(t):
						self.ti=time()
						self.collisions.append((self.physObjects[z],t))
			for z in range(len(items)):
				for t in items[z+1:]:
					if self.physObjects[items[z]].\
					checkCollision(self.physObjects[t]):
						self.ti=time()
						self.collisions.append((self.physObjects[items[z]],\
						self.physObjects[t]))
		self.collision()
		for z in self.physObjects.keys():
			self.physObjects[z].move()
			x,y=self.physObjects[z].pos
			self.canvas.coords(z,x-self.r,y-self.r,x+self.r,y+self.r)
		self.root.after(self.dt,self.move)

	def collision(self):
		x=0
		while time()-self.ti<self.dt/1000 and self.collisions!=[]:
			x+=1
			objects=set()
			for a,b in self.collisions:
				a.collide(b)
				objects.add(a)
				objects.add(b)
			for obj in objects:
				obj.move()
		self.collisions=[]
		#print x

	def createCircle(self,event):
		self.physObjects[self.canvas.create_oval(event.x-self.r,event.y-self.r,\
		event.x+self.r,event.y+self.r,fill='#%s%s%s'%(\
		hex(randint(30,255))[-2:],hex(randint(30,255))[-2:],\
		hex(randint(30,255))[-2:]))]=circle([event.x,event.y],self.r,\
		acceleration=[0,1000],hard=0.1,cElastic=1000)

physEngine()