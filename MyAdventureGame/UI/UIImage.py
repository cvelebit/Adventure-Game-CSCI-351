
import pygame
import numpy as np
from World.WorldCommon import ScreenSize, Players, WorldObjects

class UIImage():

    def __init__(self, element=None):
        if element != None:
            self.char = None
            self.path = element.get("path", None)
            self.h_bar = element.get("h_bar", None)
            self.h_bar_id = element.get("h_bar_id", None)
            self.x = int(element.get("x", 0))
            self.y = int(element.get("y", 0))
            self.width = int(element.get("width", 0))
            self.height = int(element.get("height", 0))
            self.justify = element.get("justify", "left")
            self.vjustify = element.get("vjustify", "top")
            self.safe_display = element.get("safe_display", True)
            if self.safe_display == "False":
                self.safe_display = False
            anchor = element.find("Anchor")
            if anchor != None:
                self.anchorX = float(anchor.get("x", 0))
                self.anchorY = float(anchor.get("y", 0))
            else:
                self.anchorX = 0
                self.anchorY = 0
            v = element.get('visible', 'false')
            self.visible = v == "true"
            if self.path == None:
                self.surf = None
            elif self.safe_display == False:
                self.surf = None
            else:
                self.surf = pygame.image.load(self.path)
            if self.surf != None:
                self.surf = pygame.transform.scale(self.surf, (self.width, self.height))

            self.rect = pygame.Rect((self.x, self.y),(self.width, self.height))

            if self.h_bar != None:
                self.Health_Bar()

            self._CalcRect()
    

    def Health_Bar(self):
        if self.h_bar == "Player":
            self.char = Players[0]
        elif self.h_bar:
            for i in WorldObjects:
                if i.name == self.h_bar:
                    if str(self.h_bar_id) == str(i.id):
                        self.char=i
                        if self.char.curState == "Chase":
                            self.safe_display = True
        else:
            return None

        if self.char.health <= 0:
            self.h_bar = None
            self.visible = False
            self.safe_display = False
        else:
            new_width = int(self.width * self.char.health)

        if self.safe_display != False:
            self.surf = pygame.image.load(self.path)
            self.surf = pygame.transform.scale(self.surf, (new_width, self.height))


    def _CalcRect(self):
        
        self.rect.left = self.anchorX * ScreenSize[0] + self.x
        if self.justify == "right":
            self.rect.left -= self.width
        elif self.justify == "center":
            self.rect.left -= self.width//2

        self.rect.top = self.anchorY * ScreenSize[1] + self.y
        if self.vjustify == "bottom":
            self.rect.top -= self.height
        elif self.vjustify == "center":
            self.rect.top -= self.height//2

        self.rect.width = self.width
        self.rect.height = self.height

    def ProcessEvent(self, event):
        return False

    def Update(self, deltaTime):
        if self.h_bar != None:
            self.Health_Bar()
            

    def Render(self, screen):
        if self.visible and self.surf != None:
            screen.blit(self.surf, self.rect)
        