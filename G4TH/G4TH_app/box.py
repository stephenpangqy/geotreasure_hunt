from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
import requests
import random
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3306/box'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)
CORS(app)


class Box(db.Model):
    __tablename__ = 'box'

    boxid = db.Column(db.Integer, primary_key=True)
    box_contents = db.Column(db.String(400))
    no_of_points = db.Column(db.Integer,nullable=False)
    box_latitude = db.Column(db.String(100),nullable=False)
    box_longitude = db.Column(db.String(100),nullable=False)
    planted_by_username = db.Column(db.String(300),nullable=False)
    is_opened = db.Column(db.String(1),nullable=False)

    def json(self):
        return {
            'boxid': self.boxid,
            'box_contents': self.box_contents,
            'no_of_points': self.no_of_points,
            'box_latitude': self.box_latitude,
            'box_longitude': self.box_longitude,
            'planted_by_username': self.planted_by_username,
            'is_opened': self.is_opened
        }

# Obtains a list of Boxes that are Unopened to display on the map
# http://(micro_name):(port no.)/(route)

@app.route("/getBoxes")
def getBoxes():
    try:
        boxes = Box.query.filter_by(is_opened='N')
        if not boxes:
            return jsonify({
                "code": 404,
                "message": "There are no boxes on the map at all!"
            }),404
        box_array = []
        for box in boxes:
            box_array.append(box.json())
        
        return jsonify({
            "code": 200,
            "boxes": box_array
        }), 200
    
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": "An error occurred while retrieving boxes: " + str(e)
        })
    
    


@app.route("/", methods=["POST"])
def create_box():
    # Format should be { username , latitude, longitude }
    plant_username = request.json.get('username')
    latitude = request.json.get('latitude')
    longitude = request.json.get('longitude')
    # randomly generate number of points and rewards (MAY NEED TO EDIT)
    no_of_points = random.randint(1,300)
    no_of_prize = random.randint(0,1)
    prize_list = ['$20 Gongcha Voucher','$5 Capitaland Voucher','$3 Li-Ho Voucher','$1 Popular Voucher','$10 GrabVoucher']
    box_prizes = []
    for i in range(0,no_of_prize):
        index = random.randint(0,len(prize_list)-1)
        box_prizes.append(prize_list[index])
    box_prizes_string = ','.join(box_prizes)
    if box_prizes_string == "":
        box_prizes_string = None
    box = Box(box_contents=box_prizes_string,no_of_points=no_of_points,box_latitude=latitude,box_longitude=longitude,planted_by_username=plant_username,is_opened = 'N')

    try:
        db.session.add(box)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating the box. " + str(e)
            }
        ),500
    
    return jsonify(
        {
            "code": 201,
            "message": "Your box has been deployed successfully"
        }
    ),201

@app.route("/search")
def find_box():
    query_params = request.args
    #print(query_params)
    latitude = str(query_params['latitude'])
    longitude = str(query_params['longitude'])
    # BOX SEARCH takes in the first 5 digits of latitude and longitude in order to check if the user is approximately near the box
    box = Box.query.filter(Box.box_latitude.like(latitude[0:5] + "%"),Box.box_longitude.like(longitude[0:5] + "%"),Box.is_opened.like("N")).first()
    try:
        if box != None:
            return jsonify(
                {
                    "code": 200,
                    "result": box.json()
                }
            ),200
        else:
            return jsonify(
                {
                    "code": 404,
                    "message": "There is no box nearby."
                }
            ),404
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while searching for a box: " + str(e)
            }
        ),500

# When opening box, change is_opened to 'Y'
@app.route('/open',methods=['PUT'])
def openBox():
    # JSON TO PASS THROUGH { boxid }
    try:
        boxid = request.json.get('boxid')
        box_details = Box.query.filter_by(boxid=boxid).first()
        box_details.is_opened = 'Y'
        db.session.commit()
        return jsonify({
            "code": 200,
            "message": "Box status updated to open successfully."
        }),200
    except Exception as e:
        return jsonify({
            "code":500,
            "message":"An error occurred while updating box status: " + str(e)
        }),500




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)

    