from app import app
from app import scraper
from app import db
from app import models
from flask import render_template, request, session, redirect, url_for
from datetime import datetime

@app.route('/')
@app.route('/index')
def index():
    currentUser = getCurrentUser()
    dbFights = models.Fight.query.all()
    fights = []

    latestDate = dbFights[len(dbFights) - 1].date
    eventName = dbFights[len(dbFights) - 1].event
    for fight in dbFights:
        if(fight.date == latestDate):
            fights.append(fight)

    if currentUser:
        return render_template('index.html', logged_in=True,
                               user_name=currentUser, fights=fights,
                               event_name=eventName)
    return render_template('index.html', logged_in=False, fights=fights, event_name=eventName)

@app.route('/signup')
def signUp():
    currentUser = getCurrentUser()
    if currentUser:
        return render_template('signUp.html', logged_in=True, user_name=currentUser)
    return render_template('signUp.html', logged_in=False)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/registerUser', methods=["POST", "GET"])
def registerUser():
    if request.method == "POST":
        # check if form is empty
        if not request.form['name'] or not request.form['email'] or not request.form['password']:
            return render_template("signUp.html", empty_form=True, emailError=True)

        else:
            # check if email/username already exists in database
            emailQuery = models.User.query.filter_by(email=request.form['email']).first()
            nameQuery = models.User.query.filter_by(name=request.form['name']).first()

            if (not emailQuery and not nameQuery):
                # add User to database
                newUser = models.User(request.form['name'], request.form['email'], request.form['password'], 0)

                session['username'] = request.form['name']
                session['email'] = request.form['email']

                db.session.add(newUser)
                db.session.commit()
                return redirect(url_for('index'))
            else:
                # email already exists
                emailErr = False
                nameErr = False
                if(emailQuery):
                    emailErr = True
                if(nameQuery):
                    nameErr = True
                return render_template("signUp.html", empty_form=False, emailError=emailErr, nameError=nameErr)
    return render_template("signUp.html")


@app.route('/signInUser', methods=['POST', 'GET'])
def signInUser():
    if request.method == 'POST':
        # check if form is empty
        if not request.form['email'] or not request.form['password']:
            return render_template('login.html', incorrect_login=True)

        else:
            user = models.User.query.filter_by(email=request.form['email']).first()

            if user and user.password == request.form['password']:
                session['username'] = user.name
                session['email'] = request.form['email']

                return redirect(url_for('index'))

            else:
                return render_template('login.html', incorrect_login=True)

@app.route('/placeBets')
def placeBets():
    user = getCurrentUser()
    loggedIn = False
    if user: loggedIn = True
    allFights = models.Fight.query.all()
    eventName = allFights[-1].event

    fights = []
    for fight in allFights:
        if(fight.event == eventName):
            fights.append(fight)

    return render_template('placeBets.html', event_name=eventName,
                           fights=fights, user_name=user, logged_in=loggedIn)

@app.route('/createBet/<int:fightID>', methods = ['POST'])
def createBet(fightID):
    if request.method == 'POST':
        user = getCurrentUser()

        if not user:
            return redirect(url_for('login'))
        else:
            usermodel = models.User.query.filter_by(email=session['email']).first()

        if not request.form['betAmount'] or len(request.form) < 2:
            return redirect(url_for('placeBets'))
        elif int(request.form['betAmount']) > usermodel.balance:
            print("TOO LARGE")
        else:
            newBet = models.Bet(fightID=fightID,
                                userID=usermodel.id,
                                amount=int(request.form['betAmount']))
            usermodel.balance -= int(request.form['betAmount'])
            db.session.add(newBet)
            db.session.commit()
            print("New bet added to database")


    return redirect(url_for('placeBets'))



def getCurrentUser():
    currentUser = None
    if 'username' in session:
        currentUser = session['username']
    return currentUser
