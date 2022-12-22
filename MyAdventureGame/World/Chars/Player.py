
import pymunk
from pymunk.vec2d import Vec2d
import pygame
import numpy as np
import math
from World.Chars.Character import Character, AnimType
from World.WorldObject import WorldObject
from World.WorldCommon import WorldObjects, ComputeDir, MoveDir, Camera, Server
import json
import os

import sys
sys.path.append("../MyGameServer")
import Network.mySocket as sck
import Database.database as db
sys.path.pop()

_attackLength = 1.0
_keyDirection = 500 #can't be small like 1 because player might reach the destination before the next update

class Player(Character):
    _database_save_interval = 3
    _speed = 200.0
    def __init__(self, element=None, path=None, size=None, body_type=pymunk.Body.KINEMATIC, local = False, id = 'me'):
        self.local = local
        self.ID = id
        self.lst_pos = None
        self.health = 1.0
        self.keyd = [0,0]
        self.mousemove = False
        self.keyattack = False
        self.keymove = False
        self.test = False
        self.lastdir = np.asfarray([1.0,0])
        super().__init__(element=element,path=path,size=size, body_type = body_type)
        self.timeToSave = Player._database_save_interval
        self.speed = Player._speed
        self.dirty = False


    def ProcessEvent(self,event):
        global _keyDirection
        if not self.local:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            left, middle, right = pygame.mouse.get_pressed()

            if left:
                self.mouseTarget = np.asfarray(pygame.mouse.get_pos()) - Camera
                self.lastdir, len = ComputeDir(self.GetCenterPosition(), self.mouseTarget)
                self.mousemove = True if len != 0 else False

        elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            self.animTimeSafe = False
            self.animTime = 0
            self.keyattack = True
            rock = WorldObject(path=os.path.dirname(__file__) + "/../../TinyAdventurePack/Other/Rock.png", size = (15,15), body_type = pymunk.Body.DYNAMIC)
            rock.shape.friction = 0
            rock.damage = 0.5
            rock.timeToDestruction = 2.0
            rock.SetCenterPosition(self.GetCollisionBoxCenter() + (self.lastdir * 45))
            dir = Vec2d(self.lastdir[0],self.lastdir[1])
            dir[1] = -dir[1]
            rock.body.apply_impulse_at_world_point(dir * 2500.0, rock.body.position)
            rock.name = 'p_rock'
            WorldObjects.append(rock)

        if event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_UP:
                self.keyd[1] -= _keyDirection
                self.keymove = True
                
            if event.key == pygame.K_DOWN:
                self.keyd[1] += _keyDirection
                self.keymove = True
                
            if event.key == pygame.K_LEFT:
                self.keyd[0] -= _keyDirection
                self.keymove = True
                
            if event.key == pygame.K_RIGHT:
                self.keyd[0] += _keyDirection
                self.keymove = True
                
           
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                self.keyd[1] += _keyDirection
            if event.key == pygame.K_DOWN:
                self.keyd[1] -= _keyDirection
            if event.key == pygame.K_LEFT:
                self.keyd[0] += _keyDirection
            if event.key == pygame.K_RIGHT:
                self.keyd[0] -= _keyDirection
            if self.keyd[1] == 0 and self.keyd[0] == 0:
                self.keymove = False
            
        

    def Update(self,deltaTime):
        global _attackLength
        idx = 0 if self.ID == 'me' else 1
        for i in WorldObjects:
            if i.name == "Skel":
                if i.last_attack <= 0:
                    dif = i.GetCenterPosition() - self.GetCenterPosition()
                    if dif[0] < 55 and dif[0] > -55:
                        if dif[1] < 55 and dif[1] > -55:
                            self.health -= float(i.attack_damage)
                            i.last_attack = i.attack_refresh
                        
                    elif dif[1] < 55 and dif[1] > -55:
                        if dif[0] < 55 and dif[0] > -55:
                            self.health -= float(i.attack_damage)
                            i.last_attack = i.attack_refresh
                else:
                    i.last_attack -= deltaTime
        if not Server[0]:
            if self.health <= 0:
                self.timeToDestruction = 0
        
        if not Server[0]:

            if self.keyattack:
                self.animType = AnimType.ATTACK
                self.animTime += deltaTime
                if self.animTime >= _attackLength:
                    self.keyattack = None
                    self.animTimeSafe = True

            #elif self.mousemove:
                #self.mousemove = MoveDir(self, self.lastdir, self.mouseTarget, Player._speed, deltaTime)
                #self.animType = AnimType.WALK

            elif self.keymove:
                myPos = self.GetCenterPosition()
                self.keyTarget = np.asfarray(myPos + self.keyd)
                self.lastdir, len = ComputeDir(self.GetCenterPosition(), self.keyTarget)
                self.keymove = True if len != 0 else False

        if (not Server[0]) and self.local:
            #print('client sending player message')
            p = self.GetCenterPosition()
            dct = {'x': p[0], 'y':p[1]}
            sck.SendMessage(self.ID, json.dumps(dct), source = 0)
            
        else:
            #print('server getting player message')
            while True:
                msg = sck.GetMessage(self.ID)
                if msg == None:
                    break
                savePos = json.loads(msg)
                print(msg)
                if self.lst_pos != savePos:
                    self.lst_pos = savePos
                    self.SetCenterPosition(np.asfarray([float(savePos['x']),float(savePos['y'])]), safeMove = True)
                    if Server[0]:
                        self.dirty = True
                        db.SetCharPos(0, float(savePos['x']),float(savePos['y']))
                        sck.SendMessage(self.ID, msg, source=idx)
        x = self.rect.x
        y = self.rect.y
        super().Update(deltaTime)
        if not Server[0] and self.local and (x != self.rect.x or y != self.rect.y):
            p = self.GetCenterPosition()
            dct = {'x': p[0], 'y':p[1]}
            sck.SendMessage(self.ID, json.dumps(dct))

        if Server[0]:
            self.timeToSave -= deltaTime
            if self.timeToSave <= 0:
                if self.dirty:
                    self.dirty = False
                    self.timeToSave = Player._database_save_interval
                    p = self.GetCenterPosition()
                    db.SetCharPos(idx, p[0], p[1])
                else:
                    self.timeToSave = 0

    def Render(self,screen):
        super().Render(screen)
