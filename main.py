
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
pygame.display.set_caption("probrobly a pirate game")
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

Keys = {"W": False, "A": False, "S": False, "D": False, "E": False, "Esc" : False, "Space" : False}
#SAVE["inventory"] = SAVE["inventory"]
#SAVE["inventory"] = {"sailors": [], "cannonballs": 10, "nets": 3, "bullets" : 20}

#Sounds
F.sounds = {"cannon" : pygame.mixer.Sound("fightAssets/cannon.wav"),
"nuke" : pygame.mixer.Sound("fightAssets/nuke.wav"),
"swivel" : pygame.mixer.Sound("fightAssets/swivel.wav")}
MAP["Music"] = pygame.mixer.music.load("mapAssets/mapMusic.wav")

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
	"armor": [4, 2, 1.5, 1, 0.2],
	"HP": [50, 75, 100, 150, 200, 250, 350, 400, 500],
}
MAP["PlayerLevels"] = {"speed": 0, "armor": 0, "HP": 0}
MAP["PlayerStats"] = {
	"speed": MAP["Stats"]["speed"][MAP["PlayerLevels"]["speed"]],
	"armor": MAP["Stats"]["armor"][MAP["PlayerLevels"]["armor"]],
	"HP": MAP["Stats"]["HP"][MAP["PlayerLevels"]["HP"]],
	"maxHP" : MAP["Stats"]["HP"][MAP["PlayerLevels"]["HP"]]
}
SHOP["UpgradeCosts"] = {
	"speed": [100, 500, 1200, 9999, "max"],
	"armor": [200, 1000, 2000, 9999, "max"],
	"HP": [50, 100, 200, 500, 1000, 1500, 9999, "max"],
}
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
		if MAP["LandBlocks"][i] == 2:
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

			#if sideCovered == 3:

			#if sideCovered == 4:
			MAP["DrawList"].append(tile(int(X), int(Y), "mapAssets/Land/Grass/0.png", random.randint(-2, 1)*90))

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
MAP.warningSprite = loadImage("mapAssets/warning.png")
MAP.warningSprite = pygame.transform.scale(MAP.warningSprite, (16, 16))
MAP.levelSprites = [loadImage("mapAssets/levels/1.png"),
loadImage("mapAssets/levels/2.png"),
loadImage("mapAssets/levels/3.png"),
loadImage("mapAssets/levels/4.png"),]
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

for i in range(len(MAP.ships)):
	size = MAP.ships[i].get_size()
	MAP.ships[i] = pygame.transform.scale(MAP.ships[i], (size[0]*2, size[1]*2))

MAP.waves = [
	loadImage("mapAssets/Waves/wave1.png"),
	loadImage("mapAssets/Waves/wave2.png"),
	loadImage("mapAssets/Waves/wave3.png"),
	loadImage("mapAssets/Waves/wave4.png"),
]

MAP["pirateShipsSprites"] = {
	"tiny": [
		loadImage("mapAssets/Pirates/tiny/W.png"),
		loadImage("mapAssets/Pirates/tiny/N.png"),
		loadImage("mapAssets/Pirates/tiny/E.png"),
		loadImage("mapAssets/Pirates/tiny/S.png"),
	],
	"small": [
		loadImage("mapAssets/Pirates/small/W.png"),
		loadImage("mapAssets/Pirates/small/N.png"),
		loadImage("mapAssets/Pirates/small/E.png"),
		loadImage("mapAssets/Pirates/small/S.png"),
	],
	"medium": [
		loadImage("mapAssets/Pirates/medium/W.png"),
		loadImage("mapAssets/Pirates/medium/N.png"),
		loadImage("mapAssets/Pirates/medium/E.png"),
		loadImage("mapAssets/Pirates/medium/S.png"),
	],
	"large": [
		loadImage("mapAssets/Pirates/large/W.png"),
		loadImage("mapAssets/Pirates/large/N.png"),
		loadImage("mapAssets/Pirates/large/E.png"),
		loadImage("mapAssets/Pirates/large/S.png"),
	],
}

for i in MAP["pirateShipsSprites"].keys():
	for l in range(len(MAP["pirateShipsSprites"][i])):
		MAP["pirateShipsSprites"][i][l] = pygame.transform.scale(MAP["pirateShipsSprites"][i][l], (64,64))

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

def blit_alpha(target, source, location, opacity):
    x = location[0]
    y = location[1]
    temp = pygame.Surface((source.get_width(), source.get_height())).convert()
    temp.blit(target, (-x, -y))
    temp.blit(source, (0, 0))
    temp.set_alpha(opacity)
    target.blit(temp, location)

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
	def __init__(self, level):
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

		self.rect = self.sprite.get_rect()
		self.rect.size = self.size
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

#SAVE["sailors"] = [sailor(3), sailor(2), sailor(2)]
#for i in range(len(SAVE["sailors"])):
#	SAVE["sailors"][i].setPos((i * 50) + 150, displayHeight * 0.7)

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

MAP.barrelSprites = [loadImage("mapAssets/barrel/0.png"), loadImage("mapAssets/barrel/1.png")]
MAP.barrels = []
MAP.barrelCreateTimer = random.randint(5, 10)
MAP.barrelText = text("click to pick up", 0, -10, 10, (0,0,0))

class barrel:
	def __init__(self):
		self.X = random.randint(0, MAP["AreaSize"][0])
		self.Y = random.randint(0, MAP["AreaSize"][1])
		self.drawX = self.X - MAP["PlayerPos"][0]
		self.drawY = self.Y - MAP["PlayerPos"][1]
		while testCollision((self.X, self.Y), True) == False:
			self.X = random.randint(0, MAP["AreaSize"][0])
			self.Y = random.randint(0, MAP["AreaSize"][1])
		self.frameTime = 0.5
		self.time = 0
		self.frame = 0
		self.sprites = [
		loadImage("mapAssets/barrel/0.png"),
		loadImage("mapAssets/barrel/1.png")
		]
		self.delete = False

	def checkMouse(self):
		if self.drawX > 0 and self.drawX < displayWidth and self.drawY > 0 and self.drawY < displayHeight:
			if dist((self.drawX, self.drawY), (mousePos[0], mousePos[1])) < 50:
				MAP.barrelText.XYdraw(self.drawX, self.drawY)
				if mouseButtons[0] == True:
					global SAVE 
					SAVE["gold"] += random.randint(5, 20)
					MAP["Text"]["Gold"] = text("Gold: "+str(SAVE["gold"]), displayWidth*0.075, displayHeight*0.03, 15, (0,0,0))
					self.delete = True

	def run(self):
		self.time +=frameTime
		self.frame = round(self.time % self.frameTime)
		self.draw()
		self.checkMouse()

	def draw(self):
		self.drawX = self.X - MAP["PlayerPos"][0]
		self.drawY = self.Y - MAP["PlayerPos"][1]
		gameDisplay.blit(MAP.barrelSprites[self.frame], (self.drawX, self.drawY))

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
		self.goldGiven = (random.random()+1) * power * 5

		if power >= 5 and power < 10:
			self.type = "tiny"
		if power >= 10 and power < 20:
			self.type = "small"
		if power >= 20 and power < 35:
			self.type = "medium"
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
			if self.maxHP > SAVE["inventory"]["cannonballs"]*12:
				gameDisplay.blit(MAP.warningSprite, (self.drawX + 5, self.drawY - 25))
		else:
			self.hovered = False
		if (
			self.drawX > -40
			and self.drawX < displayWidth + 20
			and self.drawY > -40
			and self.drawY < displayHeight + 20
		):
			gameDisplay.blit(
				MAP["pirateShipsSprites"][self.type][self.dir], (self.drawX, self.drawY)
			)

MAP["inventoryUI"] = {}
MAP["inventoryUI"]["up"] = 0 #ranges from 0 - 1
def inventoryUI():
	pygame.draw.rect(gameDisplay, (139,69,19), (displayWidth*0.8, (displayHeight - (MAP["inventoryUI"]["up"] * displayHeight * 0.1))-5, displayWidth*0.19, 1000))
	if MAP["inventoryUI"]["up"] > 0.5:
		if mousePos[0] > displayWidth * 0.8 and mousePos[1] > displayHeight * 0.9:
			if MAP["inventoryUI"]["up"] < 1:
				MAP["inventoryUI"]["up"] += frameTime * 5
			F["drawImages"]["bullets"].draw(displayWidth*0.83, displayHeight*0.96)
			F.text["bulletAmmo"].XYdraw(displayWidth*0.81, displayHeight*0.94)

			F["drawImages"]["cannonball"].draw(displayWidth*0.88, displayHeight*0.96)
			F.text["cannonballAmmo"].XYdraw(displayWidth*0.86, displayHeight*0.94)

			F["drawImages"]["nuclearBomb"].draw(displayWidth*0.93, displayHeight*0.96)
			F.text["nukeAmmo"].XYdraw(displayWidth*0.91, displayHeight*0.94)
		else:
			if MAP["inventoryUI"]["up"] > 0:
				MAP["inventoryUI"]["up"] -= frameTime * 5
			else:
				MAP["inventoryUI"]["up"] = 0
	else:
		if SAVE["inventory"]["cannonballs"] * 10 < MAP["PlayerStats"]["maxHP"]+50:
			gameDisplay.blit(MAP["warningSprite"], (displayWidth*0.88, displayWidth-30))
			print("cannonballs warning")

		if SAVE["inventory"]["bullets"] * 1 < MAP["PlayerStats"]["maxHP"]:
			gameDisplay.blit(MAP["warningSprite"], (displayWidth*0.83, displayWidth-30))
			print("bullets warning")

		#dont need a warning for nukes

		if mousePos[0] > displayWidth * 0.8 and mousePos[1] > displayHeight * 0.95:
			MAP["inventoryUI"]["up"] += frameTime * 5
		else:
			if MAP["inventoryUI"]["up"] > 0:
				MAP["inventoryUI"]["up"] -= frameTime * 5
			else:
				MAP["inventoryUI"]["up"] = 0

MAP["Text"]["Gold"] = text("Gold: "+str(SAVE["gold"]), displayWidth*0.075, displayHeight*0.03, 15, (0,0,0))

# GAME STATES (Functions)
def map():
	startFunc = time.time()
	global MAP
	global gameState
	global slotButtons
	global F
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
		MAP["PlayerSpeed"][0] = -MAP["PlayerSpeed"][0] * 1.0
		MAP["PlayerPos"][0] += MAP["PlayerSpeed"][0] * frameTime * 30

	MAP["PlayerPos"][1] += MAP["PlayerSpeed"][1] * frameTime * 30
	collideTemp = testCollision(MAP["PlayerPos"], False)
	if collideTemp == True or collideTemp == "port":
		MAP["PlayerSpeed"][1] = -MAP["PlayerSpeed"][1] * 1.0
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
				gameState = "Fight"
				F.text["cannonballAmmo"] = text(str(SAVE["inventory"]["cannonballs"]), 20, -20,  10, (0,0,0))
				slotButtons["cannon"].changeDraw([F["drawImages"]["cannonball"].draw, F.text["cannonballAmmo"].XYdraw])
				F.text["bulletAmmo"] = text(str(SAVE["inventory"]["bullets"]), 20, -20,  10, (0,0,0))
				slotButtons["swivel"].changeDraw([F["drawImages"]["bullets"].draw, F.text["bulletAmmo"].XYdraw])
				F.text["nukeAmmo"] = text(str(SAVE["inventory"]["nukes"]), 20, -20, 10, (0,0,0))
				slotButtons["nuclearBomb"].changeDraw([F["drawImages"]["nuclearBomb"].draw, F.text["nukeAmmo"].XYdraw])
				F.enemieStats = MAP["PirateShips"][i]
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

	#barrels
	MAP.barrelCreateTimer -= frameTime
	if MAP.barrelCreateTimer < 0:
		MAP.barrels.append(barrel())
		MAP.barrelCreateTimer = random.randint(5, 10)

	for i in range(len(MAP.barrels)):
		MAP.barrels[i].run()

	i = 0
	while i < len(MAP.barrels):
		if MAP.barrels[i].delete == True:
			del MAP.barrels[i]
			break
		i+=1
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
		gameState = "Help"
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

F.nuclearExplosion = [loadImage("fightAssets/NukeExplosion/0.png"),
loadImage("fightAssets/NukeExplosion/1.png"),
loadImage("fightAssets/NukeExplosion/2.png"),
loadImage("fightAssets/NukeExplosion/3.png"),
loadImage("fightAssets/NukeExplosion/4.png"),
loadImage("fightAssets/NukeExplosion/5.png"),
loadImage("fightAssets/NukeExplosion/6.png")
]
F.bulletExplosion = []
for i in range(len(F.nuclearExplosion)):
	F.nuclearExplosion[i] = drawImage(F.nuclearExplosion[i])
	F.nuclearExplosion[i].resize(512, 512)

for i in range(len(F.cannonballExplosion)):
	F.cannonballExplosion[i] = drawImage(F.cannonballExplosion[i])
	F.cannonballExplosion[i].resize(32, 32)

class explosion:
	def __init__(self, Type, X, Y):
		if Type == 1:
			self.frames = F.cannonballExplosion
			self.timePerFrame = 0.1
		elif Type == 2:
			self.frames = F.bulletExplosion
			self.timePerFrame = 0.1
		elif Type == 3:
			self.timePerFrame = 0.2
			self.frames = F.nuclearExplosion
		self.frame = 0
		self.timeRunning = 0
		self.X = X
		self.Y = Y
		self.destory = False
		self.flashBrightness = 255
		self.Type = Type

	def run(self):
		self.timeRunning += frameTime
		self.frame = math.floor(self.timeRunning / self.timePerFrame)
		self.flashBrightness -= frameTime * 255 * 1
		if self.frame >= len(self.frames):
			self.destory = True
		else:
			self.frames[self.frame].draw(self.X, self.Y)
		if self.Type == 3:
			nukeSurf.set_alpha(self.flashBrightness)
			gameDisplay.blit(nukeSurf, (0,0))

nukeSurf = pygame.Surface((displayWidth, displayHeight))
nukeSurf.fill((255,255,255))
nukeSurf.set_alpha(255)
class nuke:
	def __init__(self, X):
		self.X = X - displayWidth*0.075
		self.targetX = X
		self.Y = 0
		self.destory = False

	def run(self):
		self.X += displayWidth * 0.1 * frameTime
		self.Y += displayHeight * frameTime
		if self.Y>displayHeight*0.7:
			pygame.mixer.Sound.play(F.sounds["nuke"])
			self.destory = True
			F.projectiles.append(explosion(3, self.X, displayHeight-256))
			shakeController([random.random() * 10 -5, random.random() * 10 -5], 2)
			F.enemieStats.HP -= random.randint(200,220)
		self.draw()

	def draw(self):
		F["drawImages"]["nuclearBomb"].draw(self.X, self.Y)

class bullet:
	def __init__(self, X, Y, Xvol, Yvol, Type, shotBy):
		self.X, self.Y = X, Y
		self.Xvol, self.Yvol = Xvol, Yvol
		self.explode = False
		self.destory = False
		self.type = Type  # 1 for cannonball 2 for bullet
		self.shotBy = shotBy #either player of enemey

	def run(self):
		self.X += self.Xvol * frameTime * 20
		self.Y += self.Yvol * frameTime * 20
		self.Yvol += frameTime * 30
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
		if self.shotBy == "player":
			rect = pygame.Rect(550, 350, 200, 500)
		else:
			rect = pygame.Rect(100, 400, 100, 500)

		if self.checkCollide([rect]):
			if self.type == 1:
				shakeController(
					[random.random() * 5 - 2.5, random.random() * 5 - 2.5], 0.3
				)
			elif self.type == 2:
				shakeController(
					[random.random() *0.5- 0.25, random.random()*0.5 - 0.25], 0.05
				)
			self.explode = True
			self.Xvol = 0
			self.Yvol = 0

		if F.sheildPower > 0.2 and self.X < 300:
			self.Xvol -= self.Xvol * frameTime * 10

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
				if self.type == 1:
					if self.shotBy == "player":
						F.enemieStats.HP -= random.randint(8,15)
					else:
						MAP["PlayerStats"]["HP"] -= random.randint(8,15)
				elif self.type == 2:
					if self.shotBy == "player":
						F.enemieStats.HP -= round(random.random()-0.2)
					else:
						MAP["PlayerStats"]["HP"] -= round(random.random()-0.2)
				F.projectiles.append(explosion(self.type, self.X, self.Y))

def drawCooldown(cooldown, totalCooldown, rect):
	part = cooldown / totalCooldown
	if part>=0:
		pygame.draw.rect(gameDisplay, (200, 200, 200), (rect.x, rect.y + rect.h, rect.w, -rect.h*part))

F.babyFrames = [loadImage("fightAssets/baby0.png"), loadImage("fightAssets/baby1.png")]
F.babyFrames[0] = pygame.transform.scale(F.babyFrames[0], (64, 64))
F.babyFrames[1] = pygame.transform.scale(F.babyFrames[1], (64, 64))

class baby:
	def __init__(self, X, Y):
		self.X = X
		self.Y = Y
		self.destory = False
		self.frame = 0
		self.frameTime = 0
		self.wave = 0 #is sin ed to get the y pos
		self.HP = 10
	def run(self):
		self.frameTime += frameTime
		if self.frameTime >= 1:
			self.frameTime = 0
		elif self.frameTime >=0.5:
			self.frame = 1
		else:
			self.frame = 0

		self.X+=frameTime*5
		self.wave +=frameTime * 0.5
		drawY = self.Y + math.sin(self.wave * math.pi) * 20
		self.rect = pygame.Rect(self.X, drawY, 64, 64)
		self.checkCollide()
		if self.HP <= 0 :
			self.destory = True
		self.draw(self.X, drawY)

	def draw(self, X, Y):
		gameDisplay.blit(F.babyFrames[self.frame], (X, Y))

	def checkCollide(self):
		global F
		for i in range(len(F.projectiles)):
			if self.rect.collidepoint((F.projectiles[i].X, F.projectiles[i].Y)) and str(type(F.projectiles[i])) == "<class '__main__.bullet'>":
				F.projectiles[i].destory = True
				if F.projectiles[i].type == 1:
					self.HP -= 9
				else:
					self.HP -= 2
				break


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
			drawCooldown(F.swivelTimer, 0.05, pygame.Rect(self.X+hover[0], self.Y+hover[1], self.W, self.H))
		elif self.ability == "bomb":
			drawCooldown(F.nukeTimer, 30, pygame.Rect(self.X+hover[0], self.Y+hover[1], self.W, self.H))
		elif self.ability == "sheild":
			drawCooldown(F.sheildCooldown, F.lastSheildCooldown+0.0001,pygame.Rect(self.X+hover[0], self.Y+hover[1], self.W, self.H))
		elif self.ability == "BB":
			drawCooldown(F.BBcooldown, 7, pygame.Rect(self.X+hover[0], self.Y+hover[1], self.W, self.H))
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
	"sheildIcon": loadImage("fightAssets/sheild_icon.png"),
	"target" : loadImage("fightAssets/target.png"),
	"BB" : loadImage("fightAssets/baby_icon.png"),
	"player" : loadImage("fightAssets/ships/player.png"),
	"lvl1" : loadImage("fightAssets/ships/1.png"),
	"lvl2" : loadImage("fightAssets/ships/2.png"),
	"lvl3" : loadImage("fightAssets/ships/3.png"),
	"lvl4" : loadImage("fightAssets/ships/4.png"),
	"water" : pygame.Surface((displayWidth, displayWidth)),
	"sun": loadImage("fightAssets/sun.png")
}

F["images"]["sun"] = pygame.transform.scale(F["images"]["sun"], (64, 64))

F["images"]["lvl1"] = pygame.transform.scale(F["images"]["lvl1"], (512, 512))
F["images"]["lvl2"] = pygame.transform.scale(F["images"]["lvl2"], (512, 512))
F["images"]["lvl3"] = pygame.transform.scale(F["images"]["lvl3"], (512, 512))
F["images"]["lvl4"] = pygame.transform.scale(F["images"]["lvl4"], (512, 512))
F["images"]["player"] = pygame.transform.scale(F["images"]["player"], (512, 512))


F["images"]["water"].fill((0, 0, 150))
F["images"]["water"].set_alpha(100)


F["drawImages"] = {
	"cannonball": drawImage(F["images"]["cannonball"]),
	"bullets": drawImage(F["images"]["bullets"]),
	"bullet" : drawImage(F["images"]["bullet"]),
	"nuclearBomb": drawImage(F["images"]["nuclearBomb"]),
	"net": drawImage(F["images"]["net"]),
	"sheildIcon": drawImage(F["images"]["sheildIcon"]),
	"target":drawImage(F["images"]["target"]),
	"BB" : drawImage(F["images"]["BB"])
}


F["drawImages"]["target"].resize(64, 64)
F["drawImages"]["cannonball"].resize(32, 32)
F["drawImages"]["net"].resize(32, 32)
F["drawImages"]["bullets"].resize(32, 32)
F["drawImages"]["bullet"].resize(24, 24)
F["drawImages"]["nuclearBomb"].resize(32, 32)
F["drawImages"]["sheildIcon"].resize(32, 32)
F["drawImages"]["BB"].resize(32, 32)


F.text = {}
F.text["cannonballAmmo"] = text(str(SAVE["inventory"]["cannonballs"]), 20, -20,  10, (0,0,0))
F.text["bulletAmmo"] = text(str(SAVE["inventory"]["bullets"]), 20, -20, 10, (0,0,0))
F.text["nukeAmmo"] = text(str(SAVE["inventory"]["nukes"]), 20, -20, 10, (0,0,0))

F.text["victory"] = text("Victory", 0, 0, 40, (0, 200, 0))
F.text["deafeat"] = text("Defeat", 0, 0, 40, (200, 0, 0))


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
		[F["drawImages"]["nuclearBomb"].draw, F.text["nukeAmmo"].XYdraw],
		(0, 0, 0),
		(255, 255, 255),
		"bomb"
	),
	"BB": button( #ballon baby
		displayWidth * 0.44,
		displayHeight * 0.9,
		displayWidth * 0.07,
		displayWidth * 0.07,
		[F["drawImages"]["BB"].draw],
		(0, 0, 0),
		(255, 255, 255),
		"BB"
	),
	"sheild": button(
		displayWidth*0.9,
		displayHeight*0.9,
		displayWidth*0.07,
		displayHeight*0.07,
		[F["drawImages"]["sheildIcon"].draw],
		(0,0,0),
		(255, 255, 255),
		"sheild")
}

F.sheildImg = loadImage("fightAssets/sheild.png")
F.sheildImg = pygame.transform.scale(F.sheildImg, (512, 512))
F.mode = "nothing"
F.pressed = True
F.projectiles = []
F.swivelTimer = 0
F.cannonTimer = 0
F.nukeTimer = -0.1
F.enemeyShootTime = 3 - (150/100) #3 minus enemiey health /100
F.enemieyShootTimer = 0
F.enemieToShootBullet = 0
F.enemieBulletShootTimer = 0
F.sheildCooldown = 0
F.sheildUpFor = 0
F.sheildPower = 0
F.sheildTimer = 0
F.lastSheildCooldown = 0
F.BBcooldown = 0
F.winner = False
F.winTimer = 0
F.blockerRects = []

def battleScreen():
	global gameState
	global SAVE
	global MAP
	gameDisplay.fill((100, 100, 255))
	# Display Assets

	#drawing
	gameDisplay.blit(F["images"]["sun"], (displayWidth*0.1, displayHeight*0.1))
	gameDisplay.blit(F["images"]["water"], (0, displayHeight*0.7))
	gameDisplay.blit(F["images"]["player"], (-10 , displayHeight*0.4))

	if F.enemieStats.type == "tiny":
		gameDisplay.blit(F["images"]["lvl1"], (displayWidth*0.7 , displayHeight*0.4))
	elif F.enemieStats.type == "small":
		gameDisplay.blit(F["images"]["lvl2"], (displayWidth*0.7 , displayHeight*0.4))
	elif F.enemieStats.type == "medium":
		gameDisplay.blit(F["images"]["lvl3"], (displayWidth*0.7 , displayHeight*0.4))
	elif F.enemieStats.type == "large":
		gameDisplay.blit(F["images"]["lvl4"], (displayWidth*0.7 , displayHeight*0.4))

	if F.mode == "cannon":
		if mouseButtons[0] == True and F.cannonTimer < 0:
			x = displayWidth * 0.2 - mousePos[0]
			y = displayHeight * 0.6 - mousePos[1]
			angle = -math.atan2(y, x) - math.pi / 2
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
			angle = -math.atan2(y, x) - math.pi / 2
			xvol = math.sin(angle) * 55
			yvol = math.cos(angle) * 55
			if SAVE["inventory"]["cannonballs"] > 0:
				pygame.mixer.Sound.play(F.sounds["cannon"])
				SAVE["inventory"]["cannonballs"]-=1
				F.text["cannonballAmmo"] = text(str(SAVE["inventory"]["cannonballs"]), 20, -20,  10, (0,0,0))
				slotButtons["cannon"].changeDraw([F["drawImages"]["cannonball"].draw, F.text["cannonballAmmo"].XYdraw])
				F.projectiles.append(
					bullet(displayWidth * 0.2, displayHeight * 0.6, xvol, yvol, 1, "player")
				)
				shakeController([random.random() * 2 - 1, random.random() * 2 - 1], 0.2)
				F.cannonTimer = 1.5
			F.pressed = False

	if F.mode == "swivel":
		if mouseButtons[0] == True and F.swivelTimer < 0:
			x = displayWidth * 0.2 - mousePos[0]
			y = displayHeight * 0.6 - mousePos[1]
			angle = -math.atan2(y, x) - math.pi / 2
			angle += (random.random()-0.5) / 5
			xvol = math.sin(angle) * 40
			yvol = math.cos(angle) * 40
			if SAVE["inventory"]["bullets"] > 0:
				pygame.mixer.Sound.play(F.sounds["swivel"])
				SAVE["inventory"]["bullets"]-=1
				F.text["bulletAmmo"] = text(str(SAVE["inventory"]["bullets"]), 20, -20, 10, (0,0,0))
				slotButtons["swivel"].changeDraw([F["drawImages"]["bullets"].draw, F.text["bulletAmmo"].XYdraw])
				F.projectiles.append(
					bullet(displayWidth * 0.2, displayHeight * 0.6, xvol, yvol, 2, "player")
				)
				#shakeController([random.random() *0.5, random.random() - 0.5], 0.1)
				F.swivelTimer = 0.05
			else:
				F.swivelTimer = 0.05

	if F.mode == "nuclearBomb":
		if mouseButtons[0] == True and F.nukeTimer < 0 and SAVE["inventory"]["nukes"] > 0:
			F.projectiles.append(nuke(mousePos[0]))
			F.nukeTimer = 30
			SAVE["inventory"]["nukes"] -= 1
			F.text["nukeAmmo"] = text(str(SAVE["inventory"]["nukes"]), 20, -20, 10, (0,0,0))
			slotButtons["nuclearBomb"].changeDraw([F["drawImages"]["nuclearBomb"].draw, F.text["nukeAmmo"].XYdraw])
		F["drawImages"]["target"].draw(mousePos[0], 500)

	if F.mode == "BB":
		if mouseButtons[0] == True and F.BBcooldown < 0:
			F.projectiles.append(baby(displayWidth*0.2, mousePos[1]))
			F.BBcooldown = 7
		else:
			gameDisplay.blit(F.babyFrames[0], (displayWidth*0.2, mousePos[1]))

	if F.sheildCooldown <= 0:
		if Keys["Space"] == True:
			F.sheildUpFor += frameTime * MAP.PlayerStats["armor"]
			if F.sheildPower < 1:
				F.sheildPower += frameTime * 3
		else:
			F.sheildCooldown = F.sheildUpFor
			F.lastSheildCooldown = F.sheildUpFor
			F.sheildUpFor = 0
	if F.sheildPower > 0:
		F.sheildPower -= frameTime

	F.sheildCooldown -= frameTime
	F.swivelTimer -= frameTime
	F.cannonTimer -= frameTime
	F.nukeTimer -= frameTime
	F.BBcooldown -= frameTime

	F.enemeyShootTime = 5 - (F.enemieStats.HP / 100)
	F.enemieyShootTimer += frameTime
	if F.enemieyShootTimer > F.enemeyShootTime:
		F.enemieyShootTimer = 0
		xvol = -30
		yvol = (random.random()-0.5)*2
		if random.randint(0,1) == 0:
			F.enemieToShootBullet = random.randint(5, 10)
		else:
			F.projectiles.append(bullet(displayWidth * 0.7, displayHeight * 0.6, xvol, yvol, 1, "enemey"))

	if F.enemieToShootBullet > 0:
		if F.enemieBulletShootTimer < 0:
			xvol = -30
			yvol = (random.random()-0.5)*10
			F.projectiles.append(bullet(displayWidth * 0.7, displayHeight * 0.6, xvol, yvol, 2, "enemey"))
			F.enemieBulletShootTimer = 0.1
			F.enemieToShootBullet -= 1
		else:
			F.enemieBulletShootTimer -= frameTime

	if F.sheildPower > 0.05:
		blit_alpha(gameDisplay, F.sheildImg, (-170, 200), F.sheildPower*255)


	if F.winner == "player":
		F.text["victory"].XYdraw(displayWidth/2, displayHeight/2)

	if F.winner == "enemiey":
		F.text["deafeat"].XYdraw(displayWidth/2, displayHeight/2)

	if MAP["PlayerStats"]["HP"] < 0 and F.winner == False:
		F.winTimer = 3
		F.winner = "enemiey"

	if F.winner == "enemiey" and F.winTimer <0:
		gameState = "Map"
		MAP["PlayerStats"]["HP"] = MAP["PlayerStats"]["maxHP"]
		F.winner = False
		F.projectiles = []

	if F.enemieStats.HP < 0 and F.winner == False:
		F.winTimer = 3
		F.winner = "player"

	if F.winner == "player" and F.winTimer < 0:
		F.enemieStats.HP = F.enemieStats.maxHP
		MAP["PirateShips"].remove(F.enemieStats)
		gameState = "Map"
		SAVE["gold"] += round(F.enemieStats.goldGiven)
		MAP["Text"]["Gold"] = text("Gold: "+str(SAVE["gold"]), displayWidth*0.075, displayHeight*0.03, 15, (0,0,0))
		MAP["PlayerStats"]["HP"] = MAP["PlayerStats"]["maxHP"]
		MAP["PirateShips"].append(PirateShip(random.randint(0, MAP["AreaSize"][0]), random.randint(0, MAP["AreaSize"][1]), random.randint(5, 49)))
		F.projectiles = []
		F.winner = False

	F.winTimer -= frameTime
	F.text["myHP"] = text(str(MAP["PlayerStats"]["HP"]), displayWidth*0.3, displayHeight*0.2, 30, (0,0,0))
	F.text["enemyHP"] = text(str(F.enemieStats.HP), displayWidth*0.7, displayHeight*0.2, 30, (0,0,0))
	F.text["myHP"].draw()
	F.text["enemyHP"].draw()
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
	gameState = "Menu"


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
		"Sheild: " + str(SHOP["UpgradeCosts"]["armor"][i]),
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
SHOP["Text"]["Cannonball"] = text("10G", 0, 25, 10, (20, 20, 20))

SHOP["Text"]["Bullet"] = text("5G for 20", 0, 25, 8, (20, 20, 20))

SHOP["Text"]["Nuke"] = text("500G", 0, 25, 10, (20, 20, 20))

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

SHOP["Buttons"]["bullets"] = button(displayWidth*0.7, displayHeight*0.4, 60, 60, [SHOP["Text"]["Bullet"].XYdraw, F.drawImages["bullets"].draw], (20, 20, 0), (100, 75, 50), False)

SHOP["Buttons"]["Nuke"] = button(displayWidth * 0.6, displayHeight*0.6, 60, 60, [SHOP["Text"]["Nuke"].XYdraw, F.drawImages["nuclearBomb"].draw], (20, 20, 0), (100, 75, 50), False)

def shop():
	global SAVE, MAP, F
	gameDisplay.blit(MAP["BuyBoard"], (0, 0))
	hover = (5, 5)
	if (
		pygame.Rect(displayWidth * 0.9 + 5, 29, 60, 60).collidepoint(
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
		(displayWidth * 0.9, 24, 60, 60),
	)
	gameDisplay.blit(SHOP["shopXbutton"], (displayWidth * 0.9 + hover[0], 0 + hover[1]))
	if Keys["Esc"]:
		gameState = "Map"
	SHOP["Text"]["Upgrades"].draw()
	SHOP["Text"]["Shop"].draw()
	SHOP["Text"]["Items"].draw()

	if SHOP["Buttons"]["Nuke"].run(False) == True and SAVE["gold"]>=500:
		SAVE["gold"] -= 500
		SAVE["inventory"]["nukes"] += 1
		MAP["Text"]["Gold"] = text("Gold: "+str(SAVE["gold"]), displayWidth*0.075, displayHeight*0.03, 15, (0,0,0))

	if SHOP["Buttons"]["cannonball"].run(False) == True  and SAVE["gold"]>=10:
		SAVE["inventory"]["cannonballs"]+=1
		SAVE["gold"] -= 10
		MAP["Text"]["Gold"] = text("Gold: "+str(SAVE["gold"]), displayWidth*0.075, displayHeight*0.03, 15, (0,0,0))
	if SHOP["Buttons"]["bullets"].run(False) == True  and SAVE["gold"]>=5:
		SAVE["inventory"]["bullets"]+=20
		SAVE["gold"] -= 5
		MAP["Text"]["Gold"] = text("Gold: "+str(SAVE["gold"]), displayWidth*0.075, displayHeight*0.03, 15, (0,0,0))
	if (
		SHOP["Buttons"]["Speed"].run(False) == True
		and MAP["PlayerLevels"]["speed"] < len(MAP["UpgradeCosts"]["speed"]) - 1  and SAVE["gold"] >= SHOP["UpgradeCosts"]["speed"][MAP["PlayerLevels"]["speed"]]
	):
		MAP["PlayerLevels"]["speed"] += 1
		SHOP["Buttons"]["Speed"].changeDraw(
			[SHOP["Text"]["Speed"][MAP["PlayerLevels"]["speed"]].XYdraw]
		)
		SAVE["gold"] -= SHOP["UpgradeCosts"]["speed"][MAP["PlayerLevels"]["speed"]-1]
		MAP["Text"]["Gold"] = text("Gold: "+str(SAVE["gold"]), displayWidth*0.075, displayHeight*0.03, 15, (0,0,0))

	if (
		SHOP["Buttons"]["Armor"].run(False) == True
		and MAP["PlayerLevels"]["armor"] < len(MAP["UpgradeCosts"]["armor"]) - 1 and SAVE["gold"]>=SHOP["UpgradeCosts"]["armor"][MAP["PlayerLevels"]["armor"]]
	):
		MAP["PlayerLevels"]["armor"] += 1
		SHOP["Buttons"]["Armor"].changeDraw([SHOP["Text"]["Armor"][MAP["PlayerLevels"]["armor"]].XYdraw])
		SAVE["gold"] -= SHOP["UpgradeCosts"]["armor"][MAP["PlayerLevels"]["armor"]-1]
		MAP["Text"]["Gold"] = text("Gold: "+str(SAVE["gold"]), displayWidth*0.075, displayHeight*0.03, 15, (0,0,0))

	if (
		SHOP["Buttons"]["HP"].run(False) == True
		and MAP["PlayerLevels"]["HP"] < len(MAP["UpgradeCosts"]["HP"]) - 1 and SAVE["gold"] >= SHOP["UpgradeCosts"]["HP"][MAP["PlayerLevels"]["HP"]]
	):
		MAP["PlayerLevels"]["HP"] += 1
		SHOP["Buttons"]["HP"].changeDraw(
			[SHOP["Text"]["HP"][MAP["PlayerLevels"]["HP"]].XYdraw]
		)
		SAVE["gold"] -= SHOP["UpgradeCosts"]["HP"][MAP["PlayerLevels"]["HP"]-1]
		MAP["Text"]["Gold"] = text("Gold: "+str(SAVE["gold"]), displayWidth*0.075, displayHeight*0.03, 15, (0,0,0))
	MAP["PlayerStats"] = {
	"speed": MAP["Stats"]["speed"][MAP["PlayerLevels"]["speed"]],
	"armor": MAP["Stats"]["armor"][MAP["PlayerLevels"]["armor"]],
	"maxHP": MAP["Stats"]["HP"][MAP["PlayerLevels"]["HP"]],
	"HP" : MAP["Stats"]["HP"][MAP["PlayerLevels"]["HP"]]
	}

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
		gameDisplay.blit(MAP["GoldCoin"], (displayWidth*0.17, displayHeight*0.005))
		miniMap(0, 0, 25)
		inventoryUI()
	if gameState == "Prep":
		prepMenu(SAVE["inventory"], PREP["Enemy"].cargo)
	if gameState == "shop":
		shop()
		MAP["Text"]["Gold"].draw()
		gameDisplay.blit(MAP["GoldCoin"], (displayWidth*0.17, displayHeight*0.005))

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

tutorialFrame = 0
AtutorialPressed = False
DtutorialPressed = False
tutorialFrames = [loadImage("menuAssets/tutorial/hover.PNG"),
loadImage("menuAssets/tutorial/barrels.png"),
loadImage("menuAssets/tutorial/goToFight.png"),
loadImage("menuAssets/tutorial/tooHigh.png"),
loadImage("menuAssets/tutorial/shop.png"),
loadImage("menuAssets/tutorial/fightIntro.png"),
loadImage("menuAssets/tutorial/sheild.png")]

def tutorial():
	global tutorialFrame
	global gameState
	global DtutorialPressed
	global AtutorialPressed

	if Keys["Esc"] == True:
		gameState = "Menu"

	if Keys["D"] == True and DtutorialPressed == False:
		tutorialFrame += 1
		DtutorialPressed = True

	if Keys["D"] == False:
		DtutorialPressed = False

	if Keys["A"] == False:
		AtutorialPressed = False

	if Keys["A"] == True and AtutorialPressed == False:
		tutorialFrame -= 1
		AtutorialPressed = True

	if tutorialFrame > len(tutorialFrames)-1:
		gameState = "Menu"
		tutorialFrame = 0
	else:
		gameDisplay.blit(tutorialFrames[tutorialFrame], (0,0))


for i in range(12):  # Creaing pirate ships in the map
	MAP["PirateShips"].append(
		PirateShip(
			random.randint(0, MAP["AreaSize"][0]),
			random.randint(0, MAP["AreaSize"][1]),
			random.randint(5, 49),
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
			if gameState == "Fight":
				if event.key == pygame.K_1:
					F.mode = "cannon"
				if event.key == pygame.K_2:
					F.mode = "swivel"
				if event.key == pygame.K_3:
					F.mode = "nuclearBomb"
				if event.key == pygame.K_4:
					F.mode = "BB"
				if event.key == pygame.K_SPACE:
					Keys["Space"] = True

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
			if event.key == pygame.K_SPACE:
				Keys["Space"] = False

	if gameState == "Cutscene":
		cutScene()
	if gameState == "Menu":
		menu()
	if gameState == "Map" or gameState == "Prep" or gameState == "shop":
		map()
	if gameState == "Fight":
		battleScreen()
	if gameState == "Help":
		tutorial()

	shakeController([0, 0], None)

	screenDisplay.blit(gameDisplay, shakePos)
	pygame.display.update()
	clock.tick()
	frameTime = time.time() - startFrame