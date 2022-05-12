import pandas as pd
import requests, json, logging, smtplib, datetime
from flask import render_template, url_for, flash, redirect
from canvasadmin import app
from canvasadmin.forms import RegistrationForm, LoginForm
from canvasadmin.models import User, Post
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
from pathlib import Path
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from logging.handlers import SysLogHandler

posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/asap")
def asap():
    home = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
    confighome = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
    with open(confighome) as f:
        configs = json.load(f)
    # Logging
    if configs['logserveraddress'] is None:
        logfilename = Path.home() / ".ASAPCanvas" / configs['logfilename']
        thelogger = logging.getLogger('MyLogger')
        thelogger.basicConfig(filename=str(logfilename), level=thelogger.info)
    else:
        thelogger = logging.getLogger('MyLogger')
        thelogger.setLevel(logging.DEBUG)
        handler = logging.handlers.SysLogHandler(address = (configs['logserveraddress'],514))
        thelogger.addHandler(handler)
    userid = configs['ASAPuserid']
    orgid = configs['ASAPorgid']
    password = configs['ASAPpassword']
    apikey = configs['ASAPAPIKey']
    url = configs['ASAPurl']
    headers = {'Authorization' : 'user='+userid+'&organizationId='+orgid+'&password='+password+'&apiKey='+apikey}
    thelogger.info('Canvas Admin Web->Getting ASAP Key')
    r = requests.get(url,headers = headers)
    if r.status_code == 404:
        thelogger.info('Canvas Admin Web->Failed to get ASAP Key')
        if configs['Debug'] == "True":
            thelogger.info('Canvas Admin Web->Failed to get ASAP Key')
    elif r.status_code == 200:
        thelogger.info('Canvas Admin Web->Got ASAP Key')
        accesstoken = r.json()
        thelogger.info('Canvas Admin Web->Key is ' + accesstoken)
        url2 = configs['ASAPapiurl']
        header = {'asap_accesstoken' : accesstoken}
        thelogger.info('Canvas Admin Web->Getting data from ASAP')
        r2 = requests.get(url2,headers = header)
        results = pd.concat([pd.json_normalize(r2.json()), pd.json_normalize(r2.json(),record_path="Students", max_level=2)], axis=1).drop(columns='Students')
        # was drop('Students',1)
        #Drop columns we don't need
        results.drop(results.columns.difference(['CreatedDate',
                                                'EventEnrollmentID',
                                                'ScheduledEvent.Course.CourseName',
                                                'ScheduledEvent.Course.IsOnline',
                                                'EnrollmentStatusCd',
                                                'ScheduledEvent.EventCd',
                                                'StudentID',
                                                'CustomerID',
                                                'Person.Email',
                                                'Person.FirstName',
                                                'Person.LastName']),axis=1,inplace=True)
        results = results.rename(columns={'CreatedDate':'Created Date',
                                            'EnrollmentStatusCd':'Enrollment Status',
                                            'EventEnrollmentID':'Enroll ID',
                                            'Student ID':'Student ID',
                                            'ScheduledEvent.Course.CourseName':'Course Name',
                                            'ScheduledEvent.Course.IsOnline':'Course Online',
                                            'ScheduledEvent.EventCd':'Event CD',
                                            'CreatedDate':'Created Date2',
                                            'CustomerID':'Customer ID',
                                            'Person.Email':'Email',
                                            'Person.FirstName':'FirstName',
                                            'Person.LastName':'LastName'})
        print(results)
        return render_template('asap.html', title='ASAP', tables=[results.to_html(classes='data')], titles=results.columns.values)

@app.route("/asapclasses", methods=['GET', 'POST'])
def asapclasses():
    return render_template('about.html', title='About')  

@app.route("/asapstudents", methods=['GET', 'POST'])
def asapstudents():
    return render_template('about.html', title='About')

@app.route("/canvasclasses", methods=['GET', 'POST'])
def canvasclasses():
    return render_template('about.html', title='About')

@app.route("/canvasstudents", methods=['GET', 'POST'])
def canvasstudents():
    return render_template('about.html', title='About')