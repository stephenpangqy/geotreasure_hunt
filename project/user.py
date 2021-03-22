from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from os import environ
import requests
from datetime import datetime
from flask_cors import CORS
import amqp_setup
import pika

from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)

# SQL settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/user'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#changes for user account
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db = SQLAlchemy(app)
CORS(app)

class users(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(300), unique=True)
    password = db.Column(db.String(80), nullable=False)
    is_member = db.Column(db.String(1), nullable=False)
    membership_date = db.Column(db.Date)
    current_points = db.Column(db.Integer)
    total_points = db.Column(db.Integer)
    boxes_open = db.Column(db.Integer)

    # def __init__(self, id, username, password, is_member, membership_date,current_points,total_points, boxes_open):
    #     self.id = id
    #     self.username = username
    #     self.password = password
    #     self.is_member = is_member
    #     self.membership_date = membership_date
    #     self.current_points = current_points
    #     self.total_points = total_points
    #     self.boxes_open = boxes_open

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

@app.route("/user/<string:username>")
def get_user(username):
    user = users.query.filter_by(username=username).first()
    if user:
        return jsonify({
            "code": 200,
            "user": user.json()
        }),200
    else:
        usernotfoundmessage = 'user not found'
        # amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="user.activity", 
        # body=usernotfoundmessage, properties=pika.BasicProperties(delivery_mode = 2))
        return jsonify({
            "code":404,
            "user": "Not found."
        }),404



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
                # amqp on subscription
                # membershipok = 'Member has been successfully applied for user {usermembership}'
                # amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="user.activity", 
                # body=membershipok, properties=pika.BasicProperties(delivery_mode = 2)) 
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
            else:
                membershipexist = 'User {usermembership} already subscribed'
                amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="user.error", 
                body=membershipexist, properties=pika.BasicProperties(delivery_mode = 2))
                return jsonify(
                    {
                        "code": 500,
                        "data": usermembership.json(),
                        "message": "user is a existing subscribed member"
                    }
                ),500
        
        else:
            nouser = 'when trying to subscribe, Usernames do NOT match'
            amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="user.error", 
                body=nouser, properties=pika.BasicProperties(delivery_mode = 2))
            return jsonify(
                {
                    "code": 403,
                    "message": "Usernames do NOT match!"
                }
            ),403

    else:
        #return error for user not found
        usernotfound = 'username not found'
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="user.error", 
                body=usernotfound, properties=pika.BasicProperties(delivery_mode = 2))
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
    # DATA PASSED THROUGH { box_contents, box_latitude, box_longitude, boxid, is_opened, no_of_points, planted_by_username }
    #get record for user
    points = users.query.filter_by(username=username).first()

    #get box stuff from content 
    data = request.get_json()
    itemname = data['box_contents']
    #get record of the user inventory
    content = ""
    if itemname != None:
        content = user_inventory.query.filter_by(username=username, itemname=itemname).first()
    

    #check if there is such user is in our user database
    if points:
        #check if existing record of both primary keys username and itemid
        if content:
            #double check it sync with db again
            if itemname == content.itemname:
                #update quantity
                updatequantity = 'user {points} content updated'
                amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="user.activity", 
                body=updatequantity, properties=pika.BasicProperties(delivery_mode = 2))
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
                failtoinsert = 'An error occurred when updating {points} inventory' + str(e)
                amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="user.error", 
                body=failtoinsert, properties=pika.BasicProperties(delivery_mode = 2)) 
                return jsonify(
                    {
                        "code":500,
                        "message": "an error occurred updating user inventory" + str(e)
                    }
                ), 500

        else:
            #update user point in user db
            #check if requested user is sync with db user
            #update points of the user
            points.total_points += data['no_of_points']
            points.current_points += data['no_of_points']
            #update user number of boxes open
            points.boxes_open += 1
            db.session.commit()

            #return success for both content and points updated
            # updatecontentandpoints = 'Successful update of new content and points for {points}'
            # amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="user.activity", 
            # body=updatecontentandpoints, properties=pika.BasicProperties(delivery_mode = 2)) 
            return jsonify(
                {
                    "code":201,
                    "data":{
                        "item_won": itemname,
                        "points_earned": data['no_of_points']
                    }
                }
            ),201

    else:
        #return error when username not found
        usernotfound = 'User not found when opening box and updating contents or points'
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="user.error", 
            body=usernotfound, properties=pika.BasicProperties(delivery_mode = 2)) 
        return jsonify(
            {
            "code": 404,
            "data": {
                    "username": username
                },
            "message": "user not found"
            }
        ),404

# for purchase incentives, not membership
@app.route("/user/purchase/<string:username>", methods=['PUT'])
def purchase(username):
    # DATA PASSED THROUGH { data: [ {itemname,price,quantity}, {itemname,price,quantity}, ...] }
    data = request.get_json()
    #get record for user
    user = users.query.filter_by(username=username).first()

    #check if there is such user is in our user database
    if user:
        user_balance = user.current_points
        cart = data['data']
        if cart != []:
            subtotal = 0
            for item_dict in cart:
                subtotal += item_dict['price'] * int(item_dict['quantity'])
            #print(subtotal)
            #print(user_balance)
            # If user has enough points
            if user_balance >= subtotal:
                # Updating user's balance
                try:
                    balanceupdated = 'User {user} balance is updated.'
                    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="user.activity", 
                    body=balanceupdated, properties=pika.BasicProperties(delivery_mode = 2)) 
                    user.current_points -= subtotal
                    db.session.commit()
                except Exception as e:
                    balancenotupdated = 'An error occurred when trying to update user balance' + str(e)
                    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="user.error", 
                    body=balancenotupdated, properties=pika.BasicProperties(delivery_mode = 2)) 
                    return jsonify({
                        "code": 500,
                        "message": "An error occurred when trying to update user balance: " + str(e)
                    }),500

                # Update user's inventory
                for item_dict in cart:
                    content = user_inventory.query.filter_by(username=username,itemname=item_dict['itemname']).first()
                    if content == None:
                        createcontent = user_inventory(username, item_dict['itemname'], int(item_dict['quantity']))
                        try:
                            contentcreated = 'content {createcontent} created for user {user}'
                            amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="user.activity", 
                            body=contentcreated, properties=pika.BasicProperties(delivery_mode = 2)) 
                            db.session.add(createcontent)
                            db.session.commit()
                            del createcontent
                        except Exception as e:
                            contentupdateerror = 'An error occurred when updating user inventory of new content'
                            amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="user.error", 
                            body=contentupdateerror, properties=pika.BasicProperties(delivery_mode = 2)) 
                            # return error when fail to insert
                            return jsonify(
                                {
                                    "code":500,
                                    "message": "an error occurred updating user inventory" + str(e)
                                }
                            ), 500
                    else:
                        content.quantity += int(item_dict['quantity'])
                        try:
                            contentquantityupdate = 'Content quantity for user {user} updated'
                            amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="user.activity", 
                            body=contentquantityupdate, properties=pika.BasicProperties(delivery_mode = 2)) 
                            db.session.commit()
                        except Exception as e:
                            contentquantityupdateerror = 'An error occurred when updating user inventory of content quantity'
                            amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="user.error", 
                            body=contentquantityupdateerror, properties=pika.BasicProperties(delivery_mode = 2)) 
                            # return error when fail to insert
                            return jsonify(
                                {
                                    "code":500,
                                    "message": "an error occurred updating user inventory" + str(e)
                                }
                            ), 500
                purchasesuccess = 'Purchase for user {user} is successful. Items added to inventory.'
                amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="user.activity", 
                body=purchasesuccess, properties=pika.BasicProperties(delivery_mode = 2)) 
                return jsonify({
                    "code":201,
                    "message": "Purchase is successful. Your items have been added to your inventory."
                }),201

            # i dont think this part should have as before this purchase step
            # is the order creation and before that is checking whether got sufficient currency 
            # which should be implemented in another function (which have already, check_balance() )
            else:
                insufficientpoints = 'User {user} do not have enough points to purchase everything in the cart'
                amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="user.error", 
                body=insufficientpoints, properties=pika.BasicProperties(delivery_mode = 2)) 
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


# LOGIN ROUTES #
# @login_manager.user_loader
# def load_user(user_id):
#     return users.query.get(int(user_id))

# class LoginForm(FlaskForm):
#     username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
#     password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

# class RegisterForm(FlaskForm):
#     username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
#     password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

# @app.route('/', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()

#     if form.validate_on_submit():
#         user = users.query.filter_by(username=form.username.data).first()
#         if user:
#             if check_password_hash(user.password, form.password.data):
#                 login_user(user)
#                 return redirect(url_for('dashboard'))

#         return '<h1>Invalid username or password</h1> <br> <br> <a href="/"><< Go back</a>'
#         #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

#     return render_template('login.html', form=form)

# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     form = RegisterForm()

#     if form.validate_on_submit():
#         # Check if username already exists
#         exist_user = users.query.filter_by(username=form.username.data).first()
#         if exist_user:
#             return "<h1>Username already exists, please select a new one. <br> <br> <a href='/signup'> << Go back </a>"
#         hashed_password = generate_password_hash(form.password.data, method='sha256')
#         new_user = users(username=form.username.data, password=hashed_password, is_member='N', membership_date=None,current_points=0,total_points=0, boxes_open=0)
#         db.session.add(new_user)
#         db.session.commit()

#         login_user(new_user)
#         return redirect(url_for('dashboard'))
#         #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

#     return render_template('signup.html', form=form)

# @app.route('/dashboard')
# @login_required
# def dashboard():
#     return render_template('dashboard.html', name=current_user.username)

# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5004, debug=True)
