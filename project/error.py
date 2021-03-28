from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from os import environ
import requests
from datetime import datetime

import json
import os
import amqp_setup

app = Flask(__name__)

# SQL settings
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3306/errorlog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

class Error(db.Model):
    __tablename__ = 'errorlog'
    errorID = db.Column(db.Integer, primary_key=True)
    user_Involved = db.Column(db.String(300))
    errorType = db.Column(db.String(300), nullable=False)
    errorDescription = db.Column(db.String(400))
    errorDatetime = db.Column(db.DateTime, nullable=False)

    # def __init__(self,errorID,user_Involved,errorType,errorDescription,errorDatetime):
    #     self.errorID = errorID
    #     self.user_Involved = user_Involved
    #     self.errorType = errorType
    #     self.errorDescription = errorDescription
    #     self.errorDatetime = errorDatetime

monitorBindingKey='*.error'

def receiveError():
    amqp_setup.check_setup()
    
    queue_name = "Error"  

    # set up a consumer and start to wait for coming messages
    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    amqp_setup.channel.start_consuming() # an implicit loop waiting to receive messages; 
    #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.

def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nReceived an error by " + __file__)
    processError(body)
    print() # print a new line feed

def processError(errorMsg):
    print("Printing the error message:")
    try:
        error = json.loads(errorMsg)
        print("--JSON:", error)
        # ADD TO ERROR DB
        user_Involved = error['user']
        errorType = error['action']
        errorDescription = error['error']
        errorDatetime = datetime.now()
        error = Error(user_Involved=user_Involved,errorType=errorType,errorDescription=errorDescription,errorDatetime=errorDatetime)
        db.session.add(error)
        db.session.commit()
    except Exception as e:
        print("--NOT JSON:", e)
        print("--DATA:", errorMsg)
    print()


if __name__ == "__main__":  # execute this program only if it is run as a script (not by 'import')    
    print("\nThis is " + os.path.basename(__file__), end='')
    print(": monitoring routing key '{}' in exchange '{}' ...".format(monitorBindingKey, amqp_setup.exchangename))
    receiveError()