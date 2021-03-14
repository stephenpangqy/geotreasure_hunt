from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from invokes import invoke_http
import requests
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/box'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)


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
@app.route("/", methods=["POST"])
def create_box():
    # Format should be { username , latitude, longitude }
    plant_username = request.json.get('username')
    latitude = request.json.get('latitude')
    longitude = request.json.get('longitude')
    # randomly generate number of points and rewards (MAY NEED TO EDIT)
    no_of_points = random.randint(1,300)
    no_of_prize = random.randint(0,1)
    prize_list = ['$5 GrabVoucher','$10 GrabVoucher','20% OFF Popular Voucher','1-for-1 LiHo Tea Voucher','1-for-1 Gong Cha']
    box_prizes = []
    for i in range(0,no_of_prize):
        index = random.randint(0,len(prize_list)-1)
        box_prizes.append(prize_list[index])
    box_prizes_string = ','.join(box_prizes)
    box = Box(box_contents=box_prizes_string,no_of_points=no_of_points,box_latitude=latitude,box_longitude=longitude,planted_by_username=plant_username,is_opened = 'N')

    try:
        db.session.add(box)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating the order. " + str(e)
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
    latitude = query_params['latitude']
    longitude = query_params['longitude']
    box = Box.query.filter(Box.box_latitude.like(latitude[0:5] + "%"),Box.box_longitude.like(longitude[0:5] + "%")).first()
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



if __name__ == '__main__':
    app.run(debug=True)

    