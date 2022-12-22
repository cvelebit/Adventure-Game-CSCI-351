#this will be used by client and server
#take into account the fact it will be shared
#used to send message

import socket
import threading
import time
import queue

_Messages = {}
_theConnection = []
_lock = threading.Lock()

def IsConnected(index):
    global _theConnection
    if index >= len(_theConnection):
        return False
    return _theConnection != None

def SendMessage(name, mes, source=None, target=None):#server might want to send message to 1 clients, all clients or all but 1 client
    global _theConnection
    if target == None:
        for i in range(len(_theConnection)):
            if _theConnection[i] == None or (source!= None and i == source):
                continue
            try:
                _theConnection[i].sendall(bytearray(name + "|" + mes + "\x01", "utf-8"))
                #print(f'Message {name} sent with data {mes}')
            except: #Exception as e
                #print(e, 'Sending Failed')
                _theConnection[i] = None
    else:
        try:
            _theConnection[target].sendall(bytearray(name + "|" + mes + "\x01", "utf-8"))
        except:
            _theConnection[target] = None

def GetMessage(name):
    global _Messages
    global _lock

    with _lock:
        if not name in _Messages:
            #print('no messages of that name')
            return None

        mesList = _Messages[name]
        if mesList.empty():
            return None
        mes = mesList.get()

        #print(f'Message {name} recieved with data {mes}')
    return mes

def _Process(idx):
    global _theConnection
    global _Messages
    global _lock

    data = ""
    with _theConnection[idx]:
        while True:
            try:
                d = _theConnection[idx].recv(1024)
            except Exception as e:
                print(e)
                break
            if not d:
                break
            data += d.decode("utf-8")
            index = data.find("\x01")
            if index != -1:
                wrd = data.find("|")
                ky = data[0:wrd]
                ms = data[wrd+1:index]
                #print(f'got ms, {ky} has info {ms}')
                with _lock:
                    if not ky in _Messages:
                        _Messages[ky] = queue.Queue()
                    _Messages[ky].put(ms)

                data = data[index+1:]
    _theConnection[idx] = None #None
                

def _Listener(port): #client
    global _theConnection
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    conn.bind(('127.0.0.1', port))
    conn.listen()
    conn, addr = conn.accept()
    if len(_theConnection) == 0:
        _theConnection.append(conn)
    else:
        theConnection[0] = conn
    # process incoming messages
    _Process(0)


def _Connector(index, address, port): #server makes connection
    global _theConnection
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    connected = False
    tries = 25

    while not connected and tries > 0:
        try:
            conn.connect((address,port))
            connected = True
        except Exception as e:
            time.sleep(1)
            tries -= 1

    if connected:
        if len(_theConnection) <= index:
            _theConnection.append(conn)
        else:
            _theConnection[index] = conn
        _Process(index)



def Init(asListener, index = 0, port = None, address = None):
    if asListener:
        argList = []
        argList.append(port)
        t = threading.Thread(target=_Listener, args = argList)
    else:
        argList = []
        argList.append(index)
        argList.append(address)
        argList.append(port)
        t = threading.Thread(target=_Connector, args = argList)
    t.start()





