from app import app
from flask import Flask,abort,request,Response
import json
from flask import jsonify

import sys
sys.path.append('/../')
import zot_n_ride as ZNR
import bcrypt

@app.route('/')
@app.route('/home')
@app.route('/welcome')
def welcome():
    return 'Welcome to Zot n\' Ride!'

@app.route('/user/<username>')
def display_profile(username):
    return 'User {}'.format(username)

#Endpoint for creating a user
@app.route('/api/register',methods=['POST'])
def register_user():
    if not request.json:
        abort(400)
    body=request.json
    hashedPW=bcrypt.hashpw(body['password'].encode('utf-8'),bcrypt.gensalt(12))
    query=ZNR.create_user_into_db(body['netID'],hashedPW,body['firstname'],body['lastname'],body['major'],body['address'],body['isDriver'])
    if(query == None):
        abort(400)
    return json.dumps(request.json)

#Endpoint for validating a login
@app.route('/api/login',methods=['POST'])
def login_user():
    if not request.json:
        abort(400)
    body=request.json
    query=ZNR.validate_login(body['email'],body['password'])
    if(not query):
        abort(400)
    return json.dumps(request.json)
    
