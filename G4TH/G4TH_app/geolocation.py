from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def getGeoLocation():
    try:
        # THIS IS MY API KEY, please replace key='...' with your own if possible.
        url = 'https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyA0J619B_oiVoB6E4OyX1EtJ-L2YaWj7ww'
        
        r = requests.post(url)
        return jsonify (
            {
                "code": r.status_code,
                "result": r.json()
                # Checking of status code will be done in the other microservice.
            }
        )
    except Exception as e:
        return jsonify (
            {
                "code": 500,
                "result": "An error occurred while obtaining user's geolocation: " + str(e)
            }
        )


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)