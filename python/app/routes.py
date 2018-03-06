from app import app
from flask import Flask,abort,request,Response
import json
import sys
sys.path.append('/../')
import zot_n_ride as ZNC

@app.route('/')
@app.route('/home')
@app.route('/welcome')
def welcome():
    return 'Welcome to Zot n\' Ride!'

@app.route('/user/<username>')
def display_profile(username):
    return 'User {}'.format(username)

@app.route('/api/register',methods=['POST'])
def register_user():
    if not request.json:
        abort(400)
    test=ZNC.create_user_into_db(request.json['First'],request.json['Last'],request.json['Email'])
    if(test == None):
        return Response(json.dumps(request.json), status=201, mimetype='application/json')
    return json.dumps(request.json)
