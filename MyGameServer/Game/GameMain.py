#server will control enemies, client will control player
import time
import sys
sys.path.append("../MyAdventureGame")
import World.World as world
sys.path.pop()

_disconnect = True

import pygame
import Network.mySocket as sck
import threading

def GameLoop():
    global _disconnect
    pygame.init()
    _gTickLastFrame = pygame.time.get_ticks()
    _gDeltaTime = 0.0
    while True:
        if not (sck.IsConnected(0) or sck.IsConnected(1)):
            _disconnect = True
            break
        world.Update(_gDeltaTime)
        t = pygame.time.get_ticks()
        _gDeltaTime = (t-_gTickLastFrame)/1000.0
        _gTickLastFrame = t


def ChatUpdate():
    msg = sck.GetMessage('Chat')
    if msg:
        print(msg)


def NewGameThread(remote_addr, remote_port):
    #load
    world.Init(None, None)

    #connect to client
    sck.Init(False, 0, remote_port, remote_addr)

    #start game loop, wait fo connection
    tries = 25
    while not sck.IsConnected(0) and tries > 0: #to fix a race condition
        time.sleep(1)
        tries -= 1
    GameLoop()

def JoinGameThread(remote_addr, remote_port):
    sck.Init(False, 1, remote_port, remote_addr)

    #start game loop, wait fo connection
    tries = 25
    while not sck.IsConnected(1) and tries > 0: #to fix a race condition
        time.sleep(1)
        tries -= 1

    #do something?
    #should create 'make player' also 

def NewGame(id, remote_addr, remote_port):
    global _disconnect
    
    if id == 0:
        if not _disconnect:
            return
        _disconnect = False
        argslst = []
        argslst.append(remote_addr)
        argslst.append(remote_port)
        t = threading.Thread(target=NewGameThread, args = argslst)
        t.start()

    else:
        argslst = []
        argslst.append(remote_addr)
        argslst.append(remote_port)
        t = threading.Thread(target=JoinGameThread, args = argslst)
        t.start()
        