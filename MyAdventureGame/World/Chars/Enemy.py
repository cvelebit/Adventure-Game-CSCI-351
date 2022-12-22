from World.Chars.NPCState import State
import pymunk
from pymunk.vec2d import Vec2d
import pygame
import numpy as np
import math
from World.Chars.Character import Character
from World.WorldObject import WorldObject
from World.WorldCommon import WorldObjects, Server, ComputeDir, MoveDir
import json
import sys
sys.path.append("../MyGameServer")
import Database.database as db
import Network.mySocket as sck
sys.path.pop()

_attackRefresh = 1.0

class Enemy(Character):
    def __init__(self, element=None, path=None, size=None):
        global _attackRefresh
        self.lst_pos = None
        self.lastdir = np.asfarray([1.0, 0.0])
        self.last_attack = 0
        self.attack_refresh = _attackRefresh
        self.curState = None
        self.stateList = {}
        self.attack_damage = element.get("damage")
        self.id = element.get("id")
        if element != None:
            if Server[0]:
                ai = element.find("AI")
                if ai != None:
                    for state in ai.findall("State"):
                        s = State(state)
                        self.stateList[s.name] = s
                        if self.curState == None:
                            self.curState = s.name
        super().__init__(element=element,path=path,size=size)
        if Server[0]:
            pos = self.GetCenterPosition()
            #print('server sending enemy message')
            pos = f'{pos[0]},{pos[1]}'
            sck.SendMessage(f"{str(self.name+self.id)}_Pos", pos)
            db.InsertCharPos(str(self.name+self.id),int(pos[0]),int(pos[1]))

        
    def Update(self, deltaTime):
        for i in WorldObjects:
            if i.name == "p_rock":
                dif = i.GetCenterPosition() - self.GetCenterPosition()
                if dif[0] < 55 and dif[0] > -55:
                    if dif[1] < 55 and dif[1] > -55:
                        self.health -= i.damage
                        i.timeToDestruction = 0
                elif dif[1] < 55 and dif[1] > -55:
                    if dif[0] < 55 and dif[0] > -55:
                        self.health -= i.damage
                        i.timeToDestruction = 0
        if not Server[0]:
            if self.health <= 0:
                self.timeToDestruction = 0

        if self.curState != None and Server[0]:
            result = self.stateList[self.curState].Update(self, deltaTime)
            if result:
                self.stateList[self.curState].action.Enter(self)

        if Server[0]:
            rpos = self.GetCenterPosition()
            #print('server sending enemy message')
            p = self.GetCenterPosition()
            dct = {'x': p[0], 'y':p[1], 'speed':self.speed}
            sck.SendMessage(f"{str(self.name+self.id)}_Pos", json.dumps(dct))
            db.SetCharPos(str(self.name+self.id),int(float(rpos[0])),int(float(rpos[1])))
            
        else:
            #print('client getting enemy message')
            msg = sck.GetMessage(f"{str(self.name+self.id)}_Pos")
            if msg != None:
                savePos = json.loads(msg)
                if self.lst_pos != savePos:
                    self.lst_pos = savePos
                    self.speed = float(savePos['speed'])
                    self.mouseTarget = np.asfarray([float(savePos['x']),float(savePos['y'])])
                    self.lastDir, len = ComputeDir(self.GetCenterPosition(), self.mouseTarget)
                    self.mousemove = True if len!= 0 else False
                    #print(f'client set {str(self.name+self.id)}_Pos at {savePos}')

        super().Update(deltaTime)
        

