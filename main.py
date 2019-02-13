import time
startLoad = time.time()
import copy
import math
import random
import pygame
import islands as islandData
import numpy as np
import json

# Init
displayWidth, displayHeight = 800, 600
pygame.init()
screenDisplay = pygame.display.set_mode((displayWidth, displayHeight))
gameDisplay = pygame.Surface((displayWidth, displayHeight))
pygame.display.set_caption("penis face")
clock = pygame.time.Clock()
loadImage = pygame.image.load

# AttrDict class
class AttrDict(dict):
	def __getattr__(self, attr):
		return self[attr]

	def __setattr__(self, attr, value):
		self[attr] = value

#Loading save

file = open("not_the_save.txt", "r+")

# Variables
global gameState
gameState = "Cutscene"
global MAP, MENU, F, PREP, SAVE
frameTime = 0
MAP = MENU = F = PREP = SHOP = AttrDict({})

SAVE = json.loads(file.read())

Keys = {"W": False, "A": False, "S": False, "D": False, "E": False, "Esc" : False}
#SAVE["inventory"] = SAVE["inventory"]
print(SAVE)
#SAVE["inventory"] = {"sailors": [], "cannonballs": 10, "nets": 3, "bullets" : 20}

# MAP variables
MAP["SparkleType"] = 1  # 0 is shit, 1 is fps low and 2 is off
if MAP["SparkleType"] == 0:
	MAP["WaterReflections"] = []
	MAP["WaterReflectionsCount"] = 0
	MAP["WaterReflectionsPos"] = [0, 0]
	MAP["lastReflectSprite"] = 0

MAP["PirateShips"] = []
MAP["AreaSize"] = [displayWidth * 3, displayHeight * 3]
MAP["PlayerPos"] = [MAP["AreaSize"][0] / 2, MAP["AreaSize"][0] / 2]
MAP["ScreenPos"] = [MAP["AreaSize"][0] / 2, MAP["AreaSize"][0] / 2]
MAP["PlayerSpeed"] = [0, 0]
MAP["PlayerDir"] = 0
MAP["Stats"] = {
	"speed": [1.5, 2.5, 3.5, 5, 25],
	"armor": [1.3, 1.15, 1, 0.8, 0.1],
	"HP": [50, 60, 75, 100, 150, 250, 350, 500, 2000], #hehe
}
MAP["PlayerLevels"] = {"speed": 0, "armor": 0, "HP": 0}
MAP["PlayerStats"] = {
	"speed": MAP["Stats"]["speed"][MAP["PlayerLevels"]["speed"]],
	"armor": MAP["Stats"]["armor"][MAP["PlayerLevels"]["armor"]],
	"HP": MAP["Stats"]["HP"][MAP["PlayerLevels"]["HP"]],
}
SHOP["UpgradeCosts"] = {
	"speed": [100, 500, 1200, 9999, "max"],
	"armor": [200, 1000, 2000, 9999, "max"],
	"HP": [50, 100, 200, 500, 1000, 1500, 9999, "max"],
}
#                          total 6800                             total 9200                        total 5350
MAP["ShipDrawPos"] = [displayWidth / 2, displayHeight / 2]
MAP["waveList"] = []
MAP["WindDir"] = (
	math.pi * 1.5
)  # random.randint(0, round(math.pi*2)) #in degrees beacuse its easier for me
MAP["WindSpeed"] = 20  # random.randint(1,10)
MAP["screenRect"] = pygame.Rect(-25, -25, displayWidth + 50, displayHeight + 50)
MAP["LandBlocks"] = {}  # List of all peices of land each land is 25x25px
MAP["MiniMapDrawList"] = {}  # actually a dictionary but ctr + h is too hard
# Land masses is a 400x300 array or dictionay
# 1 is sand, 2 is land, 3 is town and 4 is port
MAP.WaveSpawnTimer = 0
PREP.EnemyCargo = {}

shakePos = [0, 0]
shakeVol = [random.random() * 4 - 2, random.random() * 4 - 2]
# WaterReflections
if MAP["SparkleType"] == 0:
	for p in range(10):
		MAP["WaterReflections"].append(pygame.Surface((displayWidth, displayHeight)))
		MAP["WaterReflections"][-1].fill((0, 0, 200))
		for i in range(1000):
			x = (random.random() + random.random()) / 2
			x -= 0.5

			y = random.random()
			#    y * how much angle + how wide (inverse)
			x /= y * 5 + 3

			x *= displayWidth
			x += displayWidth / 2
			y = -y
			y += 1
			y *= displayHeight
			# this i think represents its, im not sure though beacuse i dont actually understand it very well
			# https://www.google.com/search?safe=strict&ei=9j5QXP25G8v79QPuhaiYCQ&q=%28x-0.5%29%2Fy*5%2B3&oq=%28x-0.5%29%2Fy*5%2B3&gs_l=psy-ab.3.1.0i8i30l10.5595.6251..6419...0.0..0.311.311.3-1......0....1..gws-wiz.......0i71.JB_DbqJCM2Q
			pygame.draw.rect(MAP["WaterReflections"][-1], (200, 200, 255), (x, y, 5, 5))

# Random generation
islands = {}

islandTypes = islandData.data[:]

class tile:
	def __init__(self, X, Y, path, angle):
		self.X = X
		self.Y = Y
		self.img = loadImage(path)
		self.img = pygame.transform.rotate(self.img, angle)
		self.img = pygame.transform.scale(self.img, (25,25))

	def run(self):
		gameDisplay.blit(self.img, (self.X - MAP["ScreenPos"][0], self.Y - MAP["ScreenPos"][1]))

def generateIslands():
	global islands
	global MAP
	islandPoints = []
	done = False
	# create bases
	for i in range(7):
		x = (random.randint(0, round((MAP["AreaSize"][0] - 800) / 25))) * 25
		y = (random.randint(0, round((MAP["AreaSize"][1] - 600) / 25))) * 25
		islandBase = random.choice(islandTypes)
		for i in islandBase:  # goes through every block in the base
			blockX = int(i.split(",")[0])
			blockY = int(i.split(",")[1])
			MAP["LandBlocks"][str(x + blockX) + "," + str(y + blockY)] = 2

	# add sand to bases
	endNum = 500
	i = 0
	while i < endNum:
		start = random.choice(list(MAP["LandBlocks"].keys()))
		x = start.split(",")[0]
		y = start.split(",")[1]
		side = random.randint(0, 3)
		if side == 0:
			if x + "," + str(int(y) + 25) in MAP["LandBlocks"].keys():
				endNum += 1
			else:
				MAP["LandBlocks"][x + "," + str(int(y) + 25)] = 1
		if side == 1:
			if x + "," + str(int(y) - 25) in MAP["LandBlocks"].keys():
				endNum += 1
			else:
				MAP["LandBlocks"][x + "," + str(int(y) - 25)] = 1
		if side == 2:
			if str(int(x) + 25) + "," + y in MAP["LandBlocks"].keys():
				endNum += 1
			else:
				MAP["LandBlocks"][str(int(x) + 25) + "," + y] = 1
		if side == 3:
			if str(int(x) - 25) + "," + y in MAP["LandBlocks"].keys():
				endNum += 1
			else:
				MAP["LandBlocks"][str(int(x) - 25) + "," + y] = 1
		i += 1

	# add sand to bases
	endNum = 10
	i = 0
	while i < endNum:
		start = random.choice(list(MAP["LandBlocks"].keys()))
		x = start.split(",")[0]
		y = start.split(",")[1]
		side = random.randint(0, 3)
		if side == 0:
			if x + "," + str(int(y) + 25) in MAP["LandBlocks"].keys():
				endNum += 1
			else:
				MAP["LandBlocks"][x + "," + str(int(y) + 25)] = 4
		if side == 1:
			if x + "," + str(int(y) - 25) in MAP["LandBlocks"].keys():
				endNum += 1
			else:
				MAP["LandBlocks"][x + "," + str(int(y) - 25)] = 4
		if side == 2:
			if str(int(x) + 25) + "," + y in MAP["LandBlocks"].keys():
				endNum += 1
			else:
				MAP["LandBlocks"][str(int(x) + 25) + "," + y] = 4
		if side == 3:
			if str(int(x) - 25) + "," + y in MAP["LandBlocks"].keys():
				endNum += 1
			else:
				MAP["LandBlocks"][str(int(x) - 25) + "," + y] = 4
		i += 1

	#Generate the sides for tile drawing
	MAP["DrawList"] = []
	for i in MAP["LandBlocks"].keys():
		sideCovered = 0
		#Find positions
		X = i.split(",")[0]
		Y = i.split(",")[1]
		if MAP["LandBlocks"][i] == 1:
			#test blocks around it by using in (returns bool)
			N = X+","+str(int(Y)-25) in MAP["LandBlocks"].keys() 
			E = str(int(X)+25)+","+Y in MAP["LandBlocks"].keys()
			S = X+","+str(int(Y)+25) in MAP["LandBlocks"].keys()
			W = str(int(X)-25)+","+Y in MAP["LandBlocks"].keys()
			NE = str(int(X)+25)+","+str(int(Y)-25) in MAP["LandBlocks"].keys()
			SE = str(int(X)+25)+","+str(int(Y)+25) in MAP["LandBlocks"].keys()
			NW = str(int(X)-25)+","+str(int(Y)-25) in MAP["LandBlocks"].keys()
			SW = str(int(X)-25)+","+str(int(Y)+25) in MAP["LandBlocks"].keys()

			if N:
				sideCovered+=1
			if E:
				sideCovered+=1
			if S:
				sideCovered+=1
			if W:
				sideCovered+=1

			if sideCovered == 0:
				MAP["DrawList"][i] = tile("mapAssets/Land/Sand/4.png", random.randint(-2, 1)*90)

			elif sideCovered == 1: #Done
				if N == True:
					MAP["DrawList"].append(tile(int(X), int(Y), "mapAssets/Land/Sand/3.png", 0))
				elif S == True:
					MAP["DrawList"].append(tile(int(X), int(Y), "mapAssets/Land/Sand/3.png", 180))
				elif E == True:
					MAP["DrawList"].append(tile(int(X), int(Y), "mapAssets/Land/Sand/3.png", -90))
				elif W == True:
					MAP["DrawList"].append(tile(int(X), int(Y),"mapAssets/Land/Sand/3.png", 90))

			elif sideCovered == 2:
				if N == True and S == True:
					MAP["DrawList"].append(tile(int(X), int(Y), "mapAssets/Land/Sand/1+1.png", 0))
				if W == True and E == True:
					MAP["DrawList"].append(tile(int(X), int(Y), "mapAssets/Land/Sand/1+1.png", 90))

				if N == True and E == True: #edge is SE
					MAP["DrawList"].append(tile(int(X), int(Y), "mapAssets/Land/Sand/2.png", -90))
				if S == True and E == True:
					MAP["DrawList"].append(tile(int(X), int(Y), "mapAssets/Land/Sand/2.png", 180))
				if N == True and W == True:
					MAP["DrawList"].append(tile(int(X), int(Y), "mapAssets/Land/Sand/2.png", 0))
				if S == True and W == True:
					MAP["DrawList"].append(tile(int(X), int(Y), "mapAssets/Land/Sand/2.png", 90))

			elif sideCovered == 3:
				if N == False:
					MAP["DrawList"].append(tile(int(X), int(Y), "mapAssets/Land/Sand/1.png", 180))
				elif S == False:
					MAP["DrawList"].append(tile(int(X), int(Y), "mapAssets/Land/Sand/1.png", 0))
				elif E == False:
					MAP["DrawList"].append(tile(int(X), int(Y), "mapAssets/Land/Sand/1.png", 90))
				elif W == False:
					MAP["DrawList"].append(tile(int(X), int(Y),"mapAssets/Land/Sand/1.png", -90))

			elif sideCovered == 4: #corner points ES
				MAP["DrawList"].append(tile(int(X), int(Y), "mapAssets/Land/Sand/0.png", random.randint(-2, 1)*90)) 
 

def testCollision(point, pirate):
	collide = islandArray[int(point[0] / 25)][int(point[1] / 25)]
	if pirate == False:
		if collide == 4:
			global gameState
			gameState = "shop"
			return "port"
		elif collide != 0:
			return True
		else:
			return False
	else:
		if collide == 0:
			return False
		else:
			return True


generateIslands()
MAP["CollisionsList"] = []
for pos in MAP["LandBlocks"]:
	x = int(pos.split(",")[0])
	y = int(pos.split(",")[1])
	if (
		str(x + 25) + "," + str(y) in MAP["LandBlocks"]
		and str(x - 25) + "," + str(y) in MAP["LandBlocks"]
		and str(x) + "," + str(y + 25) in MAP["LandBlocks"]
		and str(x) + "," + str(y - 25) in MAP["LandBlocks"]
	):
		pass
	else:
		MAP["CollisionsList"].append(pygame.Rect(x, y, 25, 25))

islandArray = np.zeros(
	(round(MAP["AreaSize"][0] / 25) + 800, round(MAP["AreaSize"][1] / 25) + 600)
)
for pos in MAP["LandBlocks"]:
	x = int(pos.split(",")[0]) / 25
	y = int(pos.split(",")[1]) / 25
	x = round(x)
	y = round(y)
	islandArray[x][y] = MAP["LandBlocks"][pos]

while testCollision(MAP["PlayerPos"], False) == True:
	MAP["PlayerPos"][0] += 25


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
MAP["PlayerRect"] = MAP.ships[0].get_rect()

MAP.waves = [
	loadImage("mapAssets/Waves/wave1.png"),
	loadImage("mapAssets/Waves/wave2.png"),
	loadImage("mapAssets/Waves/wave3.png"),
	loadImage("mapAssets/Waves/wave4.png"),
]


def doubleSizeList(list):
	newList = []
	for i in range(len(list)):
		size = list[i].get_rect().size
		newList.append(pygame.transform.scale(list[i], (size[0] * 2, size[1] * 2)))
	return newList


MAP["pirateShipsSprites"] = {
	"tiny": [
		loadImage("mapAssets/Pirates/tiny/pirateVSmallL.png"),
		loadImage("mapAssets/Pirates/tiny/pirateVSmallU.png"),
		loadImage("mapAssets/Pirates/tiny/pirateVSmallR.png"),
		loadImage("mapAssets/Pirates/tiny/pirateVSmallD.png"),
	],
	"small": [
		loadImage("mapAssets/Pirates/small/pirateSmallL.png"),
		loadImage("mapAssets/Pirates/small/pirateSmallU.png"),
		loadImage("mapAssets/Pirates/small/pirateSmallR.png"),
		loadImage("mapAssets/Pirates/small/pirateSmallD.png"),
	],
}

MAP["pirateShipsSprites"]["tiny"] = doubleSizeList(MAP["pirateShipsSprites"]["tiny"])
MAP["pirateShipsSprites"]["small"] = doubleSizeList(MAP["pirateShipsSprites"]["small"])
MAP.ships = doubleSizeList(MAP.ships)
# MAP.waves = doubleSizeList(MAP.waves)

MENU["ButtonPlay"] = loadImage("menuAssets/playButton.png")
MENU["ButtonOptions"] = loadImage("menuAssets/optionsButton.png")
MENU["ButtonQuit"] = loadImage("menuAssets/quitButton.png")

SHOP["BuyBoard"] = loadImage("mapAssets/buy board.png")
SHOP["BuyBoard"] = pygame.transform.scale(
	SHOP["BuyBoard"], (displayWidth, displayHeight)
)
SHOP["shopXbutton"] = loadImage("mapAssets/shopXbutton.png")
SHOP["shopXbutton"] = pygame.transform.scale(SHOP["shopXbutton"], (60, 84))

PREP["Paper"] = loadImage("mapAssets/paper.png")
PREP["Paper"] = pygame.transform.scale(MAP["Paper"], (displayWidth, displayHeight))
PREP["FightButtonRect"] = pygame.Rect(
	displayWidth * 0.85, displayHeight * 0.9, displayWidth * 0.14, displayHeight * 0.09
)
PREP["Text"] = {}
PREP["Xbutton"] = loadImage("mapAssets/prepXbutton.png")


class drawImage:
	def __init__(self, img):
		self.img = img

	def resize(self, W, H):
		self.img = pygame.transform.scale(self.img, (W, H))

	def draw(self, X, Y):
		rect = self.img.get_rect()
		gameDisplay.blit(self.img, (X - rect.w / 2, Y - rect.h / 2))


class sparkle:
	def __init__(self, X, Y):
		self.X = X
		self.Y = Y
		self.swap = False
		#          (x, y),

	def do(self, move):
		self.X += move[0]
		self.Y += move[1]
		self.delChance = self.checkRarety()
		self.checkMove() #yuuuh
		pygame.draw.rect(gameDisplay, (200, 200, 255), (self.X, self.Y, 5, 5))

	def checkRarety(self):
		temp = abs(
			displayWidth / 2 - self.X
		)  # dist((self.X, self.Y), (displayWidth/2, displayHeight/2))
		return temp

	def checkMove(self):
		if (
			abs(self.delChance)
			+ (
				random.randint(-100, 100)
				+ random.randint(-100, 100)
				+ random.randint(-100, 100)
			)
			/ 3
			> 100
			or self.Y > displayHeight
			or self.Y < 0
		):
			self.reset()
			self.delChance = self.checkRarety()
			self.checkMove()

	def reset(self):
		self.X, self.Y = (
			random.randint(0, displayWidth),
			random.randint(0, displayHeight),
		)


if MAP["SparkleType"] == 1:
	MAP["Sparkles"] = []
	for i in range(200):
		MAP["Sparkles"].append(
			sparkle(random.randint(0, displayWidth), random.randint(0, displayHeight))
		)


def text_objects(message, font, colour):
	textSurface = font.render(message, True, colour)
	return textSurface, textSurface.get_rect()


class text:
	def __init__(self, message, X, Y, size, colour):
		self.message = message
		self.font = pygame.font.Font("FantasticBoogaloo.ttf", round(size * 1.5))
		self.surf, self.rect = text_objects(self.message, self.font, colour)
		self.X = X
		self.Y = Y
		self.rect.center = (self.X, self.Y)


	def draw(self):
		gameDisplay.blit(self.surf, self.rect)

	def XYdraw(self, X, Y):
		self.rect.center = (X, Y)
		gameDisplay.blit(self.surf, (self.rect.x + self.X, self.rect.y + self.Y, self.rect.w, self.rect.h))


class sailor:
	def __init__(self, level, gameState="prep"):
		self.level = level
		self.gold = 0
		self.stealingPower = level
		self.ability = abs(
			random.randint(-3, 3)
		)  # -3 to 0 is nothing, 1 is brid (enemies steal 25% less), 2 is monkey (you steal 30% more) and 3 is god and anime (decreases change of death by 15%)
		if level == 1:
			if random.randint(0, 1) == 0:
				self.sprite = loadImage("mapAssets\Sailors\Good\lv1(0).png")
			else:
				self.sprite = loadImage("mapAssets\Sailors\Good\lv1(1).png")
		if level == 2:
			self.sprite = loadImage("mapAssets\Sailors\Good\lv2(0).png")

		if level == 3:
			self.sprite = loadImage("mapAssets\Sailors\Good\lv3(0).png")

		self.size = self.sprite.get_rect().size
		self.size = [self.size[0] * 2, self.size[1] * 2]
		self.rect = self.sprite.get_rect()
		self.rect.size = self.size
		self.gameState = gameState
		self.X = None
		self.Y = None
		self.dragX = None
		self.dragY = None
		self.dragged = False
		self.dragDifX = None
		self.dragDifY = None
		self.location = "start"

	def setPos(self, X, Y):
		self.X = X
		self.Y = Y
		self.rect.x = X
		self.rect.y = Y

	def logic(self, dropSpots):  # drop spots is a list of rects that you can drop at
		if self.dragged == False:
			if (
				self.rect.collidepoint(mousePos[0], mousePos[1]) == True
				and mouseButtons[0] == True
			):
				self.dragged = True
				self.dragDifX = self.X - mousePos[0]
				self.dragDifY = self.Y - mousePos[1]
				self.dragX = mousePos[0] + self.dragDifX
				self.dragY = mousePos[1] + self.dragDifY
			else:
				self.dragX = self.X
				self.dragY = self.Y
		if self.dragged == True:
			for i in range(len(dropSpots)):
				if dropSpots[i].collidepoint((self.dragX, self.dragY)) == True:
					self.X = self.dragX
					self.Y = self.dragY
					self.rect.x = self.X
					self.rect.y = self.Y
					self.location = i
			if mouseButtons[0] == True:
				self.dragX = mousePos[0] + self.dragDifX
				self.dragY = mousePos[1] + self.dragDifY

			if mouseButtons[0] == False:
				self.dragged = False
				self.dragX = self.X
				self.dragY = self.Y
				self.dragDifX = None
				self.dragDifY = None

	def draw(
		self, Pos, Size
	):  # pass None for size and pos if you want unchanged size and pos
		if Size == None:
			Size = self.size[:]
		if Pos == None:
			Pos = [self.dragX, self.dragY]
		drawSprite = pygame.transform.scale(self.sprite, (Size))
		gameDisplay.blit(drawSprite, Pos)


SAVE["sailors"] = [sailor(3), sailor(2), sailor(2)]
for i in range(len(SAVE["sailors"])):
	SAVE["sailors"][i].setPos((i * 50) + 150, displayHeight * 0.7)


class wave:
	def __init__(self, X, Y):
		self.X = X
		self.Y = Y
		self.size = 0
		self.dir = "up"
		self.colour = (50, 60, 200)
		self.delete = False
		self.surface = pygame.Surface((8, 4))
		self.timer = 0

	def draw(self):
		self.timer += frameTime
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

		self.X += math.sin(MAP["WindDir"]) * MAP["WindSpeed"] * frameTime
		self.Y += math.cos(MAP["WindDir"]) * MAP["WindSpeed"] * frameTime
		gameDisplay.blit(
			MAP.waves[self.size],
			(self.X - MAP["ScreenPos"][0], self.Y - MAP["ScreenPos"][1]),
		)


def dist(point1, point2):
	X = abs(point1[0] - point2[0])
	Y = abs(point1[1] - point2[1])
	return math.sqrt(X ** 2 + Y ** 2)


class PirateShip:
	def __init__(
		self, X, Y, power
	):  # Power 5-10 very small,  10-20 small, 20-35 med 35-50 large, boss is 60
		self.X = X
		self.Y = Y
		while testCollision((self.X, self.Y), True) == True:
			self.X += 25
		self.goingTo = []
		self.findRoute()
		self.speed = (power + 75) / 7
		self.state = "wander"  # Can also be attack and retreat
		self.dir = 0
		self.HP = power * 10
		self.maxHP = power * 10
		self.hovered = False
		self.cargo = {}

		if power >= 5 and power < 10:
			self.type = "tiny"
		if power >= 10 and power < 20:
			self.type = "small"
		if power >= 20 and power < 35:
			self.type = "med"
		if power >= 35 and power < 50:
			self.type = "large"
		if power == 60:
			self.type = "boss"

	def findRoute(self):
		self.goingTo = [
			random.randint(0, MAP["AreaSize"][0]),
			random.randint(0, MAP["AreaSize"][1]),
		]
		while True:
			self.goingTo = [
				random.randint(0, MAP["AreaSize"][0]),
				random.randint(0, MAP["AreaSize"][1]),
			]  # can make a addition to self.pos to increase chance of found path
			if self.checkPath(self.goingTo) == True:
				break

	def checkPath(self, going):
		x, y = self.X, self.Y
		while dist((x, y), going) > 50:
			if x > going[0]:
				x -= 12
			if x < going[0]:
				x += 12
			if y > going[1]:
				y -= 12
			if y < going[1]:
				y += 12
			if testCollision((x, y), True):
				return False
		return True

	def AI(self):
		if dist((self.X, self.Y), (self.goingTo[0], self.goingTo[1])) < 50:
			if self.state == "wander":
				self.findRoute()
		else:
			if self.X > self.goingTo[0]:
				self.X -= frameTime * self.speed
				# self.dir = 3
			if self.X < self.goingTo[0]:
				self.X += frameTime * self.speed
				# self.dir = 1
			if self.Y > self.goingTo[1]:
				self.Y -= frameTime * self.speed
				# self.dir = 0
			if self.Y < self.goingTo[1]:
				self.Y += frameTime * self.speed
				# self.dir = 2
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
			pygame.draw.rect(
				gameDisplay,
				(0, 0, 0),
				(self.drawX - 5, self.drawY - 10, (self.HP / self.maxHP) * 40, 5),
			)
		else:
			self.hovered = False
		if (
			self.drawX > -20
			and self.drawX < displayWidth + 20
			and self.drawY > -20
			and self.drawY < displayHeight + 20
		):  # this for some reason makes it run 10-20% worse
			gameDisplay.blit(
				MAP["pirateShipsSprites"][self.type][self.dir], (self.drawX, self.drawY)
			)


MAP["Text"]["Gold"] = text("Gold: "+str(SAVE["gold"]), displayWidth*0.075, displayHeight*0.03, 20, (0,0,0))

# GAME STATES (Functions)
def map():
	startFunc = time.time()
	global MAP
	global gameState
	MAP["MiniMapDrawList"] = {}
	gameDisplay.fill((0, 0, 200))

	if MAP["SparkleType"] == 0:
		MAP["WaterReflectionsPos"][0] -= (
			MAP["PlayerSpeed"][0] + MAP["WindSpeed"] * frameTime
		)
		MAP["WaterReflectionsPos"][1] -= MAP["PlayerSpeed"][1]

		gameDisplay.blit(
			MAP["WaterReflections"][round(MAP["WaterReflectionsCount"] * 4)],
			(MAP["WaterReflectionsPos"][0], MAP["WaterReflectionsPos"][1]),
		)
		MAP["WaterReflectionsCount"] += (
			abs(MAP["PlayerSpeed"][0])
			+ abs(MAP["PlayerSpeed"][1])
			+ MAP["WindSpeed"] * frameTime
		) / 20
		if MAP["WaterReflectionsCount"] > (len(MAP["WaterReflections"]) * 0.25) - 0.75:
			MAP["WaterReflectionsCount"] = -0.5
		if MAP["lastReflectSprite"] != round(MAP["WaterReflectionsCount"] * 4):
			MAP["WaterReflectionsPos"] = [0, 0]
		MAP["lastReflectSprite"] = round(MAP["WaterReflectionsCount"] * 4)

	if MAP["SparkleType"] == 1:
		for i in range(len(MAP["Sparkles"])):
			MAP["Sparkles"][i].do(
				(
					-MAP["PlayerSpeed"][0] * frameTime * 30,
					-MAP["PlayerSpeed"][1] * frameTime * 30,
				)
			)

	pygame.draw.rect(
		gameDisplay,
		(0, 0, 0),
		(
			-MAP["ScreenPos"][0],
			-MAP["ScreenPos"][1],
			MAP["AreaSize"][0],
			MAP["AreaSize"][1],
		),
		5,
	)
	pygame.draw.line(
		gameDisplay,
		(0, 0, 0),
		(0 - MAP["ScreenPos"][0], 0 - MAP["ScreenPos"][1]),
		(
			MAP["AreaSize"][0] - MAP["ScreenPos"][0],
			MAP["AreaSize"][1] - MAP["ScreenPos"][1],
		),
	)
	pygame.draw.line(
		gameDisplay,
		(0, 0, 0),
		(MAP["AreaSize"][0] - MAP["ScreenPos"][0], 0 - MAP["ScreenPos"][1]),
		(0 - MAP["ScreenPos"][0], MAP["AreaSize"][1] - MAP["ScreenPos"][1]),
	)
	if (
		abs(sum(MAP["PlayerSpeed"]))
		< MAP["Stats"]["speed"][MAP["PlayerLevels"]["speed"]] * 2
	):
		if Keys["W"] == True:
			MAP["PlayerSpeed"][1] -= (
				frameTime * MAP["Stats"]["speed"][MAP["PlayerLevels"]["speed"]]
			)
			MAP["PlayerDir"] = 2

		if Keys["A"] == True:
			MAP["PlayerSpeed"][0] -= (
				frameTime * MAP["Stats"]["speed"][MAP["PlayerLevels"]["speed"]]
			)
			MAP["PlayerDir"] = 0

		if Keys["S"] == True:
			MAP["PlayerSpeed"][1] += (
				frameTime * MAP["Stats"]["speed"][MAP["PlayerLevels"]["speed"]]
			)
			MAP["PlayerDir"] = 6

		if Keys["D"] == True:
			MAP["PlayerSpeed"][0] += (
				frameTime * MAP["Stats"]["speed"][MAP["PlayerLevels"]["speed"]]
			)
			MAP["PlayerDir"] = 4

		if Keys["W"] == True and Keys["D"] == True:
			MAP["PlayerDir"] = 4  # 3

		if Keys["D"] == True and Keys["S"] == True:
			MAP["PlayerDir"] = 4  # 5

		if Keys["S"] == True and Keys["A"] == True:
			MAP["PlayerDir"] = 0  # 7

		if Keys["A"] == True and Keys["W"] == True:
			MAP["PlayerDir"] = 0  # 1

	MAP["PlayerSpeed"][0] -= MAP["PlayerSpeed"][0] * frameTime
	MAP["PlayerSpeed"][1] -= MAP["PlayerSpeed"][1] * frameTime

	MAP["PlayerPos"][0] += MAP["PlayerSpeed"][0] * frameTime * 30

	# Collisions
	collideTemp = testCollision(MAP["PlayerPos"], False)
	if collideTemp == True or collideTemp == "port":
		MAP["PlayerSpeed"][0] = -MAP["PlayerSpeed"][0] * 1
		MAP["PlayerPos"][0] += MAP["PlayerSpeed"][0] * frameTime * 30

	MAP["PlayerPos"][1] += MAP["PlayerSpeed"][1] * frameTime * 30
	collideTemp = testCollision(MAP["PlayerPos"], False)
	if collideTemp == True or collideTemp == "port":
		MAP["PlayerSpeed"][1] = -MAP["PlayerSpeed"][1] * 1
		MAP["PlayerPos"][1] += MAP["PlayerSpeed"][1] * frameTime * 30

	MAP["ScreenPos"] = [
		MAP["PlayerPos"][0] - displayWidth / 2,
		MAP["PlayerPos"][1] - displayHeight / 2,
	]
	# Logic
	# Into fight
	for i in range(len(MAP["PirateShips"])):
		if MAP["PirateShips"][i].hovered == True:
			distance = dist(
				(round(MAP["PlayerPos"][0]), round(MAP["PlayerPos"][1])),
				(MAP["PirateShips"][i].X, MAP["PirateShips"][i].Y),
			)
			if distance < 100 and mouseButtons[0] == True:
				PREP["Enemy"] = copy.copy(MAP["PirateShips"][i])
				gameState = "Prep"
				F.text["cannonballAmmo"] = text(str(SAVE["inventory"]["cannonballs"]), 20, -20,  10, (0,0,0))
				slotButtons["cannon"].changeDraw([F["drawImages"]["cannonball"].draw, F.text["cannonballAmmo"].XYdraw])
				F.text["bulletAmmo"] = text(str(SAVE["inventory"]["bullets"]), 20, -20,  10, (0,0,0))
				slotButtons["swivel"].changeDraw([F["drawImages"]["bullets"].draw, F.text["bulletAmmo"].XYdraw])
				# Drawing
				# Waves
	MAP["WaveSpawnTimer"] += frameTime
	if MAP["WaveSpawnTimer"] > 0.1:
		MAP["WaveSpawnTimer"] = 0
		MAP["waveList"].append(
			wave(
				MAP["PlayerPos"][0]
				+ random.randint(-displayWidth / 2 - 50, displayWidth / 2 + 50),
				MAP["PlayerPos"][1]
				+ random.randint(-displayHeight / 2 - 50, displayHeight / 2 + 50),
			)
		)
	for i in range(len(MAP["waveList"])):
		MAP["waveList"][i].draw()
	waveDeleter()

	# Land
	for pos in MAP["LandBlocks"]:
		if MAP["LandBlocks"][pos] == 1:  # sand
			colour = (0, 0, 200)#(220, 220, 2)
		elif MAP["LandBlocks"][pos] == 2:  # grass
			colour = (0, 150, 0)
		elif MAP["LandBlocks"][pos] == 3:  # town
			colour = (210, 105, 30)
		elif MAP["LandBlocks"][pos] == 4:
			colour = (5, 5, 5)

		x = int(pos.split(",")[0])
		y = int(pos.split(",")[1])
		drawX = x - MAP["ScreenPos"][0]
		drawY = y - MAP["ScreenPos"][1]

		if (
			drawX > -25
			and drawX < displayWidth
			and drawY > -25
			and drawY < displayHeight
		):
			pygame.draw.rect(gameDisplay, (colour), (drawX, drawY, 25, 25))
	
	#new land
	for i in range(len(MAP["DrawList"])):
		MAP["DrawList"][i].run()

	# Pirates
	for i in range(len(MAP["PirateShips"])):
		MAP["PirateShips"][i].AI()
		MAP["PirateShips"][i].X
		MAP["PirateShips"][i].draw()
		# Player
	drawShip = MAP["ships"][MAP["PlayerDir"]]
	gameDisplay.blit(
		drawShip,
		(
			MAP["PlayerPos"][0] - MAP["ScreenPos"][0] - 15,
			MAP["PlayerPos"][1] - MAP["ScreenPos"][1] - 15,
		),
	)
	pygame.draw.rect(
		gameDisplay,
		(0, 0, 0),
		(
			MAP["PlayerPos"][0] - MAP["ScreenPos"][0],
			MAP["PlayerPos"][1] - MAP["ScreenPos"][1],
			5,
			5,
		),
	)
	# Ui
	startMap = time.time()
	MapUI([MAP["WindDir"], MAP["WindSpeed"]], MAP["PirateShips"])
	mapTime = time.time() - startMap


global mapTime
mapTime = 0.1


def menu():
	global gameState
	# Display Assets
	gameDisplay.fill((154, 219, 235))
	playButton = gameDisplay.blit(MENU["ButtonPlay"], (275, 255))
	optionsButton = gameDisplay.blit(MENU["ButtonOptions"], (275, 377))
	quitButton = gameDisplay.blit(MENU["ButtonQuit"], (275, 500))

	"""Add code"""
	if playButton.collidepoint(mousePos[0], mousePos[1]) and mouseButtons[0]:
		gameState = "Map"
	if optionsButton.collidepoint(mousePos[0], mousePos[1]) and mouseButtons[0]:
		gameState = "Options"
	if quitButton.collidepoint(mousePos[0], mousePos[1]) and mouseButtons[0]:
		pygame.mouse.set_visible(True)
		pygame.quit()
		quit()


def optionsPage():
	gameDisplay.fill((154, 219, 235))
	###################################


class shard:
	def __init__(self, X, Y, vel):
		self.X, self.Y = X, Y
		angle = (random.random() - 0.5) * math.pi * 2
		self.Xvol = math.sin(angle) * random.randint(vel * 0.2, vel * 1.5)
		self.Yvol = math.cos(angle) * random.randint(vel * 0.2, vel * 1.5)
		self.destory = False

	def run(self):
		self.X += self.Xvol * frameTime * 20
		self.Y += self.Yvol * frameTime * 20
		self.Yvol += frameTime * 30
		self.Xvol -= self.Xvol * frameTime * 0.5
		self.Yvol -= self.Yvol * frameTime * 0.5
		if self.X > displayWidth or self.X < 0 or self.Y > displayHeight or self.Y < 0:
			self.destory = True
		self.draw()

	def draw(self):
		pygame.draw.circle(gameDisplay, (100, 50, 0), (int(self.X), int(self.Y)), 3)

F.cannonballExplosion = [loadImage("fightAssets/cannonExplosion/0.png"),
loadImage("fightAssets/cannonExplosion/1.png"),
loadImage("fightAssets/cannonExplosion/2.png"),
loadImage("fightAssets/cannonExplosion/3.png"),
loadImage("fightAssets/cannonExplosion/4.png")]

for i in range(len(F.cannonballExplosion)):
	F.cannonballExplosion[i] = drawImage(F.cannonballExplosion[i])
	F.cannonballExplosion[i].resize(32, 32)
F.bulletExplosion = []
class explosion:
	def __init__(self, Type, X, Y):
		if Type == 1:
			self.frames = F.cannonballExplosion
			self.timePerFrame = 0.1
		elif Type == 2:
			self.frames = F.bulletExplosion
			self.timePerFrame = 0.1
		self.frame = 0
		self.timeRunning = 0
		self.X = X
		self.Y = Y
		self.destory = False

	def run(self):
		self.timeRunning += frameTime
		self.frame = math.floor(self.timeRunning / self.timePerFrame)
		if self.frame >= len(self.frames):
			self.destory = True
		else:
			self.frames[self.frame].draw(self.X, self.Y)

class bullet:
	def __init__(self, X, Y, Xvol, Yvol, Type):
		self.X, self.Y = X, Y
		self.Xvol, self.Yvol = Xvol, Yvol
		self.explode = False
		self.destory = False
		self.type = Type  # 1 for cannonball 2 for bullet

	def run(self):
		self.X += self.Xvol * frameTime * 20
		self.Y += self.Yvol * frameTime * 20
		self.Yvol += frameTime * 30
		pygame.draw.rect(gameDisplay, (0, 0, 0), (600, 400, 100, 500), 3)
		if self.explode == True:
			global F
			if self.type == 1:
				for i in range(20):
					F.projectiles.append(shard(self.X, self.Y, 30))
				self.destory = True
			elif self.type == 2:
				for i in range(2):
					F.projectiles.append(shard(self.X, self.Y, 10))
				self.destory = True
		if self.checkCollide([pygame.Rect(600, 400, 100, 500)]):
			if self.type == 1:
				shakeController(
					[random.random() * 5 - 2.5, random.random() * 5 - 2.5], 0.3
				)
			elif self.type == 2:
				shakeController(
					[random.random() - 0.5, random.random() - 0.5], 0.1
				)
			self.explode = True
			self.Xvol = 0
			self.Yvol = 0

		if self.X > displayWidth or self.X < 0 or self.Y > displayHeight:
			self.destory = True
		self.draw()

	def checkCollide(self, rectList):
		hit = False
		for i in range(len(rectList)):
			if rectList[i].collidepoint((self.X, self.Y)) == True:
				hit = True
		return hit

	def draw(self):
		if self.destory == False:
			if self.explode == False:
				if self.type == 1:
					F["drawImages"]["cannonball"].draw(self.X, self.Y)
				else:
					F["drawImages"]["bullet"].draw(self.X, self.Y)
			else:
				F.projectiles.append(explosion(self.type, self.X, self.Y))

def drawCooldown(cooldown, totalCooldown, rect):
	part = cooldown / totalCooldown
	if part>=0:
		pygame.draw.rect(gameDisplay, (200, 200, 200), (rect.x, rect.y + rect.h, rect.w, -rect.h*part))

class button:
	def __init__(
		self, X, Y, W, H, draw, shadowColour, buttonColour, ability
	):  # draw should be a list of functions that take X, Y to be drawn on the button
		self.X = X
		self.Y = Y
		self.W = W
		self.H = H
		self.rect = pygame.Rect(X, Y, W, H)
		self.drawList = draw
		self.pressed = False
		self.released = False
		self.colours = [shadowColour, buttonColour]
		self.ability = ability

	def run(self, down):
		if self.released == True:
			self.released = False
			self.pressed = False

		if self.rect.collidepoint(mousePos) == True:
			if mouseButtons[0] == True:
				self.draw((1, 1))
				self.pressed = True
			else:
				if self.pressed == True:
					self.released = True
				self.draw((4, 4))
		else:
			self.pressed = False
			self.released = False
			if down == True:
				self.draw((3, 3))
			else:
				self.draw((5, 5))
		return self.released

	def draw(self, hover):
		pygame.draw.rect(
			gameDisplay, self.colours[0], (self.X, self.Y, self.W, self.H), 10
		)
		pygame.draw.rect(
			gameDisplay,
			self.colours[1],
			(self.X + hover[0], self.Y + hover[1], self.W, self.H),
		)
		if self.ability == "cannon":
			drawCooldown(F.cannonTimer, 1.5, pygame.Rect(self.X+hover[0], self.Y+hover[1], self.W, self.H))
		elif self.ability == "bullets":
			drawCooldown(F.swivelTimer, 0.2, pygame.Rect(self.X+hover[0], self.Y+hover[1], self.W, self.H))
		for i in range(len(self.drawList)):
			self.drawList[i](
				self.X + self.W / 2 + hover[0], self.Y + self.H / 2 + hover[1]
			)

	def changeDraw(self, drawList):
		self.drawList = drawList


def destroyProjectiles():
	for i in range(len(F.projectiles)):
		if F.projectiles[i].destory == True:
			del F.projectiles[i]
			destroyProjectiles()
			break


F["images"] = {
	"cannonball": loadImage("fightAssets/cannon_ball.png"),
	"bullets": loadImage("fightAssets/bullets.png"),
	"bullet": loadImage("fightAssets/bullet.png"),
	"nuclearBomb": loadImage("fightAssets/nuclear_bomb.png"),
	"net": loadImage("fightAssets/net.png"),
}



F["drawImages"] = {
	"cannonball": drawImage(F["images"]["cannonball"]),
	"bullets": drawImage(F["images"]["bullets"]),
	"bullet" : drawImage(F["images"]["bullet"]),
	"nuclearBomb": drawImage(F["images"]["nuclearBomb"]),
	"net": drawImage(F["images"]["net"]),
}

F["drawImages"]["cannonball"].resize(32, 32)
F["drawImages"]["net"].resize(32, 32)
F["drawImages"]["bullets"].resize(32, 32)
F["drawImages"]["bullet"].resize(24, 24)
F["drawImages"]["nuclearBomb"].resize(32, 32)
for item in list(F["images"].keys()):
	F["images"][item] = pygame.transform.scale(
		F["images"][item], (round(displayWidth * 0.06), int(displayWidth * 0.06))
	)


F.text = {}
F.text["cannonballAmmo"] = text(str(SAVE["inventory"]["cannonballs"]), 20, -20,  10, (0,0,0))
F.text["bulletAmmo"] = text(str(SAVE["inventory"]["bullets"]), 20, -20, 10, (0,0,0))

slotButtons = {
	"cannon": button(
		displayWidth * 0.05,
		displayHeight * 0.9,
		displayWidth * 0.07,
		displayWidth * 0.07,
		[F["drawImages"]["cannonball"].draw, F.text["cannonballAmmo"].XYdraw],
		(0, 0, 0),
		(250, 250, 250),
		"cannon"
	),
	"swivel": button(
		displayWidth * 0.17,
		displayHeight * 0.9,
		displayWidth * 0.07,
		displayWidth * 0.07,
		[F["drawImages"]["bullets"].draw, F.text["bulletAmmo"].XYdraw],
		(0, 0, 0),
		(255, 255, 255),
		"bullets"
	),
	"nuclearBomb": button(
		displayWidth * 0.29,
		displayHeight * 0.9,
		displayWidth * 0.07,
		displayWidth * 0.07,
		[F["drawImages"]["nuclearBomb"].draw],
		(0, 0, 0),
		(255, 255, 255),
		"bomb"
	),
	"net": button(
		displayWidth * 0.44,
		displayHeight * 0.9,
		displayWidth * 0.07,
		displayWidth * 0.07,
		[F["drawImages"]["net"].draw],
		(0, 0, 0),
		(255, 255, 255),
		"net"
	),
}

F.placeHolders = [
	loadImage("fightAssets/background.png"),
	loadImage("fightAssets/friendlyShip.png"),
	loadImage("fightAssets/enemyShip.png"),
]
F.mode = "nothing"
F.pressed = True
F.projectiles = []
F.swivelTimer = 0
F.cannonTimer = 0

def battleScreen():
	gameDisplay.fill((255, 255, 255))
	# Display Assets
	gameDisplay.blit(F.placeHolders[0], (0, 0))
	gameDisplay.blit(F.placeHolders[1], (50, 250))
	gameDisplay.blit(F.placeHolders[2], (585, 250))

	if F.mode == "cannon":
		if mouseButtons[0] == True and F.cannonTimer < 0:
			x = displayWidth * 0.2 - mousePos[0]
			y = displayHeight * 0.6 - mousePos[1]
			angle = -math.atan2(y, x) + math.pi / 2
			xvol = math.sin(angle) * 65
			yvol = math.cos(angle) * 65
			pygame.draw.line(
				gameDisplay,
				(100, 100, 100),
				(displayWidth * 0.2, displayHeight * 0.6),
				(displayWidth * 0.2 + xvol * 7, displayHeight * 0.6 + yvol * 7),
			)
			F.pressed = True
		elif F.pressed == True:
			x = displayWidth * 0.2 - mousePos[0]
			y = displayHeight * 0.6 - mousePos[1]
			angle = -math.atan2(y, x) + math.pi / 2
			xvol = math.sin(angle) * 55
			yvol = math.cos(angle) * 55
			if SAVE["inventory"]["cannonballs"] > 0:
				SAVE["inventory"]["cannonballs"]-=1
				F.text["cannonballAmmo"] = text(str(SAVE["inventory"]["cannonballs"]), 20, -20,  10, (0,0,0))
				slotButtons["cannon"].changeDraw([F["drawImages"]["cannonball"].draw, F.text["cannonballAmmo"].XYdraw])
				F.projectiles.append(
					bullet(displayWidth * 0.2, displayHeight * 0.6, xvol, yvol, 1)
				)
				shakeController([random.random() * 2 - 1, random.random() * 2 - 1], 0.2)
				F.cannonTimer = 1.5
			F.pressed = False

	if F.mode == "swivel":
		if mouseButtons[0] == True and F.swivelTimer < 0:
			x = displayWidth * 0.2 - mousePos[0]
			y = displayHeight * 0.6 - mousePos[1]
			angle = -math.atan2(y, x) + math.pi / 2
			angle += (random.random()-0.5) / 5
			xvol = math.sin(angle) * 40
			yvol = math.cos(angle) * 40
			if SAVE["inventory"]["bullets"] > 0:
				SAVE["inventory"]["bullets"]-=1
				F.text["bulletAmmo"] = text(str(SAVE["inventory"]["bullets"]), 20, -20, 10, (0,0,0))
				slotButtons["swivel"].changeDraw([F["drawImages"]["bullets"].draw, F.text["bulletAmmo"].XYdraw])
				F.projectiles.append(
					bullet(displayWidth * 0.2, displayHeight * 0.6, xvol, yvol, 2)
				)
				shakeController([random.random() - 0.5, random.random() - 0.5], 0.1)
				F.swivelTimer = 0.05
			else:
				F.swivelTimer = 0.05

	F.swivelTimer -= frameTime
	F.cannonTimer -= frameTime

	for i in slotButtons:
		if F.mode == i:
			if slotButtons[i].run(True) == True:
				F.mode = "nothing"
		else:
			if slotButtons[i].run(False) == True:
				F.mode = i

	for i in range(len(F.projectiles)):
		F.projectiles[i].run()
	destroyProjectiles()


def cutScene():  # Need to make
	global gameState
	gameState = "shop"


SHOP["Text"]["Speed"] = {}
for i in range(len(SHOP["UpgradeCosts"]["speed"])):
	SHOP["Text"]["Speed"][i] = text(
		"Speed: " + str(SHOP["UpgradeCosts"]["speed"][i]),
		0,
		0,
		25,
		(10, 10, 10),
	)

SHOP["Text"]["Armor"] = {}
for i in range(len(SHOP["UpgradeCosts"]["armor"])):
	SHOP["Text"]["Armor"][i] = text(
		"Armor: " + str(SHOP["UpgradeCosts"]["armor"][i]),
		0,
		0,
		25,
		(10, 10, 10),
	)
#epic
SHOP["Text"]["HP"] = {}
for i in range(len(SHOP["UpgradeCosts"]["HP"])):
	SHOP["Text"]["HP"][i] = text(
		"HP: " + str(SHOP["UpgradeCosts"]["HP"][i]),
		0,
		0,
		29,
		(10, 10, 10),
	)

SHOP["Text"]["Upgrades"] = text(
	"Upgrades", displayWidth * 0.2, displayHeight * 0.3, 35, (20, 20, 0)
)
SHOP["Text"]["Shop"] = text(
	"Shop", displayWidth * 0.5, displayHeight * 0.26, 40, (20, 20, 0)
)
SHOP["Text"]["Items"] = text(
	"Items", displayWidth * 0.75, displayHeight * 0.3, 35, (20, 20, 0)
)
SHOP["Text"]["Crew"] = text(
	"Crew", displayWidth * 0.5, displayHeight * 0.6, 35, (20, 20, 0)
)
SHOP["Text"]["Cannonball"] = text("10G", 0, 25, 10, (20, 20, 20))

SHOP["Buttons"] = {}
SHOP["Buttons"]["Speed"] = button(
	displayHeight * 0.1,
	displayWidth * 0.3,
	200,
	40,
	[SHOP["Text"]["Speed"][MAP["PlayerLevels"]["speed"]].XYdraw],
	(20, 20, 0),
	(100, 75, 50),
	False
)
SHOP["Buttons"]["Armor"] = button(
	displayHeight * 0.1,
	displayWidth * 0.375,
	200,
	40,
	[SHOP["Text"]["Armor"][MAP["PlayerLevels"]["armor"]].XYdraw],
	(20, 20, 0),
	(100, 75, 50),
	False
)
SHOP["Buttons"]["HP"] = button(
	displayHeight * 0.1,
	displayWidth * 0.45,
	150,
	40,
	[SHOP["Text"]["HP"][MAP["PlayerLevels"]["HP"]].XYdraw],
	(20, 20, 0),
	(100, 75, 50),
	False
)
SHOP["Buttons"]["cannonball"] = button(displayWidth*0.6, displayHeight*0.4, 60, 60, [SHOP["Text"]["Cannonball"].XYdraw, F.drawImages["cannonball"].draw], (20, 20, 0), (100, 75, 50), False)

def shop():
	gameDisplay.blit(MAP["BuyBoard"], (0, 0))
	hover = (5, 5)
	if (
		pygame.Rect(displayWidth * 0.05 + 5, 29, 60, 60).collidepoint(
			mousePos[0], mousePos[1]
		)
		== True
	):
		if mouseButtons[0] == True:
			global gameState
			gameState = "Map"
		hover = (2, 2)
	pygame.draw.rect(
		gameDisplay,
		(50, 50, 0),
		(displayWidth * 0.05 + hover[0], 24 + hover[1], 60, 60),
	)
	gameDisplay.blit(SHOP["shopXbutton"], (displayWidth * 0.05, 0))
	if Keys["Esc"]:
		gameState = "Map"
	SHOP["Text"]["Upgrades"].draw()
	SHOP["Text"]["Shop"].draw()
	SHOP["Text"]["Items"].draw()
	SHOP["Text"]["Crew"].draw()

	if SHOP["Buttons"]["cannonball"].run(False) == True:
		SAVE["inventory"]["cannonballs"]+=1
		SAVE["gold"] -= 10
		print(SAVE["gold"])

	if (
		SHOP["Buttons"]["Speed"].run(False) == True
		and MAP["PlayerLevels"]["speed"] < len(MAP["UpgradeCosts"]["speed"]) - 1
	):
		MAP["PlayerLevels"]["speed"] += 1
		SHOP["Buttons"]["Speed"].changeDraw(
			[SHOP["Text"]["Speed"][MAP["PlayerLevels"]["speed"]].XYdraw]
		)
	if (
		SHOP["Buttons"]["Armor"].run(False) == True
		and MAP["PlayerLevels"]["armor"] < len(MAP["UpgradeCosts"]["armor"]) - 1
	):
		MAP["PlayerLevels"]["armor"] += 1
		SHOP["Buttons"]["Armor"].changeDraw(
			[SHOP["Text"]["Armor"][MAP["PlayerLevels"]["armor"]].XYdraw]
		)
	if (
		SHOP["Buttons"]["HP"].run(False) == True
		and MAP["PlayerLevels"]["HP"] < len(MAP["UpgradeCosts"]["HP"]) - 1
	):
		MAP["PlayerLevels"]["HP"] += 1
		SHOP["Buttons"]["HP"].changeDraw(
			[SHOP["Text"]["HP"][MAP["PlayerLevels"]["HP"]].XYdraw]
		)


### Other funtions ###
def waveDeleter():
	global MAP
	for i in range(len(MAP["waveList"])):
		if MAP["waveList"][i].delete == True:
			del MAP["waveList"][i]
			waveDeleter()
			break


def miniMap(windDir, windSpeed, zoom):
	center = (round(displayWidth * 0.1), round(displayHeight * 0.9))
	pygame.draw.circle(
		gameDisplay,
		(30, 50, 230),
		(center[0], center[1]),
		round(displayWidth * 0.07),
		0,
	)
	for pos in MAP["LandBlocks"]:
		x = int(pos.split(",")[0])
		y = int(pos.split(",")[1])
		if dist((x, y), MAP["PlayerPos"]) < zoom * 0.07 * 780:  # adding to minimap
			drawX = int(x) - MAP["PlayerPos"][0]
			drawY = int(y) - MAP["PlayerPos"][1]
			drawX = (drawX / zoom) + center[0]
			drawY = (drawY / zoom) + center[1]
			pygame.draw.rect(
				gameDisplay,
				(0, 0, 0),
				(drawX, drawY, round(25 / zoom) + 1, round(25 / zoom) + 1),
			)
	for i in range(len(MAP["PirateShips"])):
		x = MAP["PirateShips"][i].X
		y = MAP["PirateShips"][i].Y
		if dist((x, y), MAP["PlayerPos"]) < zoom * 0.07 * 780:  # adding to minimap
			drawX = int(x) - MAP["PlayerPos"][0]
			drawY = int(y) - MAP["PlayerPos"][1]
			drawX = (drawX / zoom) + center[0]
			drawY = (drawY / zoom) + center[1]
			pygame.draw.rect(
				gameDisplay,
				(255, 0, 0),
				(drawX, drawY, round(25 / zoom) + 1, round(25 / zoom) + 1),
			)

	pygame.draw.circle(
		gameDisplay, (0, 0, 0), (center[0], center[1]), round(displayWidth * 0.07), 5
	)
	lineP1 = (math.sin(windDir) * windSpeed * 2, math.cos(windDir) * windSpeed * 2)
	pygame.draw.line(
		gameDisplay,
		(100, 100, 120),
		(lineP1[0] + center[0], lineP1[1] + center[1]),
		(center[0], center[1]),
		3,
	)

MAP["GoldCoin"] = loadImage("mapAssets/coin.png")
MAP["GoldCoin"] = pygame.transform.scale(MAP["GoldCoin"], (32, 32))

def MapUI(wind, pirateShips):
	if gameState == "Map":
		MAP["Text"]["Gold"].draw()
		gameDisplay.blit(MAP["GoldCoin"], (displayWidth*0.15, displayHeight*0.005))
		miniMap(wind[0], wind[1], 25)
	if gameState == "Prep":
		prepMenu(SAVE, PREP["Enemy"].cargo)
	if gameState == "shop":
		MAP["Text"]["Gold"].draw()
		shop()


PREP["Text"]["Prepare"] = text(
	"Prepare for battle", displayWidth * 0.55, displayHeight * 0.2, 25, (20, 20, 0)
)
PREP["Text"]["Cargo"] = text(
	"Cargo hold", displayWidth * 0.3, displayHeight * 0.3, 20, (20, 20, 0)
)
PREP["Text"]["Deck"] = text(
	"On deck", displayWidth * 0.7, displayHeight * 0.3, 20, (20, 20, 0)
)
PREP["Text"]["Living"] = text(
	"Living quarters", displayWidth * 0.3, displayHeight * 0.6, 20, (20, 20, 0)
)
PREP["Text"]["Fight"] = text(
	"Fight", displayWidth * 0.9, displayHeight * 0.95, 10, (0, 0, 0)
)


def prepMenu(playerCargo, enemyCargo):
	global gameState
	gameDisplay.blit(PREP["Paper"], (0, 0))
	# GAme prints cause serious performace issues
	PREP["Text"]["Prepare"].draw()
	PREP["Text"]["Cargo"].draw()
	PREP["Text"]["Deck"].draw()
	PREP["Text"]["Living"].draw()
	pygame.draw.rect(
		gameDisplay,
		(10, 200, 30),
		(
			displayWidth * 0.85,
			displayHeight * 0.9,
			displayWidth * 0.14,
			displayHeight * 0.09,
		),
	)
	PREP["Text"]["Fight"].draw()
	if (
		PREP["FightButtonRect"].collidepoint(mousePos[0], mousePos[1])
		and mouseButtons[0] == True
	):
		for i in range(len(playerCargo["sailors"])):
			if playerCargo["sailors"][i].location == 0:
				SAVE["inventory"]["sailors"].append(playerCargo["sailors"][i])
		gameState = "Fight"
	if Keys["Esc"]:
		gameState = "Map"
	dropRects = [
		pygame.Rect(
			displayWidth * 0.6,
			displayWidth * 0.3,
			displayWidth * 0.2,
			displayHeight * 0.1,
		),
		pygame.Rect(
			displayWidth * 0.1,
			displayHeight * 0.7,
			displayWidth * 0.3,
			displayHeight * 0.1,
		),
	]
	for i in range(len(playerCargo["sailors"])):
		playerCargo["sailors"][i].logic(
			dropRects
		)  # give a list of rects that you can drop at
		playerCargo["sailors"][i].draw(None, None)


def QUIT():
	pygame.quit()
	exit()


shakeEndTimer = 0


def shakeController(shake, timer):
	global shakePos
	global shakeVol
	global shakeEndTimer

	shakeVol[0] += shake[0]
	shakeVol[1] += shake[1]

	shakePos[0] += shakeVol[0]
	shakePos[1] += shakeVol[1]

	if shakePos[1] > -0:
		shakeVol[1] -= frameTime * 50
	elif shakePos[1] < 0:
		shakeVol[1] += frameTime * 50
	if shakePos[0] > -0:
		shakeVol[0] -= frameTime * 50
	elif shakePos[0] < 0:
		shakeVol[0] += frameTime * 50
	shakeVol[0] -= shakeVol[0] * frameTime * 1
	shakeVol[1] -= shakeVol[1] * frameTime * 1

	if timer != None:
		shakeEndTimer = timer
	shakeEndTimer -= frameTime
	if shakeEndTimer < 0:
		shakeVol = [0, 0]
		shakePos = [0, 0]

	if round(shakeVol[0] * 5) == 0 and round(shakeVol[1] * 5) == 0:
		shakeVol = [0, 0]


for i in range(12):  # Creaing pirate ships in the map
	MAP["PirateShips"].append(
		PirateShip(
			random.randint(0, MAP["AreaSize"][0]),
			random.randint(0, MAP["AreaSize"][1]),
			random.randint(5, 19),
		)
	)

loadTime = time.time()-startLoad
print(loadTime)
# Main Loop
while True:
	startFrame = time.time()
	mouseButtons = pygame.mouse.get_pressed()  # (left mouse button, middle, right)
	mousePos = pygame.mouse.get_pos()  # (x, y)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			QUIT()

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_w:
				Keys["W"] = True
			if event.key == pygame.K_a:
				Keys["A"] = True
			if event.key == pygame.K_s:
				Keys["S"] = True
			if event.key == pygame.K_d:
				Keys["D"] = True
			if event.key == pygame.K_f:
				print(clock.get_fps())
			if event.key == pygame.K_ESCAPE:
				Keys["Esc"] = True

		if event.type == pygame.KEYUP:
			if event.key == pygame.K_w:
				Keys["W"] = False
			if event.key == pygame.K_a:
				Keys["A"] = False
			if event.key == pygame.K_s:
				Keys["S"] = False
			if event.key == pygame.K_d:
				Keys["D"] = False
			if event.key == pygame.K_ESCAPE:
				Keys["Esc"] = False
			
	if gameState == "Cutscene":
		cutScene()
	if gameState == "Menu":
		menu()
	if gameState == "Map" or gameState == "Prep" or gameState == "shop":
		map()
	if gameState == "Fight":
		battleScreen()

	shakeController([0, 0], None)

	screenDisplay.blit(gameDisplay, shakePos)
	pygame.display.update()
	clock.tick()
	frameTime = time.time() - startFrame