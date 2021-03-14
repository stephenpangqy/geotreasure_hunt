from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from invokes import invoke_http
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/box'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

class Shop(db.model):
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

@app.route("/order", methods=["POST"])
def create_order():
     # Format should be {[item,quantity],[item,quantity], ...}