from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from os import environ
import requests
from datetime import datetime
from flask_cors import CORS


app = Flask(__name__)

# SQL settings
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3306/user'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)
CORS(app)

class users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(300), unique=True)
    is_member = db.Column(db.String(1), nullable=False)
    membership_date = db.Column(db.Date)
    current_points = db.Column(db.Integer)
    total_points = db.Column(db.Integer)
    boxes_open = db.Column(db.Integer)
    last_login = db.Column(db.Date)
    daily_boxes = db.Column(db.Integer)

    def json(self):
        return {
        "username":self.username,
        "is_member":self.is_member,
        "membership_date":self.membership_date,
        "current_points":self.current_points,
        "total_points":self.total_points,
        "boxes_open":self.boxes_open,
        "last_login":self.last_login,
        "daily_boxes":self.daily_boxes
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
    
    def memjson(self):
        return {
            "username": self.username,
            "is_member": self.is_member
        }

    def boxjson(self):
        return {
            "username": self.username,
            "daily_boxes": self.daily_boxes
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
            "itemname":self.itemname,
            "quantity":self.quantity
        }

@app.route('/user/boxcount/<string:username>')
def boxCount(username):
    user = users.query.filter_by(username=username).first()
    if user:
        return jsonify({
            "code":200,
            "data": user.boxjson()
        }),200
    else:
        return jsonify({
            "code": 404,
            "message": "User is not found"
        }),404


@app.route('/user/useBox',methods=['PUT'])
def useBox():
    # JSON PASSED - {username}
    data = request.get_json()
    username = data['username']

    user = users.query.filter_by(username=username).first()

    if user:
        if user.daily_boxes == 0:
            return jsonify({
                "code":500,
                "message": "You have zero boxes."
            })
        else:
            user.daily_boxes -= 1
            db.session.commit()
            return jsonify({
                "code":200,
                "message": "Deduction of box is successful"
            })
    else:
        return jsonify({
            "code": 404,
            "message": 'User not found.'
        })


@app.route('/user/lastlogin',methods=['PUT'])
def updateLastLogin():
    # JSON PASSED - {username}
    data = request.get_json()
    username = data['username']
    
    user = users.query.filter_by(username=username).first()
    if user:
        login_date = datetime.today().strftime('%Y-%m-%d')
        is_member = False
        if user.is_member == "Y":
            is_member = True
        user_last_login = user.last_login
        if str(user_last_login) == str(login_date):
            return jsonify({
                "code": 200,
                "message": "User logged in today already."
            })
        else:
            user.last_login = login_date
            if is_member:
                user.daily_boxes = 5
            else:
                user.daily_boxes = 3
            db.session.commit()

            return jsonify({
                "code": 200,
                "message": "Welcome back, you have received " + str(user.daily_boxes) +" boxes. Happy planting!",
            })



    else:
        return jsonify({
            "code": 404,
            "message": 'User not found.'
        })




@app.route('/user/checkmember/<string:username>')
def check_member(username):
    user = users.query.filter_by(username=username).first()
    if user:
        return jsonify({
            "code": 200,
            "user": user.memjson()
        }),200
    else:
        return jsonify({
            "code": 404,
            "message": 'User not found.'
        })


@app.route("/user/<string:username>")
def get_user(username):
    user = users.query.filter_by(username=username).first()
    if user:
        return jsonify({
            "code": 200,
            "user": user.json()
        }),200
    else:
        return jsonify({
            "code":404,
            "user": "Not found."
        }),404

@app.route("/user/getInventory/<string:username>")
def get_inventory(username):
    inventory_list = []
    inventory_list = user_inventory.query.filter_by(username=username)
    if inventory_list == [] or inventory_list == None:
        return jsonify({
            "code":200,
            "inventory": "You have no items in your inventory."
        }), 200
    else:
        item_list = []
        for inventory in inventory_list:
            item_list.append(inventory.json())
        
        return jsonify({
            "code": 200,
            "inventory": item_list
        }), 200




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
            "message": "there are no records found"
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
    # JSON PASSED THROUGH { box_contents, box_latitude, box_longitude, boxid, is_opened, no_of_points, planted_by_username }
    #get record for user
    points = users.query.filter_by(username=username).first()

    #check if there is such user is in our user database
    if points:
        #check if user is a member
        is_member = False
        if points.is_member == "Y":
            is_member = True

        #get box stuff from content 
        data = request.get_json()
        itemname = data['box_contents']
        #get record of the user inventory
        content = ""
        if itemname != None:
            content = user_inventory.query.filter_by(username=username, itemname=itemname).first()
        #check if existing record of both primary keys username and itemid
        if content:
            #double check it sync with db again
            if itemname == content.itemname:
                #update quantity
                content.quantity += 1
        elif content != "" and itemname != None:
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
                        "message": "an error occurred updating user inventory: " + str(e)
                    }
                ), 500
        #update user point in user db
        #check if requested user is sync with db user
        #update points of the user
        if is_member:
            data['no_of_points'] *= 2
        points.total_points += data['no_of_points']
        points.current_points += data['no_of_points']
        #update user number of boxes open
        points.boxes_open += 1
        db.session.commit()

        #return success for both content and points updated
        return jsonify(
            {
                "code":200,
                "data":{
                    "item_won": itemname,
                    "points_earned": data['no_of_points']
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


@app.route("/user/purchase/<string:username>", methods=['PUT'])
def purchase(username):
    # DATA PASSED THROUGH { data: [ {itemname,price,quantity}, {itemname,price,quantity}, ...] }
    data = request.get_json()
    #get record for user
    user = users.query.filter_by(username=username).first()

    #check if there is such user is in our user database
    if user:
        # Check if user is a member
        is_member = False
        if user.is_member == "Y":
            is_member = True

        user_balance = user.current_points
        cart = data['data']
        if cart != []:
            subtotal = 0
            for item_dict in cart:
                if is_member:
                    item_dict['price'] *= 0.80
                subtotal += item_dict['price'] * int(item_dict['quantity'])
            #print(subtotal)
            #print(user_balance)
            # If user has enough points
            if user_balance >= subtotal:
                # Updating user's balance
                try:
                    user.current_points -= subtotal
                    db.session.commit()
                except Exception as e:
                    return jsonify({
                        "code": 500,
                        "message": "An error occurred when trying to update user balance: " + str(e)
                    }),500

                # Update user's inventory
                item_list = []
                for item_dict in cart:
                    item_list.append(item_dict['itemname'] + "(" + str(item_dict['quantity']) + ")")
                    content = user_inventory.query.filter_by(username=username,itemname=item_dict['itemname']).first()
                    if content == None:
                        createcontent = user_inventory(username, item_dict['itemname'], int(item_dict['quantity']))
                        try:
                            db.session.add(createcontent)
                            db.session.commit()
                            del createcontent
                        except Exception as e:
                            # return error when fail to insert
                            return jsonify(
                                {
                                    "code":500,
                                    "message": "an error occurred updating user inventory: " + str(e)
                                }
                            ), 500
                    else:
                        content.quantity += int(item_dict['quantity'])
                        try:
                            db.session.commit()
                        except Exception as e:
                            # return error when fail to insert
                            return jsonify(
                                {
                                    "code":500,
                                    "message": "an error occurred updating user inventory: " + str(e)
                                }
                            ), 500
                item_string = ",".join(item_list)
                return jsonify({
                    "code":200,
                    "message": "Purchase is successful. Your items have been added to your inventory.",
                    "currencyUsed": subtotal,
                    "items_received": item_string
                }),200


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
    app.run(host="0.0.0.0",port=5004, debug=True)
