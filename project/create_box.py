from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
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
    print("----------Invoking User Microservice to Check Boxes left-------")
    checkbox_url = environ.get('checkbox_URL') or "http://localhost:5004/user/boxcount/"
    check_result = invoke_http(checkbox_url + user)
    if check_result['code'] != 200:
        message['error'] = check_result['message']
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key='box.error',
        body=json.dumps(message), properties=pika.BasicProperties(delivery_mode=2))
        return jsonify({
            "code": check_result['code'],
            "message": "Error occurred while checking how many boxes user has."
        })
    else:
        if check_result['data']['daily_boxes'] < 1:
            message['error'] = "User has no boxes to plant."
            amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key='box.error',
            body=json.dumps(message), properties=pika.BasicProperties(delivery_mode=2))
            return jsonify({
                "code": 404,
                "message": "You have no boxes to plant."
            })
        else:
            geolocation_url = environ.get('geolocation_URL') or "http://localhost:5001/"
            print("-------Invoking Geolocation Microservice-----------------")
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
                createbox_url = environ.get('box_create_URL') or "http://localhost:5002/"
                print("-------Invoking Box Microservice to create a box---------------")
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
                    print("------Invoking User microservice to subtract box use--------")
                    usebox_url = environ.get('usebox_URL') or "http://localhost:5004/user/useBox"
                    usebox_result = invoke_http(usebox_url,'PUT',{'username': user})
                    if usebox_result['code'] != 200:
                        message['error'] = usebox_result['message']
                        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key='box.error',
                        body=json.dumps(message), properties=pika.BasicProperties(delivery_mode=2))
                        return jsonify({
                            "code": usebox_result['code'],
                            "message": usebox_result['message']
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