from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/payment', methods=['POST']) # Creating the payment
# def payment():
#     return jsonify({
#         'paymentID' : 'PAYMENTID' # temp value
#     })

@app.route('/payment')
def pay_success():
    return render_template('success.html')

if __name__ == '__main__':
    app.run(debug=True)