
from flask import Flask, jsonify, request, make_response, abort
import os
import json
import Database.database as db
import Game.GameMain as gm

def Init():
    global app
    app = Flask(__name__)

    @app.route('/newgame/<int:id>', methods = ['GET'])
    def get_newgame(id = 0):
        if id != 0 and id != 1:
            return
        
        if id == 0:
            print("Starting new game")
            db.ClearSave()
            db.NewChar("me", json.dumps({"x":320, "y":240}))
            gm.NewGame(id, request.remote_addr, 5006)
            return db.GetCharData(id)

        print('joining game')
        db.NewChar("you", json.dumps({"x":420, "y":340}))
        gm.NewGame(id, request.remote_addr, 5007)
        return db.GetCharData(id)

    @app.route('/prevgame/<int:id>', methods = ['GET'])
    def get_prevgame(id = 0):
        print("Continuing previous game")
        gm.NewGame(id, request.remote_addr, 5006)
        return db.GetCharData(id)

    @app.route('/savepos/<int:id>', methods = ['POST'])
    def set_savepos(id=0):
        print("Saving game")
        if not request.json or not 'x' in request.json or not 'y' in request.json:
            abort(400)
        db.SetCharPos(id, int(request.json['x']), int(request.json['y']))
        return db.GetCharData(id)




def Run():
    global app
    app.run(port='5005', threaded=True)