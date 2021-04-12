from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
import requests
from datetime import datetime
from flask_cors import CORS
import os, sys
from invokes import invoke_http
import amqp_setup
import pika
import json

app = Flask(__name__)
CORS(app)

@app.route("/",methods=["POST"])
def OpenNearbyBox():
    # JSON PASSED INTO: {user}
    try:
        data = request.get_json()
        username = data['user']
        message = {
            "user": username,
            "action": "Box Opening"
        }
        amqp_setup.check_setup()
        user_location = getLocation()
        print("----------Invoking geolocation microservice------------")
        print(user_location)
        if user_location['code'] == 200:
            latitude = user_location['result']['location']['lat']
            longitude = user_location['result']['location']['lng']
            nearest_URL = environ.get('box_nearest_URL') or 'http://localhost:5002/search?latitude='
            get_nearest_box_URL = nearest_URL + str(latitude) + '&longitude=' + str(longitude)
            box = getNearestBox(get_nearest_box_URL)
            print("---------Invoking Box microservice to get nearest box-----------")
            print(box)
            if box['code'] == 200:
                box_info = box['result']
                if username == box_info['planted_by_username']:
                    openyourownboxmessage = 'Box found but cannot be open as it is a self-planted box.'
                    message['error'] = openyourownboxmessage
                    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key='box_opening.error',
                    body=json.dumps(message), properties=pika.BasicProperties(delivery_mode=2))
                    return jsonify({
                        "code":500,
                        "message": "You found your box! Unfortunately, you cant open your own box."
                    }),200
                else:
                    box_id = box_info['boxid']
                    box_update_url = environ.get('box_update_URL') or 'http://localhost:5002/open'
                    update_box_open = invoke_http(box_update_url,'PUT',{'boxid':box_id})
                    print("------Invoking Box microservice to Update Status of Box to Y--------------")
                    print(update_box_open)
                    if update_box_open['code'] == 200:
                        update_user = updateUser(box_info,username)
                        print("----------Invoking User microservice to update user's balance and inventory-------------")
                        print(update_user)
                        if update_user['code'] == 200:
                            message['success'] = "Updated user's balance and inventory successfully"
                            message['items_received'] = update_user['data']['item_won']
                            message['currencyGained'] = update_user['data']['points_earned']
                            amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key='box_opening.activity',
                            body=json.dumps(message), properties=pika.BasicProperties(delivery_mode=2))
                            return jsonify({
                                "code":200,
                                "rewards": {
                                    "prize": update_user['data']['item_won'],
                                    "points": update_user['data']['points_earned']
                                }
                            }),200 # changed this to 200 because it initially wouldnt display


            elif box['code'] == 404:
                message['error'] = "There are no nearby boxes for you to open"
                amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key='box_opening.error',
                    body=json.dumps(message), properties=pika.BasicProperties(delivery_mode=2))
                return jsonify({
                    "code":404,
                    "message": "There are no nearby boxes for you to open."
                }),200 # changed this to 200 because it initially wouldnt display



    except Exception as e:
        message['error'] = "Internal Error in box_opening.py: " + str(e)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key='box_opening.error',
                    body=json.dumps(message), properties=pika.BasicProperties(delivery_mode=2))
        return jsonify({
            "code":500,
            "message":"The site encountered an internal error: " + str(e)
        }),500


def getLocation():
    geolocation_URL = environ.get('geolocation_URL') or "http://localhost:5001/"
    location = invoke_http(geolocation_URL)
    return location

def getNearestBox(url):
    box = invoke_http(url)
    return box

def updateUser(boxjson,username):
    user_url = environ.get('user_URL') or 'http://localhost:5004/user/openbox/'
    user_openbox_url = user_url + username
    update = invoke_http(user_openbox_url,'PUT',boxjson)
    return update

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5003, debug=True)
