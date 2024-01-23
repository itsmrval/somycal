from flask import Flask, redirect, url_for, session, render_template, Response, request
from flask_oauthlib.client import OAuth, OAuthRemoteApp
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from icalendar import Calendar, Event
import os, requests, pytz, hashlib
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SESSION_SECRET')
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

def getUserTeams(idUser):
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
    return f"static/logo/team_nba/team_{idTeam}.png"

def getSchedules():
    response = requests.get("https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json")
    matches_info = []

    for game_date in response.json()['leagueSchedule']['gameDates']:
        for game in game_date['games']:
            match_info = {
                'gameDateTimeUTC': game['gameDateTimeUTC'],
                'weekNumber': game['weekNumber'],
                'arenaName': game['arenaName'],
                'seriesText': game['seriesText'],
                'hometeamName': game['homeTeam']['teamName'],
                'awayteamName': game['awayTeam']['teamName'],
                'url': game['branchLink'],
                'arenaCity': game['arenaCity'],
                'hometeamTricode': game['homeTeam']['teamTricode'],
                'awayteamTricode': game['awayTeam']['teamTricode'],
                'hometeamScore': game['homeTeam']['score'],
                'awayteamScore': game['awayTeam']['score'],
            }
            matches_info.append(match_info)
    return matches_info

def getTeamMatches(idTeam):
    result = []
    matches_info = getSchedules()
    for i in matches_info:
        if (i['hometeamName'] == getTeamName(idTeam) or i['awayteamName'] == getTeamName(idTeam)):
            result.append(i)
    return result

def getUserMatches(idUser):
    result = []
    teams = getUserTeams(idUser)
    for i in teams:
        result += getTeamMatches(i.idTeam)
    return result

def convert_to_datetime(date_str):
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.UTC)

def generate_ical(events):
    cal = Calendar()
    for event_data in events:
        event = Event()
        event.add('summary', f"{event_data['hometeamTricode']} vs {event_data['awayteamTricode']} 🏀")
        event.add('location', f"🏟 {event_data['arenaName']}, {event_data['arenaCity']}")
        event.add("description", f"🎖️Scores: \n{event_data['hometeamName']} {event_data['hometeamScore']} - {event_data['awayteamScore']} {event_data['awayteamName']}")
        event.add("url", event_data['url'])
        event.add('dtstart', datetime.strptime(event_data['gameDateTimeUTC'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.UTC))
        event.add('dtend', datetime.strptime(event_data['gameDateTimeUTC'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.UTC) + timedelta(hours=3))

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

        return render_template('dashboard.html', userTeams=getUserTeams(user.id), otherTeams=otherTeams, getTeamName=getTeamName, getTeamLogo=get_team_logo, userId=user.id)


    return render_template('index.html')

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


@app.route('/calendar/<int:user_id>.ics')
def generate_ical_feed(user_id):
    events = getUserMatches(user_id)
    ical_content = generate_ical(events)

    response = Response(
        ical_content,
        content_type='text/calendar',
        headers={
            'Content-Disposition': 'inline; filename=calendar.ics',
            'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
            'Pragma': 'no-cache',
            'Expires': '0',
        }
    )

    return response

@app.route('/login/google')
def google_redirect():
    if 'instagram' in request.headers.get('User-Agent').lower() or 'facebook' in request.headers.get('User-Agent').lower():
        return render_template('open_in_browser.html')
    return google.authorize(callback=url_for('authorized', _external=True, _scheme='https'))

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

    app.run(debug=True, port=8000, host='127.0.0.1')
