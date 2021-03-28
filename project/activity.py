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
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3306/activitylog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

class Activity(db.Model):
    __tablename__ = 'activitylog'
    id = db.Column(db.Integer, primary_key=True)
    activityType = db.Column(db.String(300), nullable=False)
    activityDatetime = db.Column(db.DateTime, nullable=False)
    activityDesc = db.Column(db.String(400))
    user_Involved = db.Column(db.String(300))
    ItemsReceived = db.Column(db.String(400))
    currencyGained = db.Column(db.Integer)
    currencyUsed = db.Column(db.Integer)

    # def __init__(self,id,activityType,activityDatetime,activityDesc,user_Involved,ItemsReceived,currencyGained,currencyUsed):
    #     self.id = id
    #     self.activityType = activityType
    #     self.activityDatetime = activityDatetime
    #     self.activityDesc = activityDesc
    #     self.user_Involved = user_Involved
    #     self.ItemsReceived = ItemsReceived
    #     self.currencyGained = currencyGained
    #     self.currencyUsed = currencyUsed








# i classified different microservices' activity by the microservice name
# so i used topic exchange not fanout
monitorBindingKey='*.activity'

# ------ Start consuming messages ------ #
def consume():
    amqp_setup.check_setup()
    queue_name = 'Activity_log'
    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    amqp_setup.channel.start_consuming()

# ------ print the file/microservice to retrieve activity from ------ #
def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nReceived an activity log by " + __file__)
    processOrderLog(json.loads(body))
    print() # print a new line feed

# ------ print the activity log------ #
def processOrderLog(order): 
    print("Recording an activity log:")
    print(order)
    # ADD TO ACTIVITY DB
    activityDatetime = datetime.now()
    activityType = order['action']
    user_Involved = order['user']
    activityDesc = order['success']
    ItemsReceived = None
    currencyGained = None
    currencyUsed = None
    if 'items_received' in order.keys():
        ItemsReceived = order['items_received']
    if 'currencyGained' in order.keys():
        currencyGained = order['currencyGained']
    if 'currencyUsed' in order.keys():
        currencyUsed = order['currencyUsed']
    activity = Activity(activityType=activityType,activityDatetime=activityDatetime,activityDesc=activityDesc,user_Involved=user_Involved,ItemsReceived=ItemsReceived,currencyGained=currencyGained,currencyUsed=currencyUsed)
    db.session.add(activity)
    db.session.commit()

if __name__ == "__main__":  
    print("\nThis is " + os.path.basename(__file__), end='')
    print(": monitoring routing key '{}' in exchange '{}' ...".format(monitorBindingKey, amqp_setup.exchangename))
    consume()