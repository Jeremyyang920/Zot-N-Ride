from app import app

@app.route('/')
@app.route('/home')
@app.route('/welcome')
def welcome():
    return 'Welcome to Zot n\' Ride!'

@app.route('/user/<username>')
def display_profile(username):
    return 'User {}'.format(username)
