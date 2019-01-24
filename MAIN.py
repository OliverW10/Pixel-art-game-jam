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
MAP["AreaSize"] = [displayWidth * 3, displayHeight * 3]
MAP["PlayerPos"] = [MAP["AreaSize"][0] / 2, MAP["AreaSize"][0] / 2]
MAP["ScreenPos"] = [MAP["AreaSize"][0] / 2, MAP["AreaSize"][0] / 2]
MAP["PlayerSpeed"] = [0, 0]
MAP["PlayerDir"] = 0
MAP["ShipDrawPos"] = [displayWidth / 2, displayHeight / 2]
MAP["ActualDrawShip"] = MAP["ShipDrawPos"][:]
MAP["waveList"] = []
MAP["WindDir"] = math.pi*1.5#random.randint(0, round(math.pi*2)) #in degrees beacuse its easier for me
MAP["WindSpeed"] = 20 #random.randint(1,10)
MAP["screenRect"] = pygame.Rect(-25, -25, displayWidth+50, displayHeight+50)
MAP["LandBlocks"] = {} #List of all peices of land each land is 25x25px
#Land masses is a 400x300 array or dictionay
# 1 is sand, 2 is land, 3 is town and 4 is port
MAP["WaveSpawnTimer"] = 0

#Random generation
islands = {}
islandNum=random.randint(3, 5)

for i in range(islandNum):
	town = str(random.randint(0, round(MAP["AreaSize"][0]/25))*25)+","+str(random.randint(0, round(MAP["AreaSize"][0]/25))*25)
	islands[town] = 1

for i in islands:
	MAP["LandBlocks"][i] = 3

for i in range(1000):
	points = MAP["LandBlocks"].keys()
	points = list(points)
	point = random.choice(points)
	x = int(point.split(",")[0])
	y = int(point.split(",")[1])
	x += random.randint(-1, 1)*25
	y += random.randint(-1, 1)*25
	if str(x)+","+str(y) in MAP["LandBlocks"]:
		pass
	else:
		MAP["LandBlocks"][str(x)+","+str(y)] = 2

for i in range(200):
	points = MAP["LandBlocks"].keys()
	points = list(points)
	point = random.choice(points)
	x = int(point.split(",")[0])
	y = int(point.split(",")[1])
	x += random.randint(-1, 1)*25
	y += random.randint(-1, 1)*25
	if str(x)+","+str(y) in MAP["LandBlocks"]:
		pass
	else:
		MAP["LandBlocks"][str(x)+","+str(y)] = 1


# Loading Sprites/images
MAP.ships = [
	loadImage("mapAssets/Player/shipL.png"),
	loadImage("mapAssets/Player/shipUL.png"),
	loadImage("mapAssets/Player/shipU.png"),
	loadImage("mapAssets/Player/shipUR.png"),
	loadImage("mapAssets/Player/shipR.png"),
	loadImage("mapAssets/Player/shipDR.png"),
	loadImage("mapAssets/Player/shipD.png"),
	loadImage("mapAssets/Player/shipDL.png"),
]

MAP.waves = [
	loadImage("mapAssets/Waves/wave1.png"),
	loadImage("mapAssets/Waves/wave2.png"),
	loadImage("mapAssets/Waves/wave3.png"),
	loadImage("mapAssets/Waves/wave4.png")]

def doubleSizeList(list):
	newList = []
	for i in range(len(list)):
		size = list[i].get_rect().size
		newList.append(pygame.transform.scale(list[i], (size[0]*2, size[1]*2)))
	return newList

MAP["pirateShipsSprites"] = {"verySmall" : [
	loadImage("mapAssets/Pirates/verySmall/pirateVSmallL.png"),
	loadImage("mapAssets/Pirates/verySmall/pirateVSmallU.png"),
	loadImage("mapAssets/Pirates/verySmall/pirateVSmallR.png"),
	loadImage("mapAssets/Pirates/verySmall/pirateVSmallD.png")
], "small" : [
	loadImage("mapAssets/Pirates/small/pirateSmallL.png"),
	loadImage("mapAssets/Pirates/small/pirateSmallU.png"),
	loadImage("mapAssets/Pirates/small/pirateSmallR.png"),
	loadImage("mapAssets/Pirates/small/pirateSmallD.png")]}

MAP["pirateShipsSprites"]["verySmall"] = doubleSizeList(MAP["pirateShipsSprites"]["verySmall"])
MAP["pirateShipsSprites"]["small"] = doubleSizeList(MAP["pirateShipsSprites"]["small"])
MAP.ships = doubleSizeList(MAP.ships)
#MAP.waves = doubleSizeList(MAP.waves)

MENU["ButtonPlay"] = loadImage("menuAssets/playButton.png")
MENU["ButtonOptions"] = loadImage("menuAssets/optionsButton.png")
MENU["ButtonQuit"] = loadImage("menuAssets/quitButton.png")

class wave:
	def __init__(self, X, Y):
		self.X = X
		self.Y = Y
		self.size = 0
		self.dir = "up"
		self.colour = (50,60,200)
		self.delete = False
		self.surface = pygame.Surface((8, 4))
		self.timer = 0

	def draw(self):
		self.timer+=frameTime
		if self.timer > 0.2:
			self.timer = 0
			if self.dir == "up":
				self.size += 1
			else:
				self.size -= 1

			if self.size >= 3:
				self.dir = "down"
			if self.size <= 0:
				self.delete = True

		self.X+=math.sin(MAP["WindDir"])*MAP["WindSpeed"]*frameTime
		self.Y+=math.cos(MAP["WindDir"])*MAP["WindSpeed"]*frameTime
		screenDisplay.blit(MAP.waves[self.size], (self.X - MAP["ScreenPos"][0], self.Y - MAP["ScreenPos"][1]))


class PirateShip:
	def __init__(self, X, Y, power): #power 5-10 very small,  10-20 small, 20-35 med 35-50 large, boss is 60
		self.X = X
		self.Y = Y
		self.goingTo = [random.randint(0, MAP["AreaSize"][0]), random.randint(0, MAP["AreaSize"][1])]
		self.speed = (power+75)/7
		self.state = "wander" #can also be attack and retreat
		self.dir = 0
		self.HP = power*10
		self.maxHP = power*10
		self.hovered = False

		if power >= 5 and power < 10:
			self.type = "verySmall"
		if power >= 10 and power < 20:
			self.type = "small"
		if power >= 20 and power < 35:
			self.type = "med"
		if power >= 35 and power < 50:
			self.type="large"
		if power == 60:
			self.type = "boss"

	def AI(self):
		if dist((self.X, self.Y), (self.goingTo[0], self.goingTo[1])) < 50 :
			if self.state == "wander":
				self.goingTo = [random.randint(0, MAP["AreaSize"][0]), random.randint(0, MAP["AreaSize"][1])]
		else:
			if self.X > self.goingTo[0]:
				self.X-=frameTime*self.speed
				self.dir = 3
			if self.X < self.goingTo[0]:
				self.X+=frameTime*self.speed
				self.dir = 1
			if self.Y > self.goingTo[1]:
				self.Y-=frameTime*self.speed
				self.dir = 0
			if self.Y < self.goingTo[1]:
				self.Y+=frameTime*self.speed
				self.dir = 2
			distX = self.goingTo[0] - self.X
			distY = self.goingTo[1] - self.Y
			if abs(distX) > abs(distY):
				if distX > 0:
					self.dir = 2
				else:
					self.dir = 0
			else:
				if distY > 0:
					self.dir = 3
				else:
					self.dir = 1

		if self.state == "attack":
			self.goingTo == MAP["PlayerPos"]

	def draw(self):
		self.drawX = self.X - MAP["ScreenPos"][0]
		self.drawY = self.Y - MAP["ScreenPos"][1]

		if dist((self.drawX, self.drawY), (mousePos[0], mousePos[1])) < 50:
			self.hovered = True
			pygame.draw.rect(screenDisplay, (0, 0, 0), (self.drawX-5, self.drawY-10, (self.HP / self.maxHP) * 40, 5))
		else:
			self.hovered = False
		if self.drawX>-20 and self.drawX<displayWidth+20 and self.drawY>-20 and self.drawY<displayHeight+20: # this for some reason makes it run 10-20% worse
			screenDisplay.blit(MAP["pirateShipsSprites"][self.type][self.dir], (self.drawX, self.drawY))
		
for i in range(10):
	MAP["PirateShips"].append( PirateShip(random.randint(0, MAP["AreaSize"][0]), random.randint(0, MAP["AreaSize"][1]), random.randint(5,19)))

# GAME STATES (Functions)
def map():
	global MAP
	global gameState
	pygame.draw.rect(screenDisplay, (0,0,0), (-MAP["ScreenPos"][0], -MAP["ScreenPos"][1], MAP["AreaSize"][0], MAP["AreaSize"][1]), 5)
	pygame.draw.line(screenDisplay, (0, 0, 0), (0 - MAP["ScreenPos"][0], 0 - MAP["ScreenPos"][1]), (MAP["AreaSize"][0] - MAP["ScreenPos"][0], MAP["AreaSize"][1] - MAP["ScreenPos"][1]))
	pygame.draw.line(screenDisplay, (0, 0, 0), (MAP["AreaSize"][0] - MAP["ScreenPos"][0], 0 - MAP["ScreenPos"][1]), (0 - MAP["ScreenPos"][0], MAP["AreaSize"][1] - MAP["ScreenPos"][1]))
	if abs(sum(MAP["PlayerSpeed"]))<4:
		if Keys["W"] == True:
			MAP["PlayerSpeed"][1] -= frameTime * 2
			MAP["PlayerDir"] = 2

		if Keys["A"] == True:
			MAP["PlayerSpeed"][0] -= frameTime * 2
			MAP["PlayerDir"] = 0

		if Keys["S"] == True:
			MAP["PlayerSpeed"][1] += frameTime * 2
			MAP["PlayerDir"] = 2  # 6

		if Keys["D"] == True:
			MAP["PlayerSpeed"][0] += frameTime * 2
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

	MAP["PlayerPos"][0] += MAP["PlayerSpeed"][0]*frameTime*30
	MAP["PlayerPos"][1] += MAP["PlayerSpeed"][1]*frameTime*30

	MAP["ScreenPos"]=[MAP["PlayerPos"][0]-displayWidth/2, MAP["PlayerPos"][1]-displayHeight/2]
	#Logic
	#Into fight
	for i in range(len(MAP["PirateShips"])):
		if MAP["PirateShips"][i].hovered == True:
			distance = dist((round(MAP["PlayerPos"][0]), round(MAP["PlayerPos"][1])), (MAP["PirateShips"][i].X, MAP["PirateShips"][i].Y))
			if distance < 100 and mouseButtons[0] == True:
				gameState = "Fight"
				print(gameState)

	#Drawing
	#Waves
	MAP["WaveSpawnTimer"] += frameTime
	if  MAP["WaveSpawnTimer"]>0.1:
		MAP["WaveSpawnTimer"] = 0
		MAP["waveList"].append(wave(MAP["PlayerPos"][0]+random.randint(-displayWidth/2-50, displayWidth/2+50),
									MAP["PlayerPos"][1]+random.randint(-displayHeight/2-50, displayHeight/2+50)))

	for i in range(len(MAP["waveList"])):
		MAP["waveList"][i].draw()
	waveDeleter()

	#Land
	for pos in MAP["LandBlocks"]:
		if MAP["LandBlocks"][pos] == 1:
			colour = (255, 200, 10)
		if MAP["LandBlocks"][pos] == 2:
			colour = (0, 255, 0)
		if MAP["LandBlocks"][pos] == 3:
			colour = (210,105,30)
		x = int(pos.split(",")[0])  - MAP["ScreenPos"][0]
		y = int(pos.split(",")[1])  - MAP["ScreenPos"][1]
		if x > -25 and x < displayWidth and y > -25 and y < displayHeight:
			pygame.draw.rect(screenDisplay, (colour), (x, y, 25, 25))
	#Pirates
	for i in range(len(MAP["PirateShips"])):
		MAP["PirateShips"][i].AI()
		MAP["PirateShips"][i].X
		MAP["PirateShips"][i].draw()

	#Player
	drawShip = MAP["ships"][MAP["PlayerDir"]]
	screenDisplay.blit(drawShip, (MAP["PlayerPos"][0] - MAP["ScreenPos"][0], MAP["PlayerPos"][1] - MAP["ScreenPos"][1]))
	#Ui
	MapUI([MAP["WindDir"], MAP["WindSpeed"]], MAP["PirateShips"])


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

def MapUI(wind, pirateShips):
	miniMap(wind[0], wind[1])

def dist(point1, point2):
	X = abs(point1[0]-point2[0])
	Y = abs(point1[1]-point2[1])
	return math.sqrt(X**2+Y**2)

# Main Loop
while True:
	startFrame = time.time()
	screenDisplay.fill((0, 0, 200))
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
			if event.key == pygame.K_f: print(clock.get_fps())

		if event.type == pygame.KEYUP:
			if event.key == pygame.K_w: Keys["W"] = False
			if event.key == pygame.K_a: Keys["A"] = False
			if event.key == pygame.K_s: Keys["S"] = False
			if event.key == pygame.K_d: Keys["D"] = False
	if gameState == "Menu":
		menu()

	if gameState == "Map":
		map()

	if gameState == "Fight":
		battleScreen() #dont know wether to do a fight in the map screen or one in the battle screen or both or a combination

	pygame.display.update()
	clock.tick()
	frameTime = time.time() - startFrame