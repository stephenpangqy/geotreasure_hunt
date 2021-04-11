from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3306/ingame_shop'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)
CORS(app)


class Shop(db.Model):
    __tablename__ = 'in_game_shop_items'

    itemname = db.Column(db.String(100),primary_key=True)
    itemprice = db.Column(db.String(100),nullable=False)
    itemdesc = db.Column(db.String(300),nullable=False)

    def json(self):
        return {
            'itemname': self.itemname,
            'itemprice': self.itemprice,
            'itemdesc': self.itemdesc
        }

@app.route("/getitems")
def get_sale_items():
    # No JSON is passed through in the body
    try:
        item_obj_list = Shop.query.all()
        #print(items)
        shop_items = []
        for obj in item_obj_list:
            item = {
                "itemname": obj.itemname,
                "price": obj.itemprice,
                "description": obj.itemdesc
            }
            shop_items.append(item)
        
        return jsonify({
            "code": 200,
            "shop_items": shop_items
        }),200
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": "An error occurred while retrieving shop items: " + str(e)
        }),500


@app.route("/order", methods=["POST"])
def create_order():
    # Format should be { data: [ {item,quantity}, {item,quantity}]}
    try:
        shop_items = Shop.query.all()
        data = request.get_json()
        #print(data)
        cart = data['data']
        new_cart = []
        for item_dict in cart:
            for item_obj in shop_items:
                if item_obj.itemname == item_dict['item']:
                    new_item = {
                        "itemname":item_dict['item'],
                        "price":item_obj.itemprice,
                        "quantity":item_dict["quantity"]
                    }
                    new_cart.append(new_item)
        return jsonify({
            "code": 201,
            "data": new_cart
        }),201
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": "An error occurred while creating order: " + str(e)
        }),500

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5005, debug=True)