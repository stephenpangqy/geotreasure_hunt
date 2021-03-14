from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def getGeoLocation():
    try:
        url = 'https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyA0J619B_oiVoB6E4OyX1EtJ-L2YaWj7ww'
        
        r = requests.post(url)
        return jsonify (
            {
                "code": r.status_code,
                "result": r.json()
                # Checking of status code will be done in the other microservice.
            }
        ), 200
    except Exception as e:
        return jsonify (
            {
                "code": 500,
                "message": "An error occurred while obtaining user's geolocation: " + str(e)
            }
        ), 500


if __name__ == '__main__':
    app.run(debug=True)