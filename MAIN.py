import math
import time
import random
from contextlib import redirect_stdout

with redirect_stdout(None):
	import pygame  # No console message

# Init
displayWidth, displayHeight = 800, 600
pygame.init()
screenDisplay = pygame.display.set_mode((displayWidth, displayHeight))
pygame.display.set_caption("we still need a name for our game")
clock = pygame.time.Clock()
loadImage = pygame.image.load

# AttrDict class
class AttrDict(dict):
    def __getattr__(self, attr):  return self[attr]
    def __setattr__(self, attr, value):  self[attr] = value

# Variables
gameState = "Menu"
MAP = MENU = F = AttrDict({})
Keys = {"W": False, "A": False, "S": False, "D": False, "E": False}
F.inventory = ['cannonball', 'birb', 'monkey']

# MAP variables

MAP["PirateShips"] = []
MAP["AreaSize"] = [displayWidth * 5, displayHeight * 5]
MAP["PlayerPos"] = [MAP["AreaSize"][0] / 2, MAP["AreaSize"][0] / 2]
MAP["ScreenPos"] = [MAP["AreaSize"][0] / 2, MAP["AreaSize"][0] / 2]
MAP["PlayerSpeed"] = [0, 0]
MAP["PlayerDir"] = 0
MAP["ShipDrawPos"] = [displayWidth / 2, displayHeight / 2]
MAP["ActualDrawShip"] = MAP["ShipDrawPos"][:]
MAP["waveList"] = []
MAP["WindDir"] = random.randint(0,360) #in degrees beacuse its easier for me
MAP["WindSpeed"] = random.randint(1,10)

#Surfaces
MAP["MainSurf"] = pygame.Surface(MAP["AreaSize"])  # is shifted -playerPos, anything draw on here will be relative to world

# Loading Sprites/images
MAP.ships = [
	loadImage("mapAssets/shipL.png"),
	loadImage("mapAssets/shipUL.png"),
	loadImage("mapAssets/shipU.png"),
	loadImage("mapAssets/shipUR.png"),
	loadImage("mapAssets/shipR.png"),
	loadImage("mapAssets/shipDR.png"),
	loadImage("mapAssets/shipD.png"),
	loadImage("mapAssets/shipDL.png"),
]
MAP["pirateShipsSprites"] = {"verySmall" : [
	loadImage("mapAssets/pirateVSmallL.png"),
	loadImage("mapAssets/pirateVSmallU.png"),
	loadImage("mapAssets/pirateVSmallR.png"),
	loadImage("mapAssets/pirateVSmallD.png")
], "small" : [
	loadImage("mapAssets/pirateSmallL.png"),
	loadImage("mapAssets/pirateSmallU.png"),
	loadImage("mapAssets/pirateSmallR.png"),
	loadImage("mapAssets/pirateSmallD.png")]}

MENU["ButtonPlay"] = loadImage("menuAssets/playButton.png")
MENU["ButtonOptions"] = loadImage("menuAssets/optionsButton.png")
MENU["ButtonQuit"] = loadImage("menuAssets/quitButton.png")

class wave:
	def __init__(self, X, Y):
		self.X = X
		self.Y = Y
		self.size = 1
		self.dir = "up"
		self.colour = (50,60,200)
		self.delete = False
		self.maxSize = 8
		self.speed = 10

	def draw(self):
		if self.dir == "up":
			self.size += frameTime * self.speed
		else:
			self.size -= frameTime * self.speed

		if self.size > self.maxSize:
			self.dir = "down"
		if self.size < 0:
			self.delete = True

		self.X+=math.sin(MAP["WindDir"]*math.pi/180)*MAP["WindSpeed"]*frameTime
		self.Y+=math.cos(MAP["WindDir"]*math.pi/180)*MAP["WindSpeed"]*frameTime
		pygame.draw.polygon(MAP["MainSurf"], self.colour, ((self.X + self.size, self.Y), (self.X - self.size, self.Y), (self.X, self.Y - self.size)))


class MapPirateShip:
	def __init__(self, X, Y, power): #power 5-10 very small,  10-20 small, 20-35 med 35-50 large, boss is 60
		self.X = X
		self.Y = Y
		self.mapHealth = power*10
		self.health = power*10
		self.goingTo = [random.randint(0, MAP["AreaSize"][0]), random.randint(0, MAP["AreaSize"][1])]
		self.speed = (power+75)/7
		self.state = "wander" #can also be attack and retreat
		self.dir = 0

		if power > 5 and power < 10:
			self.type = "verySmall"
		if power > 10 and power< 20:
			self.type = "small"
		if power > 20 and power < 35:
			self.type = "med"
		if power > 35 and power < 50:
			self.type="large"
		if power == 60:
			self.type = "boss"

	def AI(self):
		if dist((self.X, self.Y), (self.goingTo[0], self.goingTo[1])) < 50 :
			if self.state == "wander":
				self.goingTo = [random.randint(0, MAP["AreaSize"][0]), random.randint(0, MAP["AreaSize"][1])]
		else:
			if self.X > self.goingTo[0] and abs(self.X-self.goingTo[0]) < 5:
				self.X-=frameTime*self.speed
				self.dir = 3
			if self.X < self.goingTo[0] and abs(self.X-self.goingTo[0]) < 5:
				self.X+=frameTime*self.speed
				self.dir = 1
			if self.Y > self.goingTo[1] and abs(self.Y-self.goingTo[1]) < 5:
				self.Y-=frameTime*self.speed
				self.dir = 0
			if self.Y < self.goingTo[1] and abs(self.Y-self.goingTo[1]) < 5:
				self.Y+=frameTime*self.speed
				self.dir = 2

		if self.state == "attack":
			self.goingTo == MAP["PlayerPos"]

	def draw(self):
		MAP["MainSurf"].blit(MAP["pirateShipsSprites"][self.type][self.dir], (self.X, self.Y))

for i in range(25):
	MAP["PirateShips"].append( MapPirateShip(random.randint(0, MAP["AreaSize"][0]), random.randint(0, MAP["AreaSize"][1]), 7))

# GAME STATES (Functions)
def map():
	global MAP
	
	MAP["MainSurf"].fill((0, 0, 200))
	pygame.draw.line(MAP["MainSurf"], (0, 0, 0), (0, 0), (MAP["AreaSize"][0], MAP["AreaSize"][1]))
	pygame.draw.line(MAP["MainSurf"], (0, 0, 0), (MAP["AreaSize"][0], 0), (0, MAP["AreaSize"][1]))
	if abs(sum(MAP["PlayerSpeed"]))<4:
		if Keys["W"] == True:
			MAP["PlayerSpeed"][1] -= frameTime * 1
			MAP["PlayerDir"] = 2

		if Keys["A"] == True:
			MAP["PlayerSpeed"][0] -= frameTime * 1
			MAP["PlayerDir"] = 0

		if Keys["S"] == True:
			MAP["PlayerSpeed"][1] += frameTime * 1
			MAP["PlayerDir"] = 2  # 6

		if Keys["D"] == True:
			MAP["PlayerSpeed"][0] += frameTime * 1
			MAP["PlayerDir"] = 0  # 4

		if Keys["W"] == True and Keys["D"] == True:
			MAP["PlayerDir"] = 3

		if Keys["D"] == True and Keys["S"] == True:
			MAP["PlayerDir"] = 5

		if Keys["S"] == True and Keys["A"] == True:
			MAP["PlayerDir"] = 7

		if Keys["A"] == True and Keys["W"] == True:
			MAP["PlayerDir"] = 1

	MAP["PlayerSpeed"][0]-=MAP["PlayerSpeed"][0]*frameTime
	MAP["PlayerSpeed"][1]-=MAP["PlayerSpeed"][1]*frameTime

	MAP["PlayerPos"][0] += MAP["PlayerSpeed"][0]
	MAP["PlayerPos"][1] += MAP["PlayerSpeed"][1] 

	MAP["ScreenPos"]=[MAP["PlayerPos"][0]-displayWidth/2, MAP["PlayerPos"][1]-displayHeight/2]
	#Pirates
	for i in range(len(MAP["PirateShips"])):
		MAP["PirateShips"][i].AI()
		MAP["PirateShips"][i].draw()
	#Waves
	if random.randint(0,100) < 99:
		MAP["waveList"].append(wave(MAP["PlayerPos"][0]+random.randint(-50, displayWidth+50),
		 MAP["PlayerPos"][1]+random.randint(-50, displayHeight+50)))
	for i in range(len(MAP["waveList"])):
		MAP["waveList"][i].draw()
	waveDeleter()
	drawShip = MAP["ships"][MAP["PlayerDir"]]
	MAP["MainSurf"].blit(drawShip, MAP["PlayerPos"])
	screenDisplay.blit(MAP["MainSurf"], [-MAP["ScreenPos"][0], -MAP["ScreenPos"][1]])
	MapUI([MAP["WindDir"], MAP["WindSpeed"]])


def menu():
	global gameState
	# Display Assets
	screenDisplay.fill((154, 219, 235))
	playButton = screenDisplay.blit(MENU["ButtonPlay"], (275, 255))
	optionsButton = screenDisplay.blit(MENU["ButtonOptions"], (275, 377))
	quitButton = screenDisplay.blit(MENU["ButtonQuit"], (275, 500))

	"""Add code"""
	if playButton.collidepoint(mousePos[0], mousePos[1]) and mouseButtons[0]:
		gameState = "Map"
	if optionsButton.collidepoint(mousePos[0], mousePos[1]) and mouseButtons[0]:
		gameState = "Options"
	if quitButton.collidepoint(mousePos[0], mousePos[1]) and mouseButtons[0]:
		pygame.mouse.set_visible(True)
		pygame.quit()
		quit()
	


def battleScreen():
	# Display Assets
	screenDisplay.blit(loadImage("fightAssets/background.png"), (0, 0))
	screenDisplay.blit(loadImage("fightAssets/friendlyShip.png"), (50, 250))
	screenDisplay.blit(loadImage("fightAssets/enemyShip.png"), (585, 250))

	slots_drawn = 0
	for item in F["inventory"]:
		slots_drawn += 1
		screenDisplay.blit(
			loadImage(f"fightAssets/INV_{item}.png"),
			(30 * slots_drawn + 50 * slots_drawn, 515))

	"""Behaviorial script"""


def cutScene(): # Need to make
	pass


### Other funtions ###
def waveDeleter():
	global MAP
	for i in range(len(MAP["waveList"])):
		if MAP["waveList"][i].delete == True:
			del MAP["waveList"][i]
			waveDeleter()
			break

def miniMap(windDir, windSpeed):
	center=(round(displayWidth*0.1), round(displayHeight*0.9))
	pygame.draw.circle(screenDisplay, (0,0,0), (center[0], center[1]), round(displayWidth*0.07), 2)
	lineP1 = (math.sin(windDir)*windSpeed*2, math.cos(windDir)*windSpeed*2)
	pygame.draw.line(screenDisplay, (100,100, 120), (lineP1[0]+center[0], lineP1[1]+center[1]), (center[0], center[1]), 3)

def MapUI(wind):
	miniMap(wind[0], wind[1])

def dist(point1, point2):
	X = abs(point1[0]-point2[0])
	Y = abs(point1[1]-point2[1])
	return math.sqrt(X**2+Y**2)

# Main Loop
while True:
	startFrame = time.time()
	screenDisplay.fill((0, 0, 0))
	mouseButtons = pygame.mouse.get_pressed()  # (left mouse button, middle, right)
	mousePos = pygame.mouse.get_pos()  # (x, y)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.mouse.set_visible(True)
			pygame.quit()
			quit()

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_w:	Keys["W"] = True
			if event.key == pygame.K_a: Keys["A"] = True
			if event.key == pygame.K_s: Keys["S"] = True
			if event.key == pygame.K_d: Keys["D"] = True

		if event.type == pygame.KEYUP:
			if event.key == pygame.K_w: Keys["W"] = False
			if event.key == pygame.K_a: Keys["A"] = False
			if event.key == pygame.K_s: Keys["S"] = False
			if event.key == pygame.K_d: Keys["D"] = False
	if gameState == "Menu":
		menu()

	if gameState == "Map":
		map()

	pygame.display.update()
	clock.tick(60)
	frameTime = time.time() - startFrame