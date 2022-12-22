
import pymunk
import pygame
import random
import math
from World.WorldObject import WorldObject
from World.WorldCommon import PhysicsEngine, Camera, Server, MoveDir
from enum import IntEnum
import os

_charWidth = 120
_charHeight = 100
_imageCount = 6
_animFrameLen = 0.1667
_health = 1.0

class AnimType(IntEnum):
    IDLE = 0
    WALK = 1
    ATTACK = 2

class AnimDir(IntEnum):
    DOWN = 0
    LEFT = 1
    UP = 2
    RIGHT = 3




class Character(WorldObject):

    @staticmethod
    def _LoadSurf(path, folder, name, dir):
        global _charWidth
        global _charHeight
        global _imageCount
        try:
            surf = pygame.image.load(path + '/' + folder + '/Char_' + name + '_' + dir +'.png')
        except:
            surf = None

        if surf != None:
            surf = pygame.transform.scale(surf, (_charWidth * _imageCount, _charWidth))
        return surf


    def __init__(self, element=None, path=None, size=None, body_type=pymunk.Body.KINEMATIC):
        global _charWidth
        global _charHeight
        global _imageCount
        global _health
        
        if element != None:
            path = element.get("path")
            if path != None:
                path = os.path.dirname(__file__) + "/../../" + path


        super().__init__(element=element,path=path+"/Idle/Char_idle_down.png",
                         size=(_charWidth*_imageCount,_charHeight),body_type = body_type,
                         col_rect=pygame.Rect((34,4),(52,72)), frames = _imageCount)
        if not Server[0]:
            # outer list rep. anim type, inner list rep. anim dir
            self.anims = [[self.surf, Character._LoadSurf(path, "Idle", 'idle', 'left'),Character._LoadSurf(path, "Idle", 'idle', 'up'),Character._LoadSurf(path, "Idle", 'idle', 'right')],
                          [Character._LoadSurf(path, "Walk", 'walk', 'down'),Character._LoadSurf(path, "Walk", 'walk', 'left'),Character._LoadSurf(path, "Walk", 'walk', 'up'),Character._LoadSurf(path, "Walk", 'walk', 'right')],
                          [Character._LoadSurf(path, "Attack", 'atk', 'down'),Character._LoadSurf(path, "Attack", 'atk', 'left'),Character._LoadSurf(path, "Attack", 'atk', 'up'),Character._LoadSurf(path, "Attack", 'atk', 'right')]]
            self.animDir = AnimDir.DOWN
            self.animType = AnimType.IDLE
            self.animTime = random.uniform(0, _animFrameLen * _imageCount)
            self.animTimeSafe = True
            
            self.health = _health

            frame = self.animTime // _animFrameLen
            self.area = pygame.Rect((frame * _charWidth,0),(_charWidth,_charHeight))
        self.charLastPos = self.GetCenterPosition()
        self.mousemove = False
        self.keymove = False
        self.speed = 0

    def SetCenterPosition(self, pos, safeMove=False):
        super().SetCenterPosition(pos, safeMove)
        if safeMove:
            self.charLastPos = self.GetCenterPosition()

    def Update(self,deltaTime):
        global _charWidth
        global _charHeight
        global _imageCount
        global _animFrameLen

        if not Server[0]:
            if self.mousemove:
                
                self.mousemove = MoveDir(self, self.lastdir, self.mouseTarget, self.speed, deltaTime)

                self.animType = AnimType.WALK
            elif self.keymove:
                self.keymove = MoveDir(self, self.lastdir, self.keyTarget, self.speed, deltaTime)

                self.animType = AnimType.WALK
            
            elif self.animType != AnimType.ATTACK:
                self.animType = AnimType.IDLE
            

            if self.animTimeSafe == True: #if False animTime can be overwritten
                self.animTime += deltaTime
                if self.animTime >= _animFrameLen * _imageCount:
                    self.animTime = 0
            frame = self.animTime // _animFrameLen
        
            self.area = pygame.Rect((frame * _charWidth,0),(_charWidth,_charHeight))

        curPos = self.GetCenterPosition()
        curDir = curPos - self.charLastPos
        self.charLastPos = curPos
        if not Server[0]:
            if curDir[0] != 0 or curDir[1] != 0:
                if math.fabs(curDir[0]) > math.fabs(curDir[1]):
                    if curDir[0] > 0:
                        self.animDir = AnimDir.RIGHT
                    else:
                        self.animDir = AnimDir.LEFT
                else:
                    if curDir[1] > 0:
                        self.animDir = AnimDir.DOWN
                    else:
                        self.animDir = AnimDir.UP

        super().Update(deltaTime)

    def DetectCol(self):
        result = PhysicsEngine[0].shape_query(self.shape)
        for r in result:
            points = r.contact_point_set.points
            if len(points) > 0:
                n = r.contact_point_set.normal * points[0].distance
                p = self.GetCenterPosition()
                n.y = -n.y
                p += n
                self.SetCenterPosition(p, safeMove=True)

    def Render(self,screen):
        rect = self.rect.copy()
        rect.x += int(Camera[0])
        rect.y += int(Camera[1])
        screen.blit(self.anims[self.animType][self.animDir], rect, self.area)