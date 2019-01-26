import pygame
import math

displayWidth, displayHeight = 800, 600
pygame.init()
screenDisplay = pygame.display.set_mode((displayWidth, displayHeight))
pygame.display.set_caption("we still need a name for our game")
clock = pygame.time.Clock()

islands = {}
drawType = 4

def delBlue():
	global islands
	for i in islands:
		if islands[i] == 9:
			del islands[i]
			delBlue()
			break

while True:
	screenDisplay.fill((0,0,200))
	mouseButtons = pygame.mouse.get_pressed()  # (left mouse button, middle, right)
	mousePos = pygame.mouse.get_pos()
	for event in pygame.event.get():
		if event.type == pygame.QUIT: 
			pygame.quit()
			exit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_s:
				print(islands)
			if event.key == pygame.K_r: islands = {}
			if event.key == pygame.K_1: drawType = 1
			if event.key == pygame.K_2: drawType = 2
			if event.key == pygame.K_3: drawType = 3
			if event.key == pygame.K_4: drawType = 4
			if event.key == pygame.K_9: drawType = 9

	if mouseButtons[0] ==True:
		addX = math.floor(mousePos[0]/25)*25
		addY = math.floor(mousePos[1]/25)*25
		islands[str(addX)+","+str(addY)] = drawType

	for pos in islands:
		if islands[pos] == 1: #sand
			colour = (255, 200, 100)
		elif islands[pos] == 2: #grass
			colour = (0, 255, 0)
		elif islands[pos] == 3: #town
			colour = (210,105,30)
		elif islands[pos] == 4: #port
			colour = (5,5,5)
		elif islands[pos] == 9:
			colour = (0,0,200)

		x = int(pos.split(",")[0])
		y = int(pos.split(",")[1])
		pygame.draw.rect(screenDisplay, (colour), (x, y, 25, 25))
	delBlue()
	pygame.display.update()
	clock.tick()