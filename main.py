import copy
import math
import time
import random
import pygame
import islands as islandData
import numpy as np

# Init
displayWidth, displayHeight = 800, 600
pygame.init()
screenDisplay = pygame.display.set_mode((displayWidth, displayHeight))
gameDisplay = pygame.Surface((displayWidth, displayHeight))
pygame.display.set_caption("aiden hasnt done anything")
clock = pygame.time.Clock()
loadImage = pygame.image.load

# AttrDict class
class AttrDict(dict):
	def __getattr__(self, attr):
		return self[attr]

	def __setattr__(self, attr, value):
		self[attr] = value


# Variables
global gameState
gameState = "Cutscene"
global MAP, MENU, F, PREP, SETTINGS
frameTime = 0
MAP = MENU = F = PREP = SHOP = SETTINGS = AttrDict({})
Keys = {"W": False, "A": False, "S": False, "D": False, "E": False}
F.inventory = {"sailors": [], "cannonballs": 0, "nets": 0}

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
MAP["PlayerCargo"] = {
	"cannonball": 5,
	"nets": 2,
	"cannon": 2,
	"sailors": [],
	"Gold": 100,
}  # Inventory
MAP["Stats"] = {
	"speed": [3, 5, 7, 10],
	"armor": [1.3, 1.15, 1, 0.8],
	"HP": [50, 60, 75, 100, 150, 250, 350, 500],
}
MAP["PlayerLevels"] = {"speed": 0, "armor": 0, "HP": 0}
MAP["PlayerStats"] = {
	"speed": MAP["Stats"]["speed"][MAP["PlayerLevels"]["speed"]],
	"armor": MAP["Stats"]["armor"][MAP["PlayerLevels"]["armor"]],
	"HP": MAP["Stats"]["HP"][MAP["PlayerLevels"]["HP"]],
}
SHOP["UpgradeCosts"] = {
	"speed": [100, 500, 1200, 3000],
	"armor": [200, 1000, 2000, 6000],
	"HP": [50, 100, 200, 500, 1000, 1500, 2000],
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
MAP["MiniMapDrawList"] = {}  # actually a dictionary but ctr + h is too hard`
# Land masses is a 400x300 array or dictionay
# 1 is sand, 2 is land, 3 is town and 4 is port
MAP.WaveSpawnTimer = 0
PREP.EnemyCargo = {}

shakePos = [0,0]
shakeVol = [random.random()*4-2, random.random()*4-2]
print(shakeVol)
# WaterReflections
if MAP["SparkleType"] == 0:
	for p in range(10):
		MAP["WaterReflections"].append(pygame.Surface((displayWidth, displayHeight)))
		MAP["WaterReflections"][-1].fill((0, 0, 200))
		for i in range(2000):
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
for i in range(random.randint(6, 10)):
	currentType = islandTypes[random.randint(0, len(islandTypes) - 1)]
	islandX, islandY = (
		random.randint(0, MAP["AreaSize"][0] / 25) * 25,
		random.randint(0, MAP["AreaSize"][1] / 25) * 25,
	)
	for block in currentType:
		x = int(block.split(",")[0])
		y = int(block.split(",")[1])
		newBlock = str(x + islandX) + "," + str(y + islandY)
		MAP["LandBlocks"][newBlock] = currentType[block]

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

PREP["Gun"] = loadImage("fightAssets/items/pistol.png")
PREP["CannonBall"] = loadImage("fightAssets/items/cannonBall.png")
PREP["Paper"] = loadImage("mapAssets/paper.png")
PREP["Paper"] = pygame.transform.scale(MAP["Paper"], (displayWidth, displayHeight))
PREP["FightButtonRect"] = pygame.Rect(
	displayWidth * 0.85, displayHeight * 0.9, displayWidth * 0.14, displayHeight * 0.09
)
PREP["Text"] = {}
PREP["Xbutton"] = loadImage("mapAssets/prepXbutton.png")


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
		self.checkMove()
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

	def changeMessage(self, newMessage, colour):
		self.messsage = newMessage
		self.surf, self.rect = text_objects(self.message, self.font, colour)
		self.rect.center = (self.X, self.Y)

	def draw(self):
		gameDisplay.blit(self.surf, self.rect)

		# def move(self, X, Y):
		# 	self.rect.center = (X, Y)


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


MAP["PlayerCargo"]["sailors"] = [sailor(3), sailor(2), sailor(2)]
for i in range(len(MAP["PlayerCargo"]["sailors"])):
	MAP["PlayerCargo"]["sailors"][i].setPos((i * 50) + 150, displayHeight * 0.7)


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


class PirateShip:
	def __init__(
		self, X, Y, power
	):  # Power 5-10 very small,  10-20 small, 20-35 med 35-50 large, boss is 60
		self.X = X
		self.Y = Y
		self.goingTo = [
			random.randint(0, MAP["AreaSize"][0]),
			random.randint(0, MAP["AreaSize"][1]),
		]
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

	def AI(self):
		if dist((self.X, self.Y), (self.goingTo[0], self.goingTo[1])) < 50:
			if self.state == "wander":
				self.goingTo = [
					random.randint(0, MAP["AreaSize"][0]),
					random.randint(0, MAP["AreaSize"][1]),
				]
		else:
			if self.X > self.goingTo[0]:
				self.X -= frameTime * self.speed
				self.dir = 3
			if self.X < self.goingTo[0]:
				self.X += frameTime * self.speed
				self.dir = 1
			if self.Y > self.goingTo[1]:
				self.Y -= frameTime * self.speed
				self.dir = 0
			if self.Y < self.goingTo[1]:
				self.Y += frameTime * self.speed
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


for i in range(10):
	MAP["PirateShips"].append(
		PirateShip(
			random.randint(0, MAP["AreaSize"][0]),
			random.randint(0, MAP["AreaSize"][1]),
			random.randint(5, 19),
		)
	)

# MAP["Text"]["Gold"] = text("Gold: "+str(MAP["Stat"]))

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
	if abs(sum(MAP["PlayerSpeed"])) < 4:
		if Keys["W"] == True:
			MAP["PlayerSpeed"][1] -= frameTime * 2
			MAP["PlayerDir"] = 2

		if Keys["A"] == True:
			MAP["PlayerSpeed"][0] -= frameTime * 2
			MAP["PlayerDir"] = 0

		if Keys["S"] == True:
			MAP["PlayerSpeed"][1] += frameTime * 2
			MAP["PlayerDir"] = 6

		if Keys["D"] == True:
			MAP["PlayerSpeed"][0] += frameTime * 2
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
	if (
		testCollision(MAP["PlayerPos"]) == True
		or testCollision((MAP["PlayerPos"][0] + 5, MAP["PlayerPos"][1])) == True
	):
		MAP["PlayerSpeed"][0] = -MAP["PlayerSpeed"][0] * 1
		MAP["PlayerPos"][0] += MAP["PlayerSpeed"][0] * frameTime * 30

	MAP["PlayerPos"][1] += MAP["PlayerSpeed"][1] * frameTime * 30

	if (
		testCollision(MAP["PlayerPos"]) == True
		or testCollision((MAP["PlayerPos"][0], MAP["PlayerPos"][1] + 5)) == True
	):
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
			colour = (220, 220, 10)
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


def drawCannonball(X, Y, size=10):
	pygame.draw.circle(gameDisplay, (0, 0, 0), (int(X), int(Y)), size)


class cannonBall:
	def __init__(self, X, Y, Xvol, Yvol):
		self.X, self.Y = X, Y
		self.Xvol, self.Yvol = Xvol, Yvol

	def run(self):
		self.X += self.Xvol * frameTime * 20
		self.Y += self.Yvol * frameTime * 20
		self.Yvol += frameTime * 30
		self.draw()

	def draw(self):
		drawCannonball(self.X, self.Y)


class button:
	def __init__(
		self, X, Y, W, H, draw
	):  # draw should be a list of functions that take X, Y to be drawn on the button
		self.X = X
		self.Y = Y
		self.W = W
		self.H = H
		self.rect = pygame.Rect(X, Y, W, H)
		self.drawList = draw

	def run(self):
		if self.rect.collidepoint(mousePos) == True:
			if mouseButtons[0] == True:
				self.draw((1, 1))
				return True
			else:
				self.draw((3, 3))
		else:
			self.draw((5, 5))
		return False

	def draw(self, hover):
		pygame.draw.rect(gameDisplay, (0, 0, 0), (self.X, self.Y, self.W, self.H), 10)
		pygame.draw.rect(
			gameDisplay,
			(255, 255, 255),
			(self.X + hover[0], self.Y + hover[1], self.W, self.H),
		)
		for i in range(len(self.drawList)):
			self.drawList[i](
				self.X + self.W / 2 + hover[0], self.Y + self.H / 2 + hover[1]
			)


slotButtons = {
	"cannon": button(
		displayWidth * 0.05,
		displayHeight * 0.9,
		displayWidth * 0.07,
		displayWidth * 0.07,
		[drawCannonball],
	)
}

F.placeHolders = [
	loadImage("fightAssets/background.png"),
	loadImage("fightAssets/friendlyShip.png"),
	loadImage("fightAssets/enemyShip.png"),
]
F.mode = "nothing"
F.pressed = True
F.projectiles = []


def battleScreen():
	gameDisplay.fill((255, 255, 255))
	# Display Assets
	gameDisplay.blit(F.placeHolders[0], (0, 0))
	gameDisplay.blit(F.placeHolders[1], (50, 250))
	gameDisplay.blit(F.placeHolders[2], (585, 250))
	for i in slotButtons:
		if slotButtons[i].run() == True:
			F.mode = i

	if F.mode == "cannon":
		if mouseButtons[0] == True:
			xvol = displayWidth * 0.2 - mousePos[0]
			yvol = displayHeight * 0.6 - mousePos[1]
			pygame.draw.line(
				gameDisplay,
				(100, 100, 100),
				(displayWidth * 0.2, displayHeight * 0.6),
				(displayWidth * 0.2 + xvol * 7, displayHeight * 0.6 + yvol * 7),
			)
			F.pressed = True
		elif F.pressed == True:
			xvol = displayWidth * 0.2 - mousePos[0]
			yvol = displayHeight * 0.6 - mousePos[1]
			F.projectiles.append(
				cannonBall(displayWidth * 0.2, displayHeight * 0.6, xvol, yvol)
			)
			shakeController([random.random()*4-2, random.random()*4-2], 0.5)
			F.pressed = False

	for i in range(len(F.projectiles)):
		F.projectiles[i].run()


def cutScene():  # Need to make
	global gameState
	gameState = "Menu"


SHOP["Text"]["Speed"] = text(
	"Speed: " + str(SHOP["UpgradeCosts"]["speed"][MAP["PlayerLevels"]["speed"]]),
	displayWidth * 0.3,
	displayHeight * 0.4,
	30,
	(10, 10, 10),
)
SHOP["Text"]["Armor"] = text(
	"Armor: " + str(SHOP["UpgradeCosts"]["armor"][MAP["PlayerLevels"]["armor"]]),
	displayWidth * 0.3,
	displayHeight * 0.5,
	30,
	(10, 10, 10),
)
SHOP["Text"]["HP"] = text(
	"HP: " + str(SHOP["UpgradeCosts"]["HP"][MAP["PlayerLevels"]["HP"]]),
	displayWidth * 0.3,
	displayHeight * 0.6,
	30,
	(10, 10, 10),
)


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
	SHOP["Text"]["Speed"].changeMessage(
		"Speed: " + str(SHOP["UpgradeCosts"]["speed"][MAP["PlayerLevels"]["speed"]]),
		(10, 10, 10),
	)
	SHOP["Text"]["Armor"].changeMessage(
		"Speed: " + str(SHOP["UpgradeCosts"]["armor"][MAP["PlayerLevels"]["armor"]]),
		(10, 10, 10),
	)
	SHOP["Text"]["HP"].changeMessage(
		"Speed: " + str(SHOP["UpgradeCosts"]["HP"][MAP["PlayerLevels"]["HP"]]),
		(10, 10, 10),
	)
	SHOP["Text"]["Speed"].draw()
	SHOP["Text"]["Armor"].draw()
	SHOP["Text"]["HP"].draw()


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


def MapUI(wind, pirateShips):
	if gameState == "Map":
		miniMap(wind[0], wind[1], 25)
	if gameState == "Prep":
		prepMenu(MAP["PlayerCargo"], PREP["Enemy"].cargo)
	if gameState == "shop":
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
				F.inventory["sailors"].append(playerCargo["sailors"][i])
		gameState = "Fight"

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


def dist(point1, point2):
	X = abs(point1[0] - point2[0])
	Y = abs(point1[1] - point2[1])
	return math.sqrt(X ** 2 + Y ** 2)


def testCollision(point):
	collide = islandArray[int(point[0] / 25)][int(point[1] / 25)]
	if collide == 4:
		global gameState
		gameState = "shop"
		return "port"
	elif collide != 0:
		return True
	else:
		return False


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
		shakeVol[1]-=frameTime * 50
	elif shakePos[1] < 0:
		shakeVol[1]+=frameTime * 50
	if shakePos[0] > -0:
		shakeVol[0]-=frameTime * 50
	elif shakePos[0] < 0:
		shakeVol[0]+=frameTime * 50
	shakeVol[0] -= shakeVol[0]*frameTime*1
	shakeVol[1] -= shakeVol[1]*frameTime*1

	if timer != None:
		shakeEndTimer = timer
	shakeEndTimer -= frameTime
	if shakeEndTimer < 0:
		shakeVol = [0,0]
		shakePos = [0,0]

	if round(shakeVol[0]*5) == 0 and round(shakeVol[1]*5) == 0:
		shakeVol = [0,0]



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

		if event.type == pygame.KEYUP:
			if event.key == pygame.K_w:
				Keys["W"] = False
			if event.key == pygame.K_a:
				Keys["A"] = False
			if event.key == pygame.K_s:
				Keys["S"] = False
			if event.key == pygame.K_d:
				Keys["D"] = False
	if gameState == "Cutscene":
		cutScene()
	if gameState == "Menu":
		menu()
	if gameState == "Map" or gameState == "Prep" or gameState == "shop":
		map()
	if gameState == "Fight":
		battleScreen()
	
	shakeController([0,0], None)

	screenDisplay.blit(gameDisplay, shakePos)
	pygame.display.update()
	clock.tick()
	frameTime = time.time() - startFrame
