import pygame
from World.WorldCommon import ScreenSize, Paused, Players
from UI.UIButton import RegisterButtonAction
import UI.UI as UI
import requests
import json
import threading
import numpy as np

import sys
sys.path.append("../MyGameServer")
import Network.mySocket as sck
sys.path.pop()

pygame.init()
size = width, height = 960, 720 #640, 480
ScreenSize[0] = width
ScreenSize[1] = height
screen = pygame.display.set_mode(size)

pygame.mixer.init(frequency =22050, size = 16, channels=2, buffer=4069)
pygame.mixer.music.load("Data/Bensound-epic.ogg")


import World.World as World
World.Init(size, screen)
UI.Init()

try:
    with open("SettingsFile.txt", "r") as setFile:
        for line in setFile:
            i = line.find("volume ", 0, 7)
            if i != -1:
                volume = float(line[7:])
                if volume > 1:
                    volume = 1
                if volume < 0:
                    volume = 0
                pygame.mixer.music.set_volume(volume)
                continue
            i = line.find("END\n", 0, 4)
            if i != -1:
                break
except:
    pass

pygame.mixer.music.play(loops=-1)

SettingsFile = open("settingsFile.txt", "w")
def SaveSettings():
    global SettingsFile
    volume = pygame.mixer.music.get_volume()
    SettingsFile.write("volume " +str(volume)+ "\n")
    SettingsFile.write("END\n")
    SettingsFile.flush()
    SettingsFile.seek(0,0)
SaveSettings()

def StartForRealThisTime(type):
    

    if type == 'new':
        sck.Init(True, 0, 5006)
        r = requests.get(url = "http://localhost:5005/newgame/0")
    elif type == 'old':
        sck.Init(True, 0, 5006)
        r = requests.get(url = "http://localhost:5005/prevgame/0")
    elif type == 'join':
        sck.Init(True, 1, 5007)
        r = requests.get(url = "http://localhost:5005/newgame/1")
    else:
        print('Error - Startup Option not found')
        return

    data = r.json()
    Players[0].SetCenterPosition(np.asfarray([data['x'], data['y']]), safeMove = True)
    Paused[0] = False

def StartGame(type):
    for b in ['startnewButton','startoldButton','joinButton','volume-','volume+']:
        button = UI.GetElementByID(b)
        button.visible = False
    t = threading.Thread(target = StartForRealThisTime, args=(type,))
    t.start()

def StartNewGame():
    StartGame('new')

def StartOldGame():
    StartGame('old')

def JoinGame():
    StartGame('join')


RegisterButtonAction("StartNewGame", StartNewGame)
RegisterButtonAction("StartOldGame", StartOldGame)
RegisterButtonAction('JoinGame', JoinGame)

def VolumeUp():
    volume = pygame.mixer.music.get_volume()
    if volume < 1:
        volume += 0.1
        if volume > 1:
            volume = 1.0
        pygame.mixer.music.set_volume(volume)
        SaveSettings()
RegisterButtonAction("Volume+", VolumeUp)

def VolumeDown():
    volume = pygame.mixer.music.get_volume()
    if volume > 0:
        if volume <= 0.1:
            volume = volume*0.9
        else:
            volume -= 0.1
            if volume < 0:
                volume = 0.0

        pygame.mixer.music.set_volume(volume)
        SaveSettings()
RegisterButtonAction("Volume-", VolumeDown)

sv_time = 0
def Update(deltaTime):
    global sv_time
    sv_time += deltaTime
    paused = Paused[0]
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if UI.ProcessEvent(event) == True:
            continue
        if paused:
            continue
        if World.ProcessEvent(event) == True:
            continue
    if not paused:
        World.Update(deltaTime)
    UI.Update(deltaTime)
    if sv_time >= 3.0:
        sv_time = 0
        #SaveCharPosition()
    return True

def SaveCharPosition():
    pos = Players[0].GetCenterPosition()
    j = {"x":int(pos[0]), "y":int(pos[1])}
    r = requests.post(url = "http://localhost:5005/savepos/0", json = j)

def Render(screen):
    screen.fill((0,0,0))
    World.Render(screen)
    UI.Render(screen)
    pygame.display.flip()


_gTickLastFrame = pygame.time.get_ticks()
_gDeltaTime = 0.0

while Update(_gDeltaTime):
    Render(screen)
    t = pygame.time.get_ticks()
    _gDeltaTime = (t-_gTickLastFrame)/1000.0
    _gTickLastFrame = t

SaveCharPosition()
World.Cleanup()
UI.Cleanup()
SettingsFile.close()
