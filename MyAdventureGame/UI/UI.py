
import pygame
import xml.etree.ElementTree as ET
from UI.UIImage import UIImage
from UI.UIText import UIText
from UI.UIButton import UIButton
import UI.Chat as Chat

def GetElementByID(id):
    global _uiIds
    return _uiIDs[id]

def Init(element = None):
    global _uiObjects
    global _uiIDs

    Chat.Init()

    _uiObjects = []
    _uiIDs = {}

    if element == None:
        tree = ET.parse("Data/UI.xml")
        root = tree.getroot()
        groups = root.find("Group")
        if groups != None:
            for element in groups.findall("*"):
                if element.tag == "Image":
                    img = UIImage(element)
                    _uiObjects.append(img)
                elif element.tag == "Text":
                    img = UIText(element)
                    _uiObjects.append(img)
                elif element.tag == "Button":
                    img = UIButton(element)
                    _uiObjects.append(img)
                if img != None:
                    id = element.get("id")
                    if id != None:
                        _uiIDs[id] = img


def ProcessEvent(event):
    global _uiObjects

    if Chat.ProcessEvent(event):
        return True

    for i in reversed(_uiObjects):
        if i.ProcessEvent(event) == True:
            return True

    return False

def Update(deltaTime):
    global _uiObjects

    Chat.Update(deltaTime)

    for i in _uiObjects:
        i.Update(deltaTime)

def Render(screen):
    global _uiObjects

    for i in _uiObjects:
        i.Render(screen)

    Chat.Render(screen)

def Cleanup():
    pass