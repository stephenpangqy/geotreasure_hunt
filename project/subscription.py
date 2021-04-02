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


@app.route('/',methods=["POST"])
def updateMembership():
    # JSON RECEIVED { "code", username }
    print(request.get_json())
    code = request.json.get('code')
    username = request.json.get('username')
    if code == 200:
        current_date = datetime.today().strftime('%Y-%m-%d')
        submit_json = {
            "username": username,
            "membership-date": current_date
        }
        print("--------Invoking User microservice to update membership---------")
        membership_url = environ.get('user_URL') or 'http://localhost:5004/user/membership/'
        member_update = invoke_http(membership_url + username,'PUT',submit_json)
        amqp_setup.check_setup()
        message = {
            "user": username,
            "action": "Subscription Payment"
        }
        if member_update['code'] == 200:
            message['success'] = member_update['message']
            amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="subscription.activity", 
            body=json.dumps(message), properties=pika.BasicProperties(delivery_mode = 2))
            return jsonify({
                "code":200,
                "message": member_update['message'],
                "data": member_update['data']
            }), 200
        else:
            message['error'] = member_update['message']
            amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="subscription.error", 
            body=json.dumps(message), properties=pika.BasicProperties(delivery_mode = 2))
            return jsonify({
                "code": member_update['code'],
                "message": "An error occurred: " + member_update['message']
            }), member_update['code']


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5006,debug=True)