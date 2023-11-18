from flask import Flask, redirect, url_for, session, render_template, Response
from flask_oauthlib.client import OAuth
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from icalendar import Calendar, Event
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

teams_dict = {
    1: "Lakers",
    2: "Heat",
    3: "Warriors",
    4: "Celtics",
    5: "Spurs",
    6: "Knicks",
    7: "Pistons",
    8: "Magic",
    9: "Suns",
    10: "Pacers",
    11: "Jazz",
    12: "Trail Blazers",
    13: "Raptors",
    14: "Mavericks",
    15: "Bucks",
    16: "Thunder",
    17: "Bulls",
    18: "Pelicans",
    19: "Rockets",
    20: "Kings",
    21: "Clippers",
    22: "Cavaliers",
    23: "Hawks",
    24: "Grizzlies",
    25: "Nuggets",
    26: "Hornets",
    27: "76ers",
    28: "Wizards",
    29: "Timberwolves",
    30: "Nets"
}

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

def deleteTeam(idTeam):
    team = Team.query.filter_by(idTeam=idTeam).first()
    db.session.delete(team)
    db.session.commit()

def getTeamName(idTeam):
    return teams_dict[idTeam]

def getTeams(idUser):
    teams = Team.query.filter_by(idUser=idUser).all()
    return teams

def assignTeam(idUser, idTeam):
    team = Team.query.filter_by(idTeam=idTeam).first()
    if team is None:
        addTeam(idUser, idTeam)
    else:
        team.idUser = idUser
        db.session.commit()

def get_team_logo(idTeam):
    # Supposons que les logos sont stockés dans le dossier 'static/logos/' avec des noms comme 'team1.png', 'team2.png', etc.
    return f"static/logo/team_nba/team_{idTeam}.png"

def createEvent(summary, start_time, end_time):
    event = Event()
    event.add('summary', summary)
    event.add('dtstart', start_time)
    event.add('dtend', end_time)
    return event

def generateIcal(events):
    cal = Calendar()
    for event_data in events:
        event = createEvent(
            event_data['summary'],
            event_data['start_time'],
            event_data['end_time']
        )
        cal.add_component(event)
    return cal.to_ical()

@app.route('/')
def index():
    if 'google_token' in session:
        me = google.get('userinfo')
        if (not(me.data['email'])):
            return redirect("/logout", code=302)
        user = User.query.filter_by(email=me.data['email']).first()
        if user is None:
            user = User(email=me.data['email'])
            db.session.add(user)
            db.session.commit()

        otherTeams = []

        for i in list(teams_dict.keys()):
            if (Team.query.filter_by(idUser=user.id, idTeam=i).first() is None):
                otherTeams.append(i)

        return render_template('index.html', userTeams=getTeams(user.id), otherTeams=otherTeams, getTeamName=getTeamName, getTeamLogo=get_team_logo)

    return redirect("/login", code=302)

@app.route('/add/<int:idTeam>')
def addTeamRoute(idTeam):
    if 'google_token' in session:
        me = google.get('userinfo')
        user = User.query.filter_by(email=me.data['email']).first()
        if user is None:
            user = User(email=me.data['email'])
            db.session.add(user)
            db.session.commit()

        assignTeam(user.id, idTeam)
        return redirect("/", code=302)
    return redirect("/login", code=302)

@app.route('/del/<int:idTeam>')
def delTeamRoute(idTeam):
    if 'google_token' in session:
        me = google.get('userinfo')
        user = User.query.filter_by(email=me.data['email']).first()
        if user is None:
            user = User(email=me.data['email'])
            db.session.add(user)
            db.session.commit()

        deleteTeam(idTeam)
        return redirect("/", code=302)
    return redirect("/login", code=302)

@app.route('/calendar')
def download_ical():
    if 'google_token' in session:
        me = google.get('userinfo')
        user = User.query.filter_by(email=me.data['email']).first()
        if user is None:
            user = User(email=me.data['email'])
            db.session.add(user)
            db.session.commit()

        user_teams = getTeams(user.id)

        events_data = []
        for team in user_teams:
            team_events = parseTeamEvents(team.events)
            events_data.extend(team_events)

        ical_data = generateIcal(events_data)

        response = Response(ical_data, content_type='text/calendar')
        response.headers['Content-Disposition'] = 'inline; filename=calendar.ics'
        return response

    return redirect("/login", code=302)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login/google')
def google_redirect():
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

    app.run(debug=True, port=5050)