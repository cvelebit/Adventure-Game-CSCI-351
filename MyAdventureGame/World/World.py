
import pygame
import pymunk
import pymunk.pygame_util
import numpy as np
from World.WorldObject import WorldObject, objectWidth, objectHeight
from World.Chars.Player import Player
import xml.etree.ElementTree as ET
from World.WorldCommon import PhysicsEngine, WorldObjects, Players, Camera, ScreenSize, Server
from World.Chars.Enemy import Enemy
import os

def MakePlayer(idx, local, x, y):
    global _width
    global _height

    if len(Players) <= idx:
        Players.append(None)
    if idx == 0:
        
        Players[idx] = (Player(path = os.path.dirname(__file__) +  "/../TinyAdventurePack/Character/Char_one", size = (objectWidth, objectHeight), local = local, id = "me"))
    else:
        Players[idx] = (Player(path = os.path.dirname(__file__) +  "/../TinyAdventurePack/Character/Char_two", size = (objectWidth, objectHeight), local = local, id = "you"))
   
    if not Server[0]:
        Players[idx].SetCenterPosition(np.asfarray([_width / 2.0, _height / 2.0]), safeMove = True)
    WorldObjects.append(Players[idx])



def Init(size, screen):
    global _width
    global _height
    global _grass
    global _objectRect
    global _draw_options

    if size == None or screen == None:
        Server[0] = True

    PhysicsEngine[0] = pymunk.Space()
    PhysicsEngine[0].gravity = 0,0
    if not Server[0]:
        _draw_options = pymunk.pygame_util.DrawOptions(screen)
        _width, _height = size
        _grass = pygame.image.load("TinyAdventurePack/Other/grass.png")
        _grass = pygame.transform.scale(_grass, (objectWidth, objectHeight))
        _objectRect = pygame.Rect(0,0,objectWidth,objectHeight)

    tree = ET.parse(os.path.dirname(__file__) + '/../Data/WorldData.xml')
    root = tree.getroot() # root is "World" element

    MakePlayer(0, True, 320, 240)
    
    objects = root.find('Objects')
    if objects != None:
        for object in objects.findall("Object"):
            wo = WorldObject(element=object)
            WorldObjects.append(wo)

    enemies = root.find('Enemies')
    if enemies != None:
        for enemy in enemies.findall("Enemy"):
            wo = Enemy(element=enemy)
            WorldObjects.append(wo)



def _SortWorldObjects(worldObject):
    box = worldObject.GetCollisionBox()
    return box.y + box.height

def ProcessEvent(event):

    for i in WorldObjects:
        if i.ProcessEvent(event) == True:
            return True

_timeStep = 1.0/60.0
_timeSinceLastFrame = 0


def Update(deltaTime):
    global _timeStep
    global _timeSinceLastFrame

    _timeSinceLastFrame += deltaTime
    while (_timeSinceLastFrame >= _timeStep):
        PhysicsEngine[0].step(_timeStep)
        _timeSinceLastFrame -= _timeStep
    if not Server[0]:
        c = -(Players[0].GetCenterPosition() - (ScreenSize[0]/2.0, ScreenSize[1]/2.0))
        Camera[0] = c[0]
        Camera[1] = c[1]

    
    for i in WorldObjects:
        i.Update(deltaTime)

    i = len(WorldObjects) -1
    while i >= 0:
         if WorldObjects[i].timeToDestruction == 0:
             PhysicsEngine[0].remove(WorldObjects[i].shape, WorldObjects[i].body)
             temp = WorldObjects[i]
             WorldObjects.remove(WorldObjects[i])
             del temp
         i -= 1


    for i in WorldObjects:
        i.DetectCol()
    if not Server[0]:
        WorldObjects.sort(key=_SortWorldObjects)

def Render(screen):
    global _width
    global _height
    global _grass
    global _objectRect
    global _draw_options

    _objectRect.x = 0
    _objectRect.y = 0
    for x in range (1 + _width // objectWidth):
        _objectRect.x = objectWidth*x
        for y in range(1 + _height // objectHeight):
            _objectRect.y = objectHeight*y
            screen.blit(_grass, _objectRect)


    for i in WorldObjects:
        i.Render(screen)

    #PhysicsEngine[0].debug_draw(_draw_options)

def Cleanup():
    pass