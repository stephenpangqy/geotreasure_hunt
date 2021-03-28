from flask import Flask, render_template, jsonify, request
from invokes import invoke_http
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
import requests
import json
import amqp_setup
import pika
app = Flask(__name__)
CORS(app)


user_URL = environ.get('user_URL') or "http://localhost:5004/user/purchase/"
in_game_URL = environ.get('ingame_shop_URL') or "http://localhost:5005/order"


@app.route('/order',methods = ['POST'])
def take_order():
   # JSON TAKEN IN: { username, data: [ {name, qty}, {item, qty}, ... ]}
   if request.method == 'POST':
       # This depends on the form submission format
       data = request.get_json()
       name = data['username']
       message = {
            "user": name,
            "action": "Purchase from Shop"
       }
       print(data)
       print('\n-----Invoking in-game shop microservice-----')
       get_item = invoke_http(in_game_URL, method='POST',json = data)
       print(get_item)
       if get_item['code'] == 500:
            message['error'] = "An error occurred while purchasing"
            return jsonify(get_item)
       else:
            print('\n-----Invoking user microservice to update purchase-----')
            user_update = invoke_http(user_URL + name, method='PUT',json = get_item)
            # If got Error
            if user_update['code'] not in range(200,300):
                message['error'] = user_update['message']
                amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key='order.error',
                body=json.dumps(message), properties=pika.BasicProperties(delivery_mode = 2 ))
            # If got no error
            else:
                message['success'] = "Purchase successful"
                message['currencyUsed'] = user_update['currencyUsed']
                message['items_received'] = user_update['items_received']
                amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key='order.activity',
                body=json.dumps(message), properties=pika.BasicProperties(delivery_mode = 2 ))
                
            
            return jsonify(user_update)




if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5007, debug=True)
     
