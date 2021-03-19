from flask import Flask, render_template, jsonify
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
# username = 'Michelle'

@app.route('/',methods=["POST"])
def updateMembership():
    # JSON RECEIVED { "code", username }
    print(request.get_json())
    code = request.json.get('code')
    username = request.json.get('username')
    if code == 200:
        current_date = datetime.today().strftime('%Y-%m-%d')
        json = {
            "username": username,
            "membership-date": current_date
        }
        print("--------Invoking User microservice to update membership---------")
        member_update = invoke_http('http://localhost:5004/user/membership/'+username,'PUT',json)
        if member_update['code'] == 200:
            return jsonify({
                "code":200,
                "message": member_update['message'],
                "data": member_update['data']
            }), 200
        else:
            return jsonify({
                "code": member_update['code'],
                "message": "An error occurred: " + member_update['message']
            }), member_update['code']


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5006,debug=True)