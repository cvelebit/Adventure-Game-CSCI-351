import pygame
from World.WorldCommon import ScreenSize


#Press the enter key to open chat
#When chat is open enter message
#Chat window closes when the enter key is pressed
#Chat window shows history of past entered messages
#ignore other uses of keys when entering in chat

_chatOpen = False
_chatHistory = [] #could be a queue
_chatHistMax = 5
_curMessage = ""
_chatSurf = None


def Init():
    global _font
    _font = pygame.font.SysFont("arial", 24)

def _OpenChat():
    global _chatOpen
    global _font
    global _chatSurf

    _chatOpen = True
    
    _chatSurf = _font.render(': ', True, (0,0,0))

def _CloseChat():
    global _chatOpen
    global _chatSurf
    _chatOpen = False
    del _chatSurf

def _PostMessage():
    global _curMessage
    global _chatHistory
    global _chatHistMax
    global _font

    if _curMessage == "":
        return
    _chatHistory.append(_font.render('me: '+_curMessage, True, (0,0,0)))
    if len(_chatHistory) > _chatHistMax:
        surf = _chatHistory[0]
        del _chatHistory[0]
        del surf
    _curMessage = ""

def _AddChat(c):
    global _curMessage
    global _chatSurf
    global _font

    success = False
    if c == '\b':
        if _curMessage != '':
            _curMessage = _curMessage[:-1]
        success = True
    elif ord(c) >=32 and ord(c) <= 126:
        _curMessage += c
        success = True

    if success:
        del _chatSurf
        _chatSurf = _font.render(': ' + _curMessage, True, (0,0,0))

    return success

def ProcessEvent(event):
    global _chatOpen
    if event.type == pygame.KEYDOWN:
        c = event.unicode
        if event.key == 13: #enter key
            if _chatOpen:
                _PostMessage()
                _CloseChat()
            else:
                _OpenChat()
            return True

        elif _chatOpen:
            if event.key == 8:
                c = '\b'
            return _AddChat(c)
    return False

def Update(deltaTime):
    pass

def Render(screen):
    global _chatOpen
    global _chatSurf
    global _chatHistory

    y = ScreenSize[1]
    rect = pygame.Rect((0,y),(0,0))
    if _chatOpen:
        size = _chatSurf.get_rect().size
        y-= size[1]
        rect.top = y
        screen.blit(_chatSurf, rect)

    for surf in reversed(_chatHistory):
        size = surf.get_rect().size
        y-= size[1]
        rect.top = y
        screen.blit(surf, rect)