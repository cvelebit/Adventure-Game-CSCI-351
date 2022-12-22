
from World.WorldCommon import Players, ComputeDir, MoveDir, Server
from World.Chars.Character import AnimType


class Action():
    def __init__(self, element):
        pass

    def Enter(self, char):
        pass
    
    def Exit(self, char):
        pass

    def Act(self, char, deltaTime):
        pass

class IdleAction(Action):
    def Enter(self, char):pass

    def Act(self, char, deltaTime):
        pass


class ChaseAction(Action):
    def __init__(self, element):
        self.speed = float(element.get("speed"))
        super().__init__(element)

    def Enter(self, char):
        char.speed = self.speed
        self.target = Players[0]
        char.lastdir, len = ComputeDir(char.GetCenterPosition(), self.target.GetCenterPosition())
        
        super().Enter(char)

    def Act(self, char, deltaTime):
        if Server[0]:
            
            MoveDir(char, char.lastdir,self.target.GetCenterPosition(), self.speed, deltaTime)
            char.lastdir, len = ComputeDir(char.GetCenterPosition(),self.target.GetCenterPosition())
            
        char.lastdir, len = ComputeDir(char.GetCenterPosition(), self.target.GetCenterPosition())


class ReturnAction(Action):
    def Act(self, char, deltaTime):
        pass


def CreateAction(element):
    action = element.find("Action")
    if action == None:
        return None
    atype = action.get("type")
    if atype == "Idle":
        return IdleAction(action)
    if atype == "Chase":
        return ChaseAction(action)
    if atype == "Return":
        return ReturnAction(action)
    return None



# the decisions

class Decision():
    def __init__(self, element, state):
        self.state = state
        self.trueState = element.get("trueState")
        self.falseState = element.get("falseState")

    def Decide(self, char):
        return False

class PlayerInRange(Decision):
    def __init__(self,element,state):
        super().__init__(element, state)
        self.dist = int(element.get("distance"))
        self.distSqr = self.dist * self.dist

    def Decide(self, char):
        if hasattr(self.state.action, "target"):
            target =  self.state.action.target #rule: whenever an action has a target, action must store it in self.target
        else:
            target = Players[0]

        playerBox = target.GetCollisionBox()
        aiBox = char.GetCollisionBox()
        xdiff = 0
        ydiff = 0

        if playerBox.x > aiBox.x + aiBox.width:
            xdiff = playerBox.x - (aiBox.x +aiBox.width)
        elif playerBox.x + playerBox.width < aiBox.x:
            xdiff = aiBox.x - (playerBox.x + playerBox.width) 
        
        if playerBox.y > aiBox.y + aiBox.height:
            ydiff = playerBox.y - (aiBox.y +aiBox.height)
        elif playerBox.y + playerBox.height < aiBox.y:
            ydiff = aiBox.y - (playerBox.y + playerBox.height)

        len = xdiff * xdiff + ydiff * ydiff
        return len < self.distSqr


class HomeInRange(Decision):
    pass

class WasAttacked(Decision):
    pass

class TimeIsUp(Decision):
    pass

def CreateDecision(element, state):
    type = element.get("decide")
    if type == "player_in_range":
        return PlayerInRange(element, state)
    if type == "home_in_range":
        return HomeInRange(element, state)
    if type == "Return":
        return WasAttacked(element, state)
    if type == "time_is_up":
        return TimeIsUp(element, state)
    return None



# want the state that we are in (one state at a time)

class State():
    def __init__(self, element):
        self.name = element.get("name")
        self.action = CreateAction(element)
        self.decisions = []
        for decision in element.findall("Decision"):
            self.decisions.append(CreateDecision(decision, self))

    def Update(self, char, deltaTime):
        self.action.Act(char, deltaTime)
        for decision in self.decisions:
            result = decision.Decide(char)
            if result:
                if decision.trueState != char.curState:
                    char.curState = decision.trueState
                    self.action.Exit(char)
                    return True
            else:
                if decision.falseState != char.curState:
                    char.curState = decision.falseState
                    self.action.Exit(char)
                    return True
        return False