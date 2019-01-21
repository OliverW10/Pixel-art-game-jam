import pygame
import math
import time
import random

displayWidth, displayHeight = 800, 600
pygame.init()
screenDisplay = pygame.display.set_mode((displayWidth, displayHeight))
pygame.display.set_caption("Game")
clock = pygame.time.Clock()

#Variables
#Global
Keys={"W":False,
	"A":False,
	"S":False,
	"D":False,
	"E":False}
#Areas
M_AreaSize=[displayWidth*5, displayHeight*5]
M_PlayerPos=[M_AreaSize[0]/2, M_AreaSize[0]/2]
M_PlayerDir=0
M_ShipDrawPos=[displayWidth/2, displayHeight/2]
M_ActualDrawShip=M_ShipDrawPos[:]

#Sprites/images
ships=[pygame.image.load("sprites/L.png"),
 	pygame.image.load("sprites/UL.png"),
 	pygame.image.load("sprites/U.png"),
	None,
	pygame.image.load("sprites/R.png"),
	None,
	pygame.image.load("sprites/D.png"),
	None]

#Surfaces
M_MainSurf=pygame.Surface(M_AreaSize) #is shifted

#GAME STATES Functions
def map():
	global M_PlayerDir
	global M_ActualDrawShip
	M_MainSurf.fill((0,0,200))
	pygame.draw.line(M_MainSurf, (0,0,0), (0, 0), (M_AreaSize[0], M_AreaSize[1]))
	pygame.draw.line(M_MainSurf, (0,0,0), (M_AreaSize[0], 0), (0, M_AreaSize[1]))
	if Keys["W"]==True:
		M_PlayerPos[1]-=frameTime*100
		M_PlayerDir=2
		M_ShipDrawPos[1]=displayHeight*0.46

	if Keys["A"]==True:
		M_PlayerPos[0]-=frameTime*100
		M_PlayerDir=0
		M_ShipDrawPos[0]=displayWidth*0.46

	if Keys["S"]==True:
		M_PlayerPos[1]+=frameTime*100
		M_PlayerDir=2 #6
		M_ShipDrawPos[1]=displayHeight*0.54

	if Keys["D"]==True:
		M_PlayerPos[0]+=frameTime*100
		M_PlayerDir=0 #4
		M_ShipDrawPos[0]=displayWidth*0.54

	if Keys["W"] == False and Keys["S"] == False:
		M_ShipDrawPos[1]=displayHeight*0.5

	if Keys["A"] == False and Keys["D"] == False:
		M_ShipDrawPos[0]=displayWidth*0.5
	

	screenDisplay.blit(M_MainSurf, [-M_PlayerPos[0], -M_PlayerPos[1]])
	drawShip=ships[M_PlayerDir]
	M_ActualDrawShip=[(M_ActualDrawShip[0]+M_ShipDrawPos[0]+M_ShipDrawPos[0])/3, (M_ActualDrawShip[1]+M_ShipDrawPos[1] +M_ShipDrawPos[1])/3]

	print(M_ActualDrawShip)
	screenDisplay.blit(drawShip, M_ActualDrawShip)

def menu():
	pass
def fight():
	pass
def cutScene():
	pass

#Other funtions


#Classes
while True:
	startFrame=time.time()
	screenDisplay.fill((0,0,0))
	mouseButtons=pygame.mouse.get_pressed() #(left mouse button, middle, right)
	mousePos=pygame.mouse.get_pos() #(x, y)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.mouse.set_visible(False)
			pygame.quit()
			quit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_w:
				Keys["W"]=True
			if event.key == pygame.K_a:
				Keys["A"]=True
			if event.key == pygame.K_s:
				Keys["S"]=True
			if event.key == pygame.K_d:
				Keys["D"]=True

		if event.type == pygame.KEYUP:
			if event.key == pygame.K_w:
				Keys["W"]=False
			if event.key == pygame.K_a:
				Keys["A"]=False
			if event.key == pygame.K_s:
				Keys["S"]=False
			if event.key == pygame.K_d:
				Keys["D"]=False
	map()
	pygame.display.update()
	clock.tick(60)
	frameTime=time.time()-startFrame
