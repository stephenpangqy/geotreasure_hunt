from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
import requests
from datetime import datetime

app = Flask(__name__)

# SQL settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/user'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class users(db.Model):
    __tablename__ = 'users'

    username = db.Column(db.String(300), primary_key=True)
    is_member = db.Column(db.String(1), nullable=False)
    membership_date = db.Column(db.Date)
    current_points = db.Column(db.Integer)
    total_points = db.Column(db.Integer)
    boxes_open = db.Column(db.Integer)

    def __init__(self, username, is_member, membership_date,current_points,total_points, boxes_open):
        self.username = username
        self.is_member = is_member
        self.membership_date = membership_date
        self.current_points = current_points
        self.total_points = total_points
        self.boxes_open = boxes_open

    def json(self):
        return {
        "username":self.username,
        "is_member":self.is_member,
        "membership_date":self.membership_date,
        "current_points":self.current_points,
        "total_points":self.total_points,
        "boxes_open":self.boxes_open
        }
    
    def lbpjson(self):
        return {
            "username":self.username,
            "total_points":self.total_points
        }
    
    def lbbjson(self):
        return {
            "username":self.username,
            "boxes_open":self.boxes_open
        }

    def cbjson(self):
        return{
            "username":self.username,
            "current_points":self.current_points
        }


class user_inventory(db.Model):
    __tablename__ = 'user_inventory'
    username = db.Column(db.String(300), primary_key=True)
    itemname = db.Column(db.String(100), primary_key=True)
    quantity = db.Column(db.Integer,nullable=False)

    def __init__(self,username,itemname,quantity):
        self.username=username
        self.itemname=itemname
        self.quantity=quantity

    def json(self):
        return{
            "username":self.username,
            "itemID":self.itemname,
            "quantity":self.quantity
        }


@app.route("/user/leaderboardRank")
def leaderboard():
    # get top 10 for both point and box open
    lbpoint = users.query.order_by(users.total_points.desc()).limit(10).all()
    lbbox = users.query.order_by(users.boxes_open.desc()).limit(10).all()

    # check in there is record in both of the lb
    if lbbox and lbpoint:
        # print(lbbox)
        # print(lbpoint)
        #return result
        lbpoint_array = []
        lbbox_array = []
        for user in lbpoint:
            lbpoint_array.append(user.lbpjson())
        for user2 in lbbox:
            lbbox_array.append(user2.lbbjson())

        return jsonify(
            {
                "code": 200,
                "top10_points": lbpoint_array,
                "top10_boxes": lbbox_array
            }
        )
    #return error for no record found
    return jsonify(
        {
            "code": 404,
            "message": "there are no records in found"
        }
    ), 404

@app.route("/user/balance/<string:username>")
def checkbalance(username):
    #get the user record
    checkb = users.query.filter_by(username=username).first()
    #check if user record is found
    if checkb:
        # if record found return the balance
        return jsonify(
            {
                "code": 200,
                "data": checkb.cbjson()
            }
        )
    #return error for no such user
    return jsonify(
        {
            "code": 404,
            "message": "There is no such user existing"
        }
    ), 404

@app.route("/user/membership/<string:username>", methods=['PUT'])
def updatemembership(username):
    # Data to be passed through should be {username, membership-date}
    #get the user record
    usermembership = users.query.filter_by(username=username).first()
    # check if the user is in our record
    if usermembership:
        data = {
            "username": request.json.get('username'),
            "membership-date": request.json.get('membership-date')
        }
        #double check if the requested username sync with our database username again
        if data['username'] == usermembership.username:
            #check if user is existing member or not
            if usermembership.is_member != "Y":
                #update the membership record
                usermembership.is_member = "Y"
                usermembership.membership_date = data['membership-date']
                db.session.commit()
                return jsonify(
                    {
                        "code": 200,
                        "data": usermembership.json(),
                        "message": "Membership has been successfully applied"
                    }
                ),200
            #return error for existing membership
            return jsonify(
                {
                    "code": 500,
                    "data": usermembership.json(),
                    "message": "user is a existing subscribed member"
                }
            ),500
        
        return jsonify(
            {
                "code": 403,
                "message": "Usernames do NOT match!"
            }
        ),403


    #return error for user not found
    return jsonify(
        {
            "code": 404,
            "data": {
                "username": username
            },
            "message": "username not found"
        }
    ), 404

@app.route("/user/openbox/<string:username>", methods=['PUT'])
def openbox(username):
    # DATA PASSED THROUGH {
    #   code,
    #   result: { box_contents, box_latitude, box_longitude, boxid, is_opened, no_of_points, planted_by_username}
    # }
    #get record for user
    points = users.query.filter_by(username=username).first()

    #get box stuff from content 
    data = request.get_json()
    itemname = data['result']['box_contents']
    #get record of the user inventory
    content = ""
    if itemname != "":
        content = user_inventory.query.filter_by(username=username, itemname=itemname).first()
    

    #check if there is such user is in our user database
    if points:
        #check if existing record of both primary keys username and itemid
        if content:
            #double check it sync with db again
            if itemname == content.itemname:
                #update quantity
                content.quantity += 1
        elif content != "" and itemname != "":
            #print("hello")
            #if no record found need to create one
            createcontent = user_inventory(username, itemname, 1)
            print(createcontent)
            try:
                db.session.add(createcontent)
                db.session.commit()
            except Exception as e:
                # return error when fail to insert
                return jsonify(
                    {
                        "code":500,
                        "message": "an error occurred updating user inventory" + str(e)
                    }
                ), 500
        #update user point in user db
        #check if requested user is sync with db user
        #update points of the user
        points.total_points += data['result']['no_of_points']
        points.current_points += data['result']['no_of_points']
        #update user number of boxes open
        points.boxes_open += 1
        db.session.commit()

        #return success for both content and points updated
        return jsonify(
            {
                "code":201,
                "data":{
                    "item_won": itemname,
                    "points_earned": data['result']['no_of_points']
                }
            }
        ),201
    #return error when username not found
    return jsonify(
        {
        "code": 404,
        "data": {
                "username": username
            },
        "message": "user not found"
        }
    ),404


@app.route("/user/purchase/<string:username>", methods=['PUT']) ## FUNCTION NEEDS TO BE FIXED!!!!
def purchase(username):
    # DATA PASSED THROUGH { [ {itemname,price,quantity}, {itemname,price,quantity}, ...] }
    data = request.get_json()
    #get record for user
    user = users.query.filter_by(username=username).first()

    #get record of the user inventory
    # content = ""
    # if itemname != "":
    #     content = user_inventory.query.filter_by(username=username, itemname=itemname).first()

    #check if there is such user is in our user database
    if user:
        user_balance = user.current_points
        cart = data['data']
        if cart != []:
            subtotal = 0
            for item_dict in cart:
                subtotal += item_dict['price'] * item_dict['quantity']
            #print(subtotal)
            #print(user_balance)
            # If user has enough points
            if user_balance >= subtotal:
                # Updating user's balance
                try:
                    user_balance -= subtotal
                    db.session.commit()
                except Exception as e:
                    return jsonify({
                        "code": 500,
                        "message": "An error occurred when trying to update user balance: " + str(e)
                    }),500

                # Update user's inventory
                for item_dict in cart:
                    content = user_inventory.query.filter_by(username=username,itemname=item_dict['itemname']).first()
                    if content != "":
                        createcontent = user_inventory(username, item_dict['itemname'], item_dict['quantity'])
                        try:
                            db.session.add(createcontent)
                            db.session.commit()
                        except Exception as e:
                            # return error when fail to insert
                            return jsonify(
                                {
                                    "code":500,
                                    "message": "an error occurred updating user inventory" + str(e)
                                }
                            ), 500
                    else:
                        content.quantity += item_dict['quantity']
                        try:
                            db.session.commit()
                        except Exception as e:
                            # return error when fail to insert
                            return jsonify(
                                {
                                    "code":500,
                                    "message": "an error occurred updating user inventory" + str(e)
                                }
                            ), 500
                    
                return jsonify({
                    "code":201,
                    "message": "Purchase is successful. Your items have been added to your inventory."
                }),201


            return jsonify({
                "code": 500,
                "message": "You do not have enough points to purchase everything in your cart!"
            })
        
        return jsonify({
            "code": 404,
            "message": "Your cart is empty, Please select at least 1 item before you checkout."
        }),404
    #return error when username not found
    return jsonify(
        {
        "code": 404,
        "data": {
                "username": username
        },
        "message": "user not found"
        }
    ),404

if __name__ == '__main__':
    app.run(port=5000, debug=True)
