
import pygame
import numpy as np
import pymunk
from World.WorldCommon import PhysicsEngine, ScreenSize, Camera, Server
import os

objectWidth = 32
objectHeight = 32


class WorldObject():

    #STATIC - never moves
    #DYNAMIC - affected by physics
    #KINEMATIC - is in pyhsics world, more control over where cinematic object goes


    def __init__(self, element=None, path=None, size=None, body_type = pymunk.Body.STATIC, col_rect = None, frames = 1):
        self.body = None
        self.name = None
        if element != None:
            if path == None:
                self.path = element.get("path")
                if self.path != None:
                    self.path = os.path.dirname (__file__) + "/../" + self.path
            else:
                self.path = path
            self.name = element.get("name")
            s = element.get("scale")
        else:
            self.path = path
            s = None
            
        self.surf = pygame.image.load(self.path)

        scale = 4 if s == None else float(s)
        if size == None:
            self.size = np.asfarray(self.surf.get_rect().size)* scale
        else:
            self.size = np.asfarray(size)

        if Server[0]:
            self.surf = None
        else:
            self.surf = pygame.transform.scale(self.surf, (int(self.size[0]),int(self.size[1])))
        self.pos = np.asfarray([0,0])
        
        self.size[0] /= frames

        if element!= None:
            self.SetCenterPosition(np.asfarray([float(element.get("x")),float(element.get("y"))]))
        self.rect = pygame.Rect(self.pos, self.size)

        self.col_type = "box"
        self.col_rect = pygame.Rect((0,0), self.size) if col_rect == None else col_rect
        if element != None:
            col_elem = element.find("Col")
            if col_elem != None:
                self.col_rect = pygame.Rect((int(col_elem.get("xoff")),int(col_elem.get("yoff"))),(int(col_elem.get("w")), int(col_elem.get("h"))))
                self.col_type = col_elem.get("type")
            
        
        mass = 10
        moment = 10
        self.body = pymunk.Body(mass, moment, body_type)
        center = self.GetCollisionBoxCenter()
        self.body.position = center[0], ScreenSize[1] - center[1]
        PhysicsEngine[0].reindex_shapes_for_body(self.body)

        box = self.GetCollisionBox()
        if self.col_type == "oval":
            poly = self.GetCollisionOval(box)
            self.shape = poly
        elif self.col_type == "capsule":
            poly = self.GetCollisionCapsule(box)
            self.shape = poly
        else:
            self.shape = pymunk.Poly.create_box(self.body, box.size)

        PhysicsEngine[0].add(self.body,self.shape)

        self.timeToDestruction = -1.0


    def GetPixelArray(self):
        try:
            pixels = pygame.image.load(self.path)
        except pygame.error:
            raise SystemExit
        self.pixels = pygame.PixelArray(pixels)

    def SetCenterPosition(self, pos, safeMove=False):
        self.pos = pos - (self.size/2.0)

        if self.body != None:
            center = self.GetCollisionBoxCenter()
            self.body.position = center[0], ScreenSize[1] - center[1]
            PhysicsEngine[0].reindex_shapes_for_body(self.body)

    def GetCenterPosition(self):
        return self.pos + (self.size/2.0)

    def GetCollisionBox(self):
        return pygame.Rect(self.pos + np.asfarray(self.col_rect.topleft), self.col_rect.size)

    def GetCollisionOval(self,box):
        oval = ((-box.w/2,0),(-box.w * 0.5 * 0.707107, -box.h * 0.5 * 0.707107),(0,-box.h/2),(box.w * 0.5 * 0.707107, -box.h * 0.5 * 0.707107),(box.w/2,0),(box.w * 0.5 * 0.707107, box.h * 0.5 * 0.707107),(0,box.h/2),(-box.w * 0.5 * 0.707107, box.h * 0.5 * 0.707107))
        return pymunk.Poly(self.body,oval)

    def GetCollisionCapsule(self,box):
        capsule = ((-box.w * 0.5 * 0.707107,0),(-box.w * 0.5 * 0.707107, -box.h * 0.5 * 0.707107),(0,-box.h/2),(box.w * 0.5 * 0.707107, -box.h * 0.5 * 0.707107),(box.w * 0.5 * 0.707107,0),(box.w * 0.5 * 0.707107, box.h * 0.5 * 0.707107),(0,box.h/2),(-box.w * 0.5 * 0.707107, box.h * 0.5 * 0.707107))
        return pymunk.Poly(self.body,capsule)

    def GetCollisionBoxCenter(self):
        box = self.GetCollisionBox()
        return np.asfarray([box.x + (box.w / 2), box.y + (box.h / 2)])

    def ProcessEvent(self, event):
        return False

    def Update(self, deltaTime):

        if self.body.body_type == pymunk.Body.DYNAMIC:
            center = self.GetCollisionBoxCenter()
            self.pos[0] = self.body.position[0] - (center[0] - self.pos[0])
            self.pos[1] = (ScreenSize[1] - self.body.position[1]) - (center[1] - self.pos[1])

        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]

        if self.timeToDestruction != -1:
            self.timeToDestruction -=deltaTime
            if self.timeToDestruction < 0:
                self.timeToDestruction = 0

    def DetectCol(self):
        pass

    def Render(self, screen):
        rect = self.rect.copy()
        rect.x += int(Camera[0])
        rect.y += int(Camera[1])

        screen.blit(self.surf, rect)

