import copy
import math
import time
import random
import pygame

# Init
displayWidth, displayHeight = 800, 600
pygame.init()
screenDisplay = pygame.display.set_mode((displayWidth, displayHeight))
pygame.display.set_caption("we still need a name for our game")
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
gameState = "Menu"
global MAP, MENU, F, PREP, SETTINGS
MAP = MENU = F = PREP = SETTINGS = AttrDict({})
Keys = {"W": False, "A": False, "S": False, "D": False, "E": False}
F.inventory = ["cannonball", "birb", "monkey"]

# MAP variables
MAP["PirateShips"] = []
MAP["AreaSize"] = [displayWidth * 3, displayHeight * 3]
MAP["PlayerPos"] = [MAP["AreaSize"][0] / 2, MAP["AreaSize"][0] / 2]
MAP["ScreenPos"] = [MAP["AreaSize"][0] / 2, MAP["AreaSize"][0] / 2]
MAP["PlayerSpeed"] = [0, 0]
MAP["PlayerDir"] = 0
MAP["PlayerCargo"] = {"cannonball": 5, "monkey": 1, "cannon": 2, "sailors": []}
MAP["ShipDrawPos"] = [displayWidth / 2, displayHeight / 2]
MAP["ActualDrawShip"] = MAP["ShipDrawPos"][:]
MAP["waveList"] = []
MAP["WindDir"] = (
	math.pi * 1.5
)  # random.randint(0, round(math.pi*2)) #in degrees beacuse its easier for me
MAP["WindSpeed"] = 20  # random.randint(1,10)
MAP["screenRect"] = pygame.Rect(-25, -25, displayWidth + 50, displayHeight + 50)
MAP["LandBlocks"] = {}  # List of all peices of land each land is 25x25px
MAP["MiniMapDrawList"] = {} #actually a dictionary but ctr + h is too hard`
# Land masses is a 400x300 array or dictionay
# 1 is sand, 2 is land, 3 is town and 4 is port
MAP.WaveSpawnTimer = 0

PREP.EnemyCargo = {}
# Random generation
islands = {}
# Virgin random generation
"""
islandNum=random.randint(5, 25)

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
	if random.randint(0,1)==0:
		x += random.randint(-1, 1)*25
	else:
		y += random.randint(-1, 1)*25
	if str(x)+","+str(y) in MAP["LandBlocks"]:
		pass
	else:
		MAP["LandBlocks"][str(x)+","+str(y)] = 2

for i in range(500):
	points = MAP["LandBlocks"].keys()
	points = list(points)
	point = random.choice(points)
	x = int(point.split(",")[0])
	y = int(point.split(",")[1])
	if random.randint(0,1)==0:
		x += random.randint(-1, 1)*25
	else:
		y += random.randint(-1, 1)*25
	if str(x)+","+str(y) in MAP["LandBlocks"]:
		pass
	else:
		MAP["LandBlocks"][str(x)+","+str(y)] = 1

for i in range(10):
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
		MAP["LandBlocks"][str(x)+","+str(y)] = 4
"""

# Chad random premade islands

islandTypes = [
	{
		"125,125": 2,
		"125,150": 2,
		"150,150": 2,
		"150,125": 2,
		"175,150": 2,
		"175,175": 2,
		"150,175": 2,
		"100,125": 1,
		"100,150": 1,
		"125,100": 1,
		"150,100": 1,
		"175,125": 1,
		"175,100": 1,
		"125,175": 1,
		"150,200": 1,
		"175,200": 1,
		"200,175": 1,
		"200,150": 1,
	},
	{
		"250,150": 2,
		"250,175": 2,
		"225,175": 2,
		"225,200": 2,
		"200,200": 2,
		"200,225": 2,
		"200,250": 2,
		"225,250": 2,
		"225,225": 2,
		"250,225": 2,
		"250,200": 2,
		"275,200": 2,
		"275,225": 2,
		"250,250": 2,
		"250,275": 3,
		"250,300": 3,
		"275,300": 2,
		"275,275": 2,
		"300,275": 2,
		"300,250": 2,
		"300,225": 2,
		"275,175": 2,
		"275,250": 2,
		"300,175": 2,
		"300,200": 2,
		"325,200": 2,
		"325,225": 2,
		"350,225": 2,
		"350,250": 2,
		"350,275": 2,
		"325,275": 2,
		"325,300": 2,
		"300,300": 2,
		"300,325": 2,
		"325,250": 2,
		"275,325": 2,
		"275,350": 2,
		"250,350": 2,
		"250,325": 2,
		"225,325": 2,
		"225,300": 3,
		"200,275": 2,
		"225,275": 2,
		"200,325": 2,
		"175,325": 2,
		"150,325": 2,
		"150,300": 2,
		"125,325": 2,
		"125,300": 2,
		"125,275": 2,
		"125,250": 2,
		"150,250": 2,
		"175,250": 2,
		"200,300": 2,
		"175,300": 2,
		"175,275": 2,
		"150,275": 2,
		"150,225": 1,
		"175,225": 2,
		"175,350": 2,
		"200,350": 2,
		"225,350": 2,
		"250,375": 2,
		"275,375": 2,
		"300,350": 2,
		"275,400": 2,
		"250,400": 2,
		"225,375": 2,
		"150,350": 2,
		"125,350": 2,
		"125,375": 2,
		"100,375": 2,
		"75,375": 2,
		"75,350": 2,
		"100,350": 2,
		"100,325": 2,
		"100,275": 2,
		"100,300": 2,
		"75,300": 2,
		"75,325": 2,
		"75,275": 2,
		"50,275": 2,
		"50,300": 2,
		"50,325": 2,
		"50,350": 2,
		"100,250": 2,
		"75,250": 2,
		"150,375": 1,
		"175,375": 1,
		"200,375": 1,
		"225,400": 1,
		"125,400": 1,
		"100,400": 1,
		"75,400": 1,
		"50,375": 1,
		"325,350": 1,
		"325,325": 1,
		"350,325": 1,
		"350,300": 1,
		"350,175": 1,
		"350,200": 1,
		"325,175": 1,
		"300,150": 1,
		"275,150": 1,
		"225,150": 1,
		"250,125": 1,
		"200,175": 1,
		"175,200": 1,
		"150,200": 1,
		"125,225": 1,
		"100,225": 1,
		"75,225": 1,
		"25,275": 1,
		"25,300": 1,
		"25,325": 1,
		"25,350": 1,
		"25,375": 1,
		"50,400": 1,
		"0,350": 1,
		"0,325": 1,
		"300,375": 4,
	},
	{
		"325,150": 2,
		"325,175": 2,
		"350,175": 2,
		"350,200": 2,
		"350,225": 2,
		"375,225": 2,
		"375,250": 2,
		"400,250": 2,
		"400,275": 2,
		"375,275": 2,
		"375,300": 2,
		"350,300": 2,
		"325,300": 2,
		"300,300": 2,
		"275,300": 2,
		"250,300": 2,
		"225,300": 2,
		"200,300": 2,
		"175,300": 2,
		"150,300": 2,
		"175,325": 2,
		"200,325": 2,
		"200,350": 2,
		"225,350": 2,
		"250,350": 2,
		"250,375": 2,
		"275,375": 2,
		"300,400": 2,
		"325,400": 2,
		"350,400": 2,
		"375,400": 2,
		"400,400": 2,
		"425,400": 2,
		"425,425": 2,
		"450,425": 2,
		"475,425": 2,
		"500,425": 2,
		"500,400": 2,
		"525,400": 2,
		"525,375": 2,
		"525,350": 2,
		"525,325": 2,
		"500,325": 2,
		"500,300": 2,
		"525,425": 2,
		"525,450": 2,
		"500,450": 2,
		"375,375": 2,
		"350,375": 2,
		"350,350": 2,
		"325,350": 2,
		"325,325": 2,
		"325,275": 2,
		"325,250": 2,
		"350,250": 2,
		"400,225": 2,
		"400,200": 2,
		"425,200": 2,
		"450,200": 2,
		"450,175": 2,
		"475,175": 2,
		"450,150": 2,
		"450,125": 2,
		"425,125": 2,
		"400,125": 2,
		"375,125": 2,
		"350,125": 2,
		"350,150": 2,
		"300,150": 2,
		"300,175": 2,
		"300,200": 2,
		"325,200": 2,
		"325,225": 2,
		"425,250": 2,
		"450,250": 2,
		"150,275": 2,
		"175,275": 2,
		"275,275": 2,
		"300,275": 2,
		"375,200": 2,
		"375,175": 2,
		"375,150": 2,
		"400,150": 2,
		"425,150": 2,
		"425,175": 2,
		"400,175": 2,
		"425,225": 2,
		"450,225": 2,
		"425,275": 2,
		"400,300": 1,
		"400,325": 1,
		"400,350": 2,
		"425,350": 1,
		"425,375": 2,
		"450,375": 2,
		"450,400": 2,
		"475,400": 2,
		"475,375": 2,
		"500,375": 2,
		"500,350": 2,
		"450,350": 1,
		"375,325": 3,
		"375,350": 3,
		"400,375": 2,
		"350,275": 2,
		"350,325": 2,
		"300,325": 2,
		"275,325": 2,
		"250,325": 2,
		"225,325": 2,
		"275,350": 2,
		"300,350": 2,
		"300,375": 2,
		"325,375": 2,
		"200,275": 1,
		"225,275": 1,
		"250,275": 1,
		"275,250": 1,
		"300,250": 1,
		"300,225": 1,
		"275,225": 1,
		"250,250": 1,
		"275,200": 1,
		"275,175": 1,
		"300,125": 1,
		"325,125": 1,
		"350,100": 1,
		"375,100": 1,
		"400,100": 1,
		"425,100": 1,
		"450,100": 1,
		"475,125": 1,
		"475,150": 1,
		"525,300": 4,
		"425,300": 1,
		"475,350": 1,
		"400,425": 1,
		"375,425": 1,
		"350,425": 1,
		"325,425": 1,
		"300,425": 1,
		"275,400": 1,
		"250,400": 1,
		"225,375": 1,
		"200,375": 1,
		"175,350": 1,
		"150,325": 1,
		"425,450": 1,
		"450,450": 1,
		"475,450": 1,
	},
	{
		"300,175": 1,
		"300,200": 2,
		"300,225": 2,
		"300,250": 2,
		"300,275": 2,
		"300,300": 2,
		"300,325": 1,
		"300,350": 1,
		"300,375": 1,
		"325,375": 2,
		"325,400": 2,
		"325,425": 2,
		"350,425": 2,
		"375,425": 2,
		"400,425": 2,
		"400,400": 2,
		"425,400": 2,
		"450,400": 2,
		"450,375": 3,
		"475,375": 2,
		"475,350": 2,
		"500,350": 3,
		"525,350": 2,
		"525,325": 2,
		"550,325": 2,
		"550,350": 2,
		"550,375": 2,
		"550,400": 2,
		"550,425": 2,
		"575,425": 2,
		"575,450": 2,
		"575,475": 2,
		"575,500": 2,
		"575,525": 2,
		"575,400": 2,
		"575,375": 1,
		"525,300": 4,
		"500,300": 2,
		"500,275": 2,
		"475,275": 2,
		"450,275": 2,
		"425,275": 2,
		"425,300": 2,
		"400,300": 2,
		"375,325": 2,
		"375,350": 2,
		"350,350": 2,
		"350,375": 2,
		"350,400": 2,
		"300,425": 2,
		"300,450": 2,
		"300,475": 2,
		"300,500": 2,
		"300,525": 2,
		"300,550": 2,
		"300,575": 2,
		"325,575": 2,
		"325,550": 2,
		"350,550": 2,
		"350,525": 2,
		"350,500": 2,
		"375,500": 2,
		"375,475": 2,
		"375,450": 2,
		"400,450": 2,
		"400,475": 2,
		"425,475": 2,
		"425,500": 2,
		"450,500": 2,
		"475,500": 2,
		"500,500": 2,
		"500,525": 2,
		"525,525": 2,
		"550,525": 2,
		"600,500": 2,
		"600,475": 2,
		"625,475": 1,
		"625,450": 1,
		"625,425": 1,
		"650,425": 1,
		"650,400": 1,
		"625,400": 1,
		"625,375": 1,
		"600,375": 1,
		"525,400": 2,
		"500,400": 2,
		"475,400": 3,
		"450,425": 2,
		"425,425": 2,
		"300,400": 1,
		"400,350": 2,
		"400,325": 2,
		"425,325": 2,
		"450,325": 2,
		"475,325": 2,
		"500,325": 2,
		"550,450": 2,
		"525,450": 2,
		"525,475": 2,
		"525,500": 2,
		"450,475": 2,
		"425,450": 2,
		"375,375": 2,
		"350,325": 2,
		"325,325": 2,
		"325,300": 2,
		"275,275": 2,
		"250,275": 2,
		"250,250": 2,
		"225,250": 2,
		"275,250": 2,
		"350,300": 2,
		"425,350": 2,
		"450,350": 2,
		"475,425": 2,
		"475,450": 2,
		"450,450": 2,
		"500,450": 2,
		"500,475": 2,
		"525,550": 2,
		"500,425": 2,
		"550,550": 2,
		"500,550": 2,
		"500,575": 2,
		"475,575": 2,
		"450,575": 2,
		"425,575": 2,
		"425,550": 2,
		"400,550": 2,
		"375,550": 2,
		"375,525": 2,
		"350,475": 2,
		"475,475": 2,
		"550,475": 2,
		"600,450": 2,
		"525,425": 2,
		"500,375": 2,
		"525,375": 2,
		"425,375": 2,
		"325,350": 2,
		"375,400": 2,
		"350,450": 2,
		"325,450": 2,
		"325,475": 2,
		"400,375": 2,
		"325,500": 2,
		"325,525": 2,
		"400,500": 2,
		"425,525": 2,
		"450,525": 2,
		"450,550": 2,
		"400,525": 2,
		"475,550": 2,
		"475,525": 2,
		"550,500": 2,
		"600,425": 2,
		"600,400": 2,
		"475,300": 2,
		"450,300": 2,
		"275,300": 2,
		"275,225": 2,
		"250,225": 2,
		"375,300": 2,
		"275,550": 1,
		"275,525": 1,
		"275,500": 1,
		"275,475": 1,
		"275,450": 1,
		"275,425": 1,
		"275,400": 1,
		"250,300": 1,
		"225,275": 1,
		"275,200": 1,
		"250,200": 1,
		"275,175": 1,
		"675,425": 1,
		"350,275": 1,
		"375,275": 1,
		"400,275": 1,
		"400,575": 1,
		"375,575": 1,
		"525,575": 1,
		"550,575": 1,
		"575,550": 1,
		"600,525": 1,
	},
	{
		"300,225": 2,
		"275,225": 2,
		"275,250": 2,
		"250,250": 2,
		"225,250": 2,
		"225,275": 2,
		"275,275": 2,
		"250,275": 2,
		"250,300": 2,
		"225,300": 2,
		"300,250": 3,
		"325,225": 2,
		"300,275": 2,
		"325,275": 2,
		"275,300": 2,
		"300,300": 1,
		"275,325": 2,
		"250,325": 2,
		"250,225": 1,
		"225,225": 1,
		"200,250": 1,
		"200,275": 1,
		"200,300": 1,
		"225,325": 1,
		"300,325": 1,
		"325,300": 1,
		"325,250": 4,
	},
	{
		"350,225": 2,
		"350,250": 2,
		"325,250": 2,
		"325,275": 2,
		"325,300": 2,
		"350,300": 2,
		"350,275": 2,
		"375,275": 2,
		"375,250": 2,
		"375,225": 2,
		"375,200": 2,
		"350,200": 2,
		"375,300": 2,
		"400,300": 2,
		"400,275": 2,
		"400,250": 2,
		"325,325": 2,
		"300,325": 2,
		"300,350": 2,
		"300,375": 2,
		"350,325": 2,
		"350,350": 2,
		"325,350": 2,
		"325,375": 2,
		"375,325": 2,
		"400,325": 2,
		"300,300": 1,
		"300,275": 1,
		"350,375": 1,
		"375,350": 1,
		"400,350": 1,
		"400,225": 1,
		"425,250": 1,
		"425,275": 1,
		"425,300": 1,
		"325,225": 1,
		"275,325": 1,
		"275,350": 1,
	},
	{
		"275,250": 1,
		"275,275": 1,
		"275,300": 1,
		"275,325": 1,
		"275,350": 1,
		"300,375": 1,
		"325,375": 1,
		"325,350": 2,
		"350,350": 1,
		"350,325": 1,
		"375,325": 1,
		"350,300": 1,
		"325,300": 1,
		"300,300": 2,
		"300,325": 2,
		"325,325": 2,
		"300,350": 1,
		"300,400": 1,
		"325,400": 1,
		"350,375": 1,
		"250,300": 1,
		"250,275": 1,
		"250,325": 1,
		"300,275": 1,
		"325,275": 1,
		"375,375": 1,
		"350,400": 1,
		"350,425": 1,
		"325,425": 1,
	},
	{
		"375,300": 2,
		"350,300": 2,
		"350,325": 2,
		"325,325": 2,
		"325,350": 2,
		"350,350": 2,
		"375,325": 2,
		"375,275": 2,
		"350,275": 2,
		"350,375": 2,
		"350,400": 2,
		"375,400": 2,
		"400,400": 1,
		"400,375": 2,
		"425,375": 2,
		"425,350": 2,
		"425,325": 2,
		"425,300": 2,
		"400,300": 2,
		"400,275": 2,
		"325,375": 2,
		"375,375": 2,
		"375,350": 2,
		"400,350": 2,
		"400,325": 2,
		"325,275": 2,
		"325,300": 2,
		"325,250": 2,
		"300,250": 3,
		"325,225": 2,
		"300,225": 2,
		"300,275": 3,
		"300,300": 2,
		"300,325": 2,
		"300,200": 2,
		"275,225": 3,
		"275,200": 2,
		"250,200": 2,
		"250,225": 2,
		"250,250": 2,
		"275,250": 2,
		"275,275": 2,
		"225,200": 2,
		"225,225": 2,
		"225,250": 2,
		"250,275": 2,
		"250,300": 2,
		"275,300": 2,
		"225,175": 2,
		"200,175": 2,
		"250,175": 2,
		"225,150": 2,
		"275,175": 2,
		"250,150": 2,
		"250,125": 1,
		"225,125": 2,
		"200,125": 2,
		"175,125": 2,
		"175,150": 2,
		"175,175": 2,
		"200,150": 2,
		"150,150": 2,
		"150,125": 2,
		"125,125": 2,
		"200,100": 1,
		"175,100": 2,
		"175,75": 2,
		"150,75": 2,
		"150,100": 2,
		"125,100": 1,
		"125,75": 1,
		"200,75": 1,
		"225,100": 1,
		"325,175": 1,
		"325,200": 1,
		"350,200": 1,
		"350,225": 1,
		"375,225": 1,
		"375,250": 1,
		"300,175": 1,
		"350,250": 1,
		"400,250": 2,
		"425,250": 1,
		"425,275": 2,
		"425,225": 1,
		"450,250": 1,
		"450,275": 1,
		"450,300": 1,
		"400,225": 1,
		"450,325": 1,
		"450,350": 1,
		"425,400": 1,
		"325,400": 1,
		"300,375": 1,
		"300,350": 1,
		"275,325": 1,
		"225,275": 1,
		"200,200": 1,
		"175,200": 1,
		"125,150": 1,
		"125,175": 1,
		"150,175": 1,
		"200,225": 4,
	},
	{
		"300,225": 2,
		"300,250": 2,
		"275,250": 2,
		"275,275": 2,
		"275,300": 2,
		"300,275": 2,
		"325,275": 2,
		"325,250": 2,
		"250,300": 2,
		"250,325": 2,
		"225,325": 2,
		"300,300": 2,
		"275,325": 2,
		"250,350": 2,
		"300,325": 2,
		"300,350": 2,
		"275,350": 3,
		"325,300": 1,
		"325,325": 1,
		"325,350": 1,
		"300,375": 2,
		"275,375": 2,
		"250,375": 2,
		"275,225": 1,
		"250,275": 1,
		"225,300": 1,
		"225,350": 1,
		"225,375": 1,
		"225,400": 1,
		"250,400": 1,
		"325,375": 1,
		"350,350": 1,
		"350,300": 1,
		"350,275": 1,
		"275,400": 4,
		"450,175": 2,
		"475,175": 2,
		"425,175": 1,
		"425,200": 1,
		"450,200": 1,
		"450,150": 1,
	},
	{
		"325,275": 1,
		"325,300": 2,
		"300,300": 2,
		"300,325": 3,
		"300,350": 3,
		"325,350": 2,
		"325,325": 2,
		"350,325": 2,
		"375,325": 2,
		"400,325": 2,
		"400,300": 2,
		"425,300": 1,
		"350,350": 2,
		"350,300": 2,
		"350,275": 2,
		"375,275": 2,
		"375,250": 2,
		"300,375": 2,
		"300,400": 2,
		"325,375": 2,
		"375,300": 2,
		"400,275": 1,
		"400,250": 1,
		"425,250": 1,
		"325,400": 2,
		"275,325": 2,
		"275,350": 2,
		"250,350": 1,
		"225,350": 1,
		"250,325": 2,
		"275,375": 2,
		"250,375": 2,
		"250,400": 1,
		"275,400": 1,
		"250,300": 2,
		"275,300": 2,
		"300,275": 2,
		"350,375": 4,
	},
]

for i in range(random.randint(3, 10)):
	currentType = islandTypes[random.randint(0, len(islandTypes)-1)]
	islandX, islandY = random.randint(0, MAP["AreaSize"][0]/25)*25, random.randint(0, MAP["AreaSize"][1]/25)*25
	for block in currentType:
		x = int(block.split(",")[0])
		y = int(block.split(",")[1])
		newBlock = str(x + islandX)+","+str(y + islandY)
		MAP["LandBlocks"][newBlock] = currentType[block]

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

PREP["Gun"] = loadImage("fightAssets/items/pistol.png")
PREP["CannonBall"] = loadImage("fightAssets/items/cannonBall.png")
PREP["Paper"] = loadImage("mapAssets/paper.png")
PREP["Paper"] = pygame.transform.scale(MAP["Paper"], (displayWidth, displayHeight))
PREP["FightButtonRect"] = pygame.Rect(
	displayWidth * 0.85, displayHeight * 0.9, displayWidth * 0.14, displayHeight * 0.09
)


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

	def setPos(self, X, Y):
		self.X = X
		self.Y = Y

	def logic(self, dropSpots):
		if self.dragged == False:
			if (
				self.rect.collidepoint(mousePos[0], mousePos[1]) == True
				and mouseButtons[0] == True
			):
				self.dragged = True
				self.dragDifX = self.X - mousePos[0]
				self.dragDifY = self.Y - mousePos[1]
				self.dragX = mousePos[0] + self.dragDifX
				self.dragY = mosuePos[1] + self.dragDifY
			else:
				self.dragX = self.X
				self.dragY = self.Y
		if self.dragged == True:
			if mouseButtons[0] == True:
				self.dragX = mousePos[0] + self.dragDifX
				self.dragY = mosuePos[1] + self.dragDifY
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
		screenDisplay.blit(drawSprite, Pos)


MAP["PlayerCargo"]["sailors"] = [sailor(1), sailor(1), sailor(2)]
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
		screenDisplay.blit(
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
				screenDisplay,
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
			screenDisplay.blit(
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

# GAME STATES (Functions)
def map():
	global MAP
	global gameState
	MAP["MiniMapDrawList"] = {}
	screenDisplay.fill((0, 0, 200))
	pygame.draw.rect(
		screenDisplay,
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
		screenDisplay,
		(0, 0, 0),
		(0 - MAP["ScreenPos"][0], 0 - MAP["ScreenPos"][1]),
		(
			MAP["AreaSize"][0] - MAP["ScreenPos"][0],
			MAP["AreaSize"][1] - MAP["ScreenPos"][1],
		),
	)
	pygame.draw.line(
		screenDisplay,
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

	MAP["PlayerSpeed"][0] -= MAP["PlayerSpeed"][0] * frameTime
	MAP["PlayerSpeed"][1] -= MAP["PlayerSpeed"][1] * frameTime

	MAP["PlayerPos"][0] += MAP["PlayerSpeed"][0] * frameTime * 30
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
			colour = (255, 200, 10)
		elif MAP["LandBlocks"][pos] == 2:  # grass
			colour = (0, 255, 0)
		elif MAP["LandBlocks"][pos] == 3:  # town
			colour = (210, 105, 30)
		elif MAP["LandBlocks"][pos] == 4:
			colour = (5, 5, 5)

		x = int(pos.split(",")[0])
		y = int(pos.split(",")[1])
		drawX = x - MAP["ScreenPos"][0]
		drawY = y - MAP["ScreenPos"][1]

		if dist((x, y), MAP["PlayerPos"]) < 1100: #adding to minimap
			MAP["MiniMapDrawList"][str(x - MAP["PlayerPos"][0])+","+str(y - MAP["PlayerPos"][1])] = colour

		if drawX > -25 and drawX < displayWidth and drawY > -25 and drawY < displayHeight:
			pygame.draw.rect(screenDisplay, (colour), (drawX, drawY, 25, 25))
			# Pirates
	for i in range(len(MAP["PirateShips"])):
		MAP["PirateShips"][i].AI()
		MAP["PirateShips"][i].X
		MAP["PirateShips"][i].draw()
		# Player
	drawShip = MAP["ships"][MAP["PlayerDir"]]
	screenDisplay.blit(
		drawShip,
		(
			MAP["PlayerPos"][0] - MAP["ScreenPos"][0],
			MAP["PlayerPos"][1] - MAP["ScreenPos"][1],
		),
	)
	# Ui
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


def optionsPage():
	screenDisplay.fill((154, 219, 235))
	###################################


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
			(30 * slots_drawn + 50 * slots_drawn, 515),
		)

	"""Behaviorial script"""


def cutScene():  # Need to make
	pass


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
	pygame.draw.circle(screenDisplay, (30, 50, 230), (center[0], center[1]), round(displayWidth * 0.07), 0)
	for pos in MAP["MiniMapDrawList"]:
		drawX = (float(pos.split(",")[0]) / zoom) + center[0]
		drawY = (float(pos.split(",")[1]) / zoom) + center[1]
		pygame.draw.rect(screenDisplay, MAP["MiniMapDrawList"][pos], (drawX, drawY, round(25/zoom)+1, round(25/zoom)+1))

	pygame.draw.circle(screenDisplay, (0, 0, 0), (center[0], center[1]), round(displayWidth * 0.07), 5)
	lineP1 = (math.sin(windDir) * windSpeed * 2, math.cos(windDir) * windSpeed * 2)
	pygame.draw.line(screenDisplay, (100, 100, 120), (lineP1[0] + center[0], lineP1[1] + center[1]), (center[0], center[1]), 3)


def MapUI(wind, pirateShips):
	miniMap(wind[0], wind[1], 20)
	if gameState == "Prep":
		prepMenu(MAP["PlayerCargo"], PREP["Enemy"].cargo)


def prepMenu(playerCargo, enemyCargo):
	global gameState
	screenDisplay.blit(PREP["Paper"], (0, 0))
	game_print(
		"Prepare for battle", displayWidth * 0.55, displayHeight * 0.2, 25, (20, 20, 0)
	)
	game_print("Cargo hold", displayWidth * 0.3, displayHeight * 0.3, 20, (20, 20, 0))
	game_print("On deck", displayWidth * 0.7, displayHeight * 0.3, 20, (20, 20, 0))
	game_print(
		"Living quarter", displayWidth * 0.3, displayHeight * 0.6, 20, (20, 20, 0)
	)
	pygame.draw.rect(
		screenDisplay,
		(10, 200, 30),
		(
			displayWidth * 0.85,
			displayHeight * 0.9,
			displayWidth * 0.14,
			displayHeight * 0.09,
		),
	)
	game_print("Fight", displayWidth * 0.9, displayHeight * 0.95, 10, (0, 0, 0))
	if (
		PREP["FightButtonRect"].collidepoint(mousePos[0], mousePos[1])
		and mouseButtons[0] == True
	):
		gameState = "Fight"
	for i in range(len(playerCargo["sailors"])):
		playerCargo["sailors"][i].logic([])
		playerCargo["sailors"][i].draw(None, None)


def dist(point1, point2):
	X = abs(point1[0] - point2[0])
	Y = abs(point1[1] - point2[1])
	return math.sqrt(X ** 2 + Y ** 2)


def text_objects(message, font, colour):
	textSurface = font.render(message, True, colour)
	return textSurface, textSurface.get_rect()


def game_print(message, posX, posY, size, colour):
	text = pygame.font.Font("FantasticBoogaloo.ttf", round(size * 1.5))
	text_surf, text_rect = text_objects(message, text, colour)
	text_rect.center = (posX, posY)
	screenDisplay.blit(text_surf, text_rect)


def QUIT():
	pygame.quit()
	exit()


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
	if gameState == "Menu":
		menu()
	if gameState == "Map" or gameState == "Prep":
		map()
	if gameState == "Fight":
		battleScreen()  # dont know wether to do a fight in the map screen or one in the battle screen or both or a combination
	pygame.display.update()
	clock.tick()
	frameTime = time.time() - startFrame
