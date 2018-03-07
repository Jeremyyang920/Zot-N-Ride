from flask import Flask
from flask_pymongo import PyMongo
from flask.ext.bcrypt import Bcrypt

app = Flask(__name__)

from app import routes
bcrypt=Bcrypt(app)
