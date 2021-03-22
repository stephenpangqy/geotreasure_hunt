from flask import Flask, render_template, jsonify, request
from invokes import invoke_http
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

import requests
import json
app = Flask(__name__)
CORS(app)


user_URL = "http://localhost:5004/"
in_game_URL = "http://localhost:5005/"
activity_URL = "http://localhost:5672"
error_URL = "http://localhost:5672/"

name = 'Christine'




@app.route('/order',methods = ['POST'])
def take_order():
    # FIX THIS
    # JSON TAKEN IN: { data: [ {name, qty}, {item, qty}, ... ]}
    if request.method == 'POST':
        # This depends on the form submission format
        data = request.get_json()
        print(data)
        print('\n-----Invoking in-game shop microservice-----')
        get_item = invoke_http(in_game_URL + "order", method='POST',json = data)
        print(get_item)
        if get_item['code'] == 500:
            noorder = 'No order request made or unsuccessful request'
            return jsonify(get_item)
        else:
            print('\n-----Invoking user microservice-----')
            user_update = invoke_http(user_URL + "user/purchase/" + name, method='PUT',json = get_item)
            
            return jsonify(user_update)



#user_balance = invoke_http(user_URL + "user/balance/" + name , method='GET')
#print('order_result:', user_balance)
#user_update = invoke_http(user_URL + "user/purchase/" + name, methods='PUT')      


#def get_order(data):
    #try:
       # a_json = json.loads(data)
        #return print("String  converted to JSON")
    #except:
         #return print("String could not be converted to JSON")
    #if data.is_json:
        #try:
            #order = request.get_json()
            #print("\nReceived an order in JSON:", order)
            #result = processOrder(order)
            #return jsonify(result), 200
        #except Exception as e:
            #pass  # do nothing.

    #if reached here, not a JSON request.
    #return jsonify({
        #"code": 400,
        #"message": "Invalid JSON input: " + str(request.get_data())
    #}), 400



#def processOrder(order):
    # 1. get the balance of the user
    #print('\n-----Invoking user microservice-----')
    #username = users.username
    #user_balance = invoke_http(user_URL + "user/balance/" + name , method='GET')
    #print('order_result:', user_balance)
    #user_update = invoke_http(user_URL + "user/purchase/" + name, methods='PUT')


if __name__ == '__main__':
    app.run(port=5007, debug=True)
     
