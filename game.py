from __future__ import division
from Tkinter import *
from physicsObjects import *
from physics import *
from random import *
from time import *
from tkMessageBox import *

class physEngine(object):
	def __init__(self):
		self.root=Tk()
		self.root.title('TrickShot Basketball')
		self.root.geometry('800x800')
		self.canvas=Canvas(self.root,height=800,width=800)
		self.canvas.pack()
		self.basketball=PhotoImage(file='assets/Basketball_large.gif')
		self.netFront=PhotoImage(file='assets/netFront.gif')
		self.netBack=PhotoImage(file='assets/netBack.gif')
		self.backboard=PhotoImage(file='assets/backboard.gif')
		self.boundaries=[border([0,0],[0,800]),border([0,800],[800,800]),\
		border([800,800],[800,0]),border([800,0],[0,0])]
		self.dt=int(1000/120)
		self.r=50
		self.acceleration=[0,1500]
		self.slowTime=1
		self.physObjects={}
		self.collisions=[]
		self.ti=time()
		self.maxVelocity=1500
		self.gameMode='m'
		self.clickFunctions={'m':lambda x:None,'g':self.startMoveBasketball,\
		'e':lambda x:None}
		self.dragFunctions={'m':lambda x:None,'g':self.moveBasketball,\
		'e':lambda x:None}
		self.releaseFunctions={'m':self.checkMenu,'g':self.releaseBall,\
		'e':self.checkMenu}
		self.goals=0
		self.inBasket=False
		self.menu()
		self.canvas.bind('<Button-1>',lambda x:\
		self.clickFunctions[self.gameMode](x))
		self.canvas.bind('<B1-Motion>',lambda x:\
		self.dragFunctions[self.gameMode](x))
		self.canvas.bind('<ButtonRelease-1>',lambda x:\
		self.releaseFunctions[self.gameMode](x))
		self.root.after(self.dt,self.move)
		self.root.mainloop()

	def checkGoal(self):
		a,b=self.netPos
		aTop=[a[0],a[1]-100]
		bTop=b
		aBottom=a
		bBottom=[b[0],b[1]+100]
		try:
			if checkBounds(self.physObjects[self.basketID].pos,aTop,bTop):
				self.inBasket=True
			elif self.inBasket and checkBounds(\
			self.physObjects[self.basketID].pos,aBottom,bBottom):
					self.goals+=1
					self.inBasket=False
			else: self.inBasket=False
		except: pass

	def checkMenu(self,event):
		a1,b1=self.startBox
		a2,b2=self.quitBox
		if checkBounds([event.x,event.y],a1,b1):
			self.endMenu()
			self.totalGoals=0
			self.level1()
		elif checkBounds([event.x,event.y],a2,b2):
			if askyesno('Are you sure?',message='Do you really want to exit?'):
				self.root.destroy()

	def click(self,event):
		self.clickFunctions[self.gameMode](event)

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

	def createBasketball(self,x,y):
		self.canvas.coords(self.basketID,x-self.r,y-self.r)
		self.physObjects[self.basketID]=circle([x,y],self.r,\
		acceleration=self.acceleration,hard=0.85,cFriction=0.1,cElastic=1200)

	def createBoard(self,x,y):
		self.backboardID=(self.canvas.create_image(x-100,y-200,\
		image=self.backboard,anchor=NW))
		self.boundaries.append(stuckCircle([x-60,y],5))
		self.boundaries.append(stuckCircle([x+55,y],5))
		self.netPos=[x-60,y],[x+55,y]
		self.netbackID=(self.canvas.create_image(x-60,y-15,\
		image=self.netBack,anchor=NW))

	def createNet(self,x,y):
		self.netfrontID=(self.canvas.create_image(x-60,y-15,\
		image=self.netFront,anchor=NW))

	def dropBall(self):
		self.createBasketball(0,0)
		self.drag=False

	def endLevel(self):
		eval('self.endLevel%d()'%self.currentLevel)

	def endTimer(self):
		self.canvas.delete(self.timeID)

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
			try:
				self.canvas.coords(z,x-self.physObjects[z].radius,y-\
				self.physObjects[z].radius)
			except TclError:
				self.canvas.coords(z,x-self.physObjects[z].radius,y-\
				self.physObjects[z].radius,x+self.physObjects[z].radius,y+\
				self.physObjects[z].radius)
		if self.gameMode=='g':
			self.checkGoal()
			if self.updateTime()<=0 or self.tries>self.maxTries:
				self.totalGoals+=self.goals
				if self.goals>=self.minGoals:
					self.goals=0
					self.nextLevel()
				else:
					self.goals=0
					self.endLevel()
					self.gameOver()
		self.root.after(self.dt,self.move)

	def moveBasketball(self,event):
		a,b=self.shootBox
		if checkBounds([event.x,event.y],a,b) and self.drag:
			self.canvas.coords(self.basketID,event.x-self.r,event.y-self.r)
		elif self.drag: self.releaseBall(event)

	def nextLevel(self):
		eval('self.endLevel%d()'%self.currentLevel)
		if self.currentLevel>=6:
			self.gameOver()
		else:
			self.currentLevel+=1
	        eval('self.level%d()'%self.currentLevel)

	def rectBound(self,p1,p2):
		x1,y1=p1
		x2,y2=p2
		bounds=[]
		bounds.append(border([x1,y1],[x2,y1]))
		bounds.append(border([x2,y1],[x2,y2]))
		bounds.append(border([x2,y2],[x1,y2]))
		bounds.append(border([x1,y2],[x1,y1]))
		bounds.append(stuckCircle([x1,y1],10))
		bounds.append(stuckCircle([x2,y1],10))
		bounds.append(stuckCircle([x2,y2],10))
		bounds.append(stuckCircle([x1,y2],10))
		rectID=self.canvas.create_rectangle(x1,y1,x2,y2,fill='black')
		return bounds,rectID

	def releaseBall(self,event):
		if self.drag:
			self.createBasketball(event.x,event.y)
			dpos=vectDelta(self.p[0],[event.x,event.y])
			dt=time()-self.p[1]
			v=vectMult(dpos,1/dt)
			if length(v)>self.maxVelocity:
				v=vectMult(v,self.maxVelocity/length(v))
			self.physObjects[self.basketID].velocity=v
			self.drag=False

	def startMoveBasketball(self,event):
		a,b=self.shootBox
		if checkBounds([event.x,event.y],a,b):
			self.tries+=1
			self.p=[event.x,event.y],time()
			del self.physObjects[self.basketID]
			self.canvas.coords(self.basketID,event.x-self.r,event.y-self.r)
			self.drag=True
		else: self.drag=False

	def startTimer(self,t):
		self.timeID=self.canvas.create_text(400,700,\
		text='You have %d seconds left'%int(t))
		self.finalTime=time()+t

	def updateTime(self):
		self.canvas.delete(self.timeID)
		self.timeLeft=self.finalTime-time()
		self.timeID=self.canvas.create_text(650,700,\
		text='You have %d seconds left\nYou have scored %d goals out of %d\nYou have %d tries left'\
		%(int(self.timeLeft),self.goals,self.minGoals,self.maxTries-self.tries))
		return self.timeLeft

	def menu(self):
		self.menuItems=[]
		for xNum in range(4):
			for yNum in range(4):
				x=xNum*800/4+100+randint(-10,10)
				y=yNum*800/4+100+randint(-10,10)
				self.physObjects[self.canvas.create_image(x-50,y-50,anchor=NW,\
				image=self.basketball)]=circle([x,y],50,acceleration=\
				[0,1000],hard=0.7)
		self.startBox=[300,300],[500,400]
		self.quitBox=[300,400],[500,500]
		self.menuItems.append(self.canvas.create_rectangle(300,300,500,400))
		self.menuItems.append(self.canvas.create_text(400,150,activefill='red',\
		text='TrickShot\nBasketball',font=('Times',100,'bold'),fill='#FF3D0D'))
		self.menuItems.append(self.canvas.create_text(400,350,activefill='red',\
		text='Start Game'))
		self.menuItems.append(self.canvas.create_rectangle(300,400,500,500))
		self.menuItems.append(self.canvas.create_text(400,450,activefill='red',\
		text='Quit Game'))
	def endMenu(self):
		for x in self.menuItems:
			self.canvas.delete(x)
		for x in self.physObjects.keys():
			self.canvas.delete(x)
		self.physObjects={}
	def level1(self):
		self.gameMode='g'
		self.currentLevel=1
		self.shootBox=[0,400],[400,800]
		self.levelObjects=[]
		self.levelObjects.append(self.canvas.create_rectangle(\
		self.shootBox[0][0],self.shootBox[0][1],self.shootBox[1][0],\
		self.shootBox[1][1],fill='grey'))
		self.createBoard(700,200)
		self.basketID=self.canvas.create_image(200-self.r,200-self.r,\
		image=self.basketball,anchor=NW)
		self.createBasketball(200,200)
		self.createNet(700,200)
		self.minGoals=5
		self.maxTries=26
		self.tries=0
		self.startTimer(40)
	def endLevel1(self):
		self.canvas.delete(self.backboardID)
		self.canvas.delete(self.basketID)
		self.canvas.delete(self.netbackID)
		self.canvas.delete(self.netfrontID)
		for x in self.levelObjects:
			self.canvas.delete(x)
		del self.boundaries[-2:]
		self.dropBall()
		del self.physObjects[self.basketID]
		self.endTimer()
	def level2(self):
		self.gameMode='g'
		self.currentLevel=2
		self.shootBox=[0,400],[300,800]
		self.levelObjects=[]
		self.levelObjects.append(self.canvas.create_rectangle(\
		self.shootBox[0][0],self.shootBox[0][1],self.shootBox[1][0],\
		self.shootBox[1][1],fill='grey'))
		self.createBoard(700,600)
		self.basketID=self.canvas.create_image(200-self.r,200-self.r,\
		image=self.basketball,anchor=NW)
		self.createBasketball(200,200)
		self.createNet(700,600)
		bounds,rectangle=self.rectBound([375,200],[425,800])
		self.boundaries+=bounds
		self.levelObjects.append(rectangle)
		self.minGoals=6
		self.maxTries=24
		self.tries=0
		self.startTimer(40)
	def endLevel2(self):
		self.canvas.delete(self.backboardID)
		self.canvas.delete(self.basketID)
		self.canvas.delete(self.netbackID)
		self.canvas.delete(self.netfrontID)
		for x in self.levelObjects:
			self.canvas.delete(x)
		del self.boundaries[-10:]
		self.dropBall()
		del self.physObjects[self.basketID]
		self.endTimer()
	def level3(self):
		self.gameMode='g'
		self.currentLevel=3
		self.shootBox=[0,0],[300,400]
		self.levelObjects=[]
		self.levelObjects.append(self.canvas.create_rectangle(\
		self.shootBox[0][0],self.shootBox[0][1],self.shootBox[1][0],\
		self.shootBox[1][1],fill='grey'))
		self.createBoard(700,600)
		self.basketID=self.canvas.create_image(200-self.r,200-self.r,\
		image=self.basketball,anchor=NW)
		self.createBasketball(200,200)
		self.createNet(700,600)
		self.boundaries.append(border([425,0],[400,600]))
		self.boundaries.append(stuckCircle([400,600],10))
		self.boundaries.append(border([400,600],[375,0]))
		self.levelObjects.append(self.canvas.create_polygon(375,0,400,600,425,\
		0,fill='black'))
		self.minGoals=7
		self.maxTries=22
		self.tries=0
		self.startTimer(40)
	def endLevel3(self):
		self.canvas.delete(self.backboardID)
		self.canvas.delete(self.basketID)
		self.canvas.delete(self.netbackID)
		self.canvas.delete(self.netfrontID)
		for x in self.levelObjects:
			self.canvas.delete(x)
		del self.boundaries[-5:]
		self.dropBall()
		del self.physObjects[self.basketID]
		self.endTimer()
	def level4(self):
		self.gameMode='g'
		self.currentLevel=4
		self.shootBox=[0,0],[200,800]
		self.levelObjects=[]
		self.levelObjects.append(self.canvas.create_rectangle(\
		self.shootBox[0][0],self.shootBox[0][1],self.shootBox[1][0],\
		self.shootBox[1][1],fill='grey'))
		self.createBoard(700,600)
		self.basketID=self.canvas.create_image(200-self.r,200-self.r,\
		image=self.basketball,anchor=NW)
		self.createBasketball(200,200)
		self.createNet(700,600)
		b1,r1=self.rectBound([260,500],[310,800])
		b2,r2=self.rectBound([375,450],[425,800])
		b3,r3=self.rectBound([490,500],[540,800])
		b4,r4=self.rectBound([260,0],[310,300])
		b5,r5=self.rectBound([375,0],[425,250])
		b6,r6=self.rectBound([490,0],[540,300])
		self.boundaries+=b1+b2+b3+b4+b5+b6
		self.levelObjects+=[r1,r2,r3,r4,r5,r6]
		self.minGoals=6
		self.maxTries=20
		self.tries=0
		self.startTimer(35)
	def endLevel4(self):
		self.canvas.delete(self.backboardID)
		self.canvas.delete(self.basketID)
		self.canvas.delete(self.netbackID)
		self.canvas.delete(self.netfrontID)
		for x in self.levelObjects:
			self.canvas.delete(x)
		del self.boundaries[-50:]
		self.dropBall()
		del self.physObjects[self.basketID]
		self.endTimer()
	def level5(self):
		self.gameMode='g'
		self.currentLevel=5
		self.shootBox=[0,500],[200,800]
		self.levelObjects=[]
		self.levelObjects.append(self.canvas.create_rectangle(\
		self.shootBox[0][0],self.shootBox[0][1],self.shootBox[1][0],\
		self.shootBox[1][1],fill='grey'))
		self.createBoard(400,650)
		self.basketID=self.canvas.create_image(200-self.r,200-self.r,\
		image=self.basketball,anchor=NW)
		self.createBasketball(200,200)
		self.createNet(400,650)
		b1,r1=self.rectBound([250,300],[300,800])
		b2,r2=self.rectBound([300,300],[600,350])
		self.boundaries+=b1+b2
		self.levelObjects+=[r1,r2]
		self.minGoals=5
		self.maxTries=18
		self.tries=0
		self.startTimer(30)
	def endLevel5(self):
		self.canvas.delete(self.backboardID)
		self.canvas.delete(self.basketID)
		self.canvas.delete(self.netbackID)
		self.canvas.delete(self.netfrontID)
		for x in self.levelObjects:
			self.canvas.delete(x)
		del self.boundaries[-18:]
		self.dropBall()
		del self.physObjects[self.basketID]
		self.endTimer()
	def level6(self):
		self.gameMode='g'
		self.currentLevel=6
		self.shootBox=[0,400],[200,800]
		self.levelObjects=[]
		self.levelObjects.append(self.canvas.create_rectangle(\
		self.shootBox[0][0],self.shootBox[0][1],self.shootBox[1][0],\
		self.shootBox[1][1],fill='grey'))
		self.createBoard(730,650)
		self.basketID=self.canvas.create_image(200-self.r,200-self.r,\
		image=self.basketball,anchor=NW)
		self.createBasketball(200,200)
		self.createNet(730,650)
		b1,r1=self.rectBound([250,0],[300,600])
		b2,r2=self.rectBound([500,600],[550,800])
		self.boundaries+=b1+b2
		self.levelObjects+=[r1,r2]
		self.minGoals=7
		self.maxTries=15
		self.tries=0
		self.startTimer(30)
	def endLevel6(self):
		self.canvas.delete(self.backboardID)
		self.canvas.delete(self.basketID)
		self.canvas.delete(self.netbackID)
		self.canvas.delete(self.netfrontID)
		for x in self.levelObjects:
			self.canvas.delete(x)
		del self.boundaries[-18:]
		self.dropBall()
		del self.physObjects[self.basketID]
		self.endTimer()

	def gameOver(self):
		self.gameMode='e'
		self.menuItems=[]
		msg='GAME OVER'
		pos=0
		for xNum in range(4):
			for yNum in range(4):
				x=xNum*800/4+100+randint(-5,5)
				y=yNum*800/4+100+randint(-5,5)
				self.physObjects[self.canvas.create_oval(x-20,y-20,x+20,y+20,\
				fill='#%s%s%s'%(hex(randint(30,255))[-2:],\
				hex(randint(30,255))[-2:],hex(randint(30,255))[-2:]))]=\
				circle([x,y],50,acceleration=[randint(-50,50),\
				randint(-100,100)],hard=0.7)
		for x in msg:
			self.menuItems.append(self.canvas.create_text(pos,100,anchor=NW,\
			activefill='#%s%s%s'%(hex(randint(30,255))[-2:],\
			hex(randint(30,255))[-2:],hex(randint(30,255))[-2:]),text=x,\
			font=('Times',89,'bold')))
			pos+=89
		self.startBox=[300,300],[500,400]
		self.quitBox=[300,400],[500,500]
		self.menuItems.append(self.canvas.create_rectangle(300,300,500,400))
		self.menuItems.append(self.canvas.create_text(400,350,activefill='red',\
		text='Start Game'))
		self.menuItems.append(self.canvas.create_rectangle(300,400,500,500))
		self.menuItems.append(self.canvas.create_text(400,450,activefill='red',\
		text='Quit Game'))
		self.menuItems.append(self.canvas.create_text(400,700,activefill='red',\
		text='You scored %d goals'%self.totalGoals,font=('Times',40,'bold')))

physEngine()
