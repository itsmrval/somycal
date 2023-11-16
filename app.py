from flask import Flask, redirect, url_for, session
from flask_oauthlib.client import OAuth
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = 'fjlksjfnklsdfnsdklfnsdkjfnsdjkfnds'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

oauth = OAuth(app)

google = oauth.remote_app(
    'google',
    consumer_key=os.getenv('GOOGLE_KEY'),
    consumer_secret=os.getenv('GOOGLE_SECRET'),
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idTeam = db.Column(db.Integer, unique=True)
    idUser = db.Column(db.Integer, db.ForeignKey('user.id'))

def addTeam(idUser, idTeam):
    team = Team(idTeam=idTeam, idUser=idUser)
    db.session.add(team)
    db.session.commit()

def getTeamName(idTeam):


def getTeams(idUser):
    teams = Team.query.filter_by(idUser=idUser).all()
    return teams


@app.route('/')
def index():
    if 'google_token' in session:
        me = google.get('userinfo')
        user = User.query.filter_by(email=me.data['email']).first()
        if user is None:
            user = User(email=me.data['email'])
            db.session.add(user)
            db.session.commit()
        return 'Logged in as: ' + me.data['email']
    return redirect("/login", code=302)

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect("/", code=302)

@app.route('/login/authorized')
def authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (response['access_token'], '')
    return redirect("/", code=302)

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)