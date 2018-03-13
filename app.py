from flask import Flask,abort,request,Response
import json
from flask import jsonify
from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo

app = Flask(__name__)

import sys
import zot_n_ride as ZNR
import bcrypt

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/')
@app.route('/home')
@app.route('/welcome')
def welcome():
    return 'Welcome to Zot n\' Ride!'

@app.route('/user/<username>')
def display_profile(username):
    return 'User {}'.format(username)

#Endpoint for Creating a User
@app.route('/api/register',methods=['POST'])
def register_user():
    if not request.json:
        abort(400)
    body = request.json
    hashedPW = bcrypt.hashpw(body['password'].encode('utf-8'),bcrypt.gensalt(12))
    query = ZNR.create_user_into_db(body['netID'],hashedPW,body['firstname'],body['lastname'],body['major'],body['address'],body['isDriver'])
    if query == None:
        abort(400)
    return query

#Endpoint for Validating a Login
@app.route('/api/login',methods=['POST'])
def login_user():
    if not request.json:
        abort(400)
    body = request.json
    query = ZNR.validate_login(body['netID'],body['password'])
    if not query:
        abort(400)
    return query
    
