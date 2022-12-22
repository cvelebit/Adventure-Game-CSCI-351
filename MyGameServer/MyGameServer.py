import Database.database as db
import Network.rest as nw
import threading

Initialized = False

def MainThread():
    global Initalized

    while True:
        if not Initialized:
            continue

t = threading.Thread(target=MainThread)
t.start()

#Init
db.Init()
nw.Init()
Initialized = True


#Run
nw.Run()