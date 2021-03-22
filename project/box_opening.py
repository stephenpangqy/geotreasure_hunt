from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
import requests
from datetime import datetime
from flask_cors import CORS
import os, sys
from invokes import invoke_http
import json
import amqp_setup
import pika

app = Flask(__name__)
CORS(app)

# TEMP USERNAME: Need to figure out a way to update or pass this
username = 'Michelle'

@app.route("/")
def OpenNearbyBox():
    try:
        user_location = getLocation()
        print("----------Invoking geolocation microservice------------")
        print(user_location)
        if user_location['code'] == 200:
            latitude = user_location['result']['location']['lat']
            longitude = user_location['result']['location']['lng']
            get_nearest_box_URL = 'http://localhost:5002/search?latitude=' + str(latitude) + '&longitude=' + str(longitude)
            box = getNearestBox(get_nearest_box_URL)
            print("---------Invoking Box microservice to get nearest box-----------")
            print(box)
            if box['code'] == 200:
                foundmessage = box['message']
                box_info = box['result']
                # found box activity sent to amqp
                amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key='box_opening.activity',
                body=foundmessage, properties=pika.BasicProperties(delivery_mode=2))
                
                if username == box_info['planted_by_username']:
                    openyourownboxmessage = 'Box found but cannot be open as it is a self-planted box.'
                    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key='box_opening.activity',
                    body=openyourownboxmessage, properties=pika.BasicProperties(delivery_mode=2))

                    return jsonify({
                        "code":403,
                        "message": "You found your box! Unfortunately, you cant open your own box."
                    }),403
                    

                else:
                    box_id = box_info['boxid']
                    update_box_open = invoke_http('http://localhost:5002/open','PUT',{'boxid':box_id})
                    print("------Invoking Box microservice to Update Status of Box to Y--------------")
                    print(update_box_open)
                    if update_box_open['code'] == 200:
                        update_user = updateUser(box_info,username)
                        open_message = update_box_open['message']
                        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key='box_opening.activity',
                        body=open_message, properties=pika.BasicProperties(delivery_mode=2))
                        print("----------Invoking User microservice to update user's balance and inventory-------------")
                        print(update_user)
                        if update_user['code'] == 201:
                            updatecontentandpoints = 'Successful update of new content and points for {points}'
                            amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="box_opening.activity", 
                            body=updatecontentandpoints, properties=pika.BasicProperties(delivery_mode = 2)) 
                            return jsonify({
                                "code":200,
                                "rewards": {
                                    "prize": update_user['data']['item_won'],
                                    "points": update_user['data']['points_earned']
                                }
                            }),200


            elif box['code'] == 404:
                noboxnearby = box['message']
                amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="box_opening.activity", 
                body=noboxnearby, properties=pika.BasicProperties(delivery_mode = 2)) 
                return jsonify({
                    "code":404,
                    "message": "There are no nearby boxes for you to open."
                }),404


    except Exception as e:
        errorfinding = "box_opening.py encountered an internal error: " + str(e)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="box_opening.error", 
        body=errorfinding, properties=pika.BasicProperties(delivery_mode = 2)) 

        return jsonify({
            "code":500,
            "message":"box_opening.py encountered an internal error: " + str(e)
        }),500


def getLocation():
    geolocation_URL = "http://localhost:5001/"
    location = invoke_http(geolocation_URL)
    return location

def getNearestBox(url):
    box = invoke_http(url)
    return box

def updateUser(boxjson,username):
    user_openbox_url = 'http://localhost:5004/user/openbox/' + username
    update = invoke_http(user_openbox_url,'PUT',boxjson)
    return update

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5003, debug=True)
