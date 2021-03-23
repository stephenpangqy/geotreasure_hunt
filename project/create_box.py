from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from invokes import invoke_http
import requests
import random
import amqp_setup
import pika
import json

app = Flask(__name__)
CORS(app)

@app.route("/",methods=["POST"])
def createBox():
    # JSON PASSED: { "user" }
    data = request.get_json()
    user = data['user']
    amqp_setup.check_setup()
    message = {
        "user": user,
        "action": "Box Creation"
    }
    geolocation_url = "http://localhost:5001/"
    geo_result = invoke_http(geolocation_url)
    if geo_result['code'] != 200:
        message['error'] = "An error occurred fetching the user's location."
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key='box.error',
        body=json.dumps(message), properties=pika.BasicProperties(delivery_mode=2))
        return jsonify({
            "code": geo_result['code'],
            "message": "Error occurred while fetching user's location."
        })
    else:
        create_json = {
            "username": user,
            "latitude": geo_result['result']['location']['lat'],
            "longitude": geo_result['result']['location']['lng']
        }
        createbox_url = "http://localhost:5002/"
        result = invoke_http(createbox_url,"POST",create_json)
        if result['code'] != 201:
            message['error'] = "Error occurred creating box : " + result['message']
            amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key='box.error',
            body=json.dumps(message), properties=pika.BasicProperties(delivery_mode=2))
            return jsonify({
                "code": result['code'],
                "message": "Error occurred creating box : " + result['message']
            })
        else:
            message['success'] = "Box created sucessfully at coordinates > lat: " + str(geo_result['result']['location']['lat']) + " lng: " + str(geo_result['result']['location']['lng'])
            amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key='box.activity',
            body=json.dumps(message), properties=pika.BasicProperties(delivery_mode = 2 ))
            return jsonify({
                "code": 201,
                "message": result['message']
            })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5008, debug=True)