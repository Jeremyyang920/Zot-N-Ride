from app import app
from flask import Flask,abort,request,Response
import json
from flask import jsonify

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
    body=request.json
    test=ZNC.create_user_into_db(body['netID'],body['password'],body['firstname'],body['lastname'],body['major'],body['address'],body['isDriver'])
    if(test == None):
        abort(400)
    return json.dumps(request.json)
