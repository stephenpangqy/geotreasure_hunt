from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
import requests
from datetime import datetime
from flask_cors import CORS
import os, sys
from invokes import invoke_http
import json

app = Flask(__name__)
CORS(app)

# TEMP USERNAME: Need to figure out a way to update or pass this
username = 'Meghan'

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
                box_info = box['result']
                if username == box_info['planted_by_username']:
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
                        print("----------Invoking User microservice to update user's balance and inventory-------------")
                        print(update_user)
                        if update_user['code'] == 201:
                            return jsonify({
                                "code":200,
                                "rewards": {
                                    "prize": update_user['data']['item_won'],
                                    "points": update_user['data']['points_earned']
                                }
                            }),200


            elif box['code'] == 404:
                return jsonify({
                    "code":404,
                    "message": "There are no nearby boxes for you to open."
                }),404



    except Exception as e:
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
