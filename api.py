from flask import Flask, request, abort, Response
from flask_restful import Resource, Api
import requests
import logging

app = Flask(__name__)
api = Api(app)

# Setup basic logging
logging.basicConfig(level=logging.DEBUG)

class AllData(Resource):
    def get(self):
        try:
            response = requests.get('http://localhost:8080/get_data')
            if response.status_code != 200:
                abort(response.status_code, description="Could not fetch data from the server")
            return response.json(), 200
        except Exception as e:
            logging.error("Error fetching all data: %s", str(e))
            abort(500, description=str(e))

class Gateways(Resource):
    def get(self, gateway_name):
        try:
            response = requests.get(f'http://localhost:8080/get_data?gateway_name={gateway_name}')
            if response.status_code != 200:
                abort(response.status_code, description="Could not fetch data from the server")
            return response.json(), 200
        except Exception as e:
            logging.error("Error fetching gateway data: %s", str(e))
            abort(500, description=str(e))

class GatewayDevice(Resource):
    def get(self, gateway_name, device_name):
        try:
            response = requests.get(f'http://localhost:8080/get_data?gateway_name={gateway_name}')
            if response.status_code != 200:
                abort(response.status_code, description="Could not fetch data from the server")
            gateway_data = response.json()
            for device in gateway_data.get("devices", []):
                if device["name"] == device_name:
                    return device, 200
            abort(404, description="Device not found")
        except Exception as e:
            logging.error("Error fetching gateway device data: %s", str(e))
            abort(500, description=str(e))

class FanControl(Resource):
    def get(self):
        logging.debug("Rendering fan control page")
        html = """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Fan Control</title>
                <style>
                    .button {
                        display: inline-block;
                        padding: 10px 20px;
                        font-size: 20px;
                        cursor: pointer;
                        text-align: center;
                        text-decoration: none;
                        outline: none;
                        color: #fff;
                        background-color: #4CAF50;
                        border: none;
                        border-radius: 15px;
                        box-shadow: 0 9px #999;
                    }
                    .button:hover {background-color: #3e8e41}
                    .button:active {
                        background-color: #3e8e41;
                        box-shadow: 0 5px #666;
                        transform: translateY(4px);
                    }
                    .button-red {
                        background-color: #f44336;
                    }
                    .button-red:hover {background-color: #da190b}
                    .button-red:active {
                        background-color: #da190b;
                        box-shadow: 0 5px #666;
                        transform: translateY(4px);
                    }
                </style>
            </head>
            <body>
                <button class="button" onclick="turnOnFan()">Turn On Fan</button>
                <button class="button button-red" onclick="turnOffFan()">Turn Off Fan</button>
                <script>
                    function turnOnFan() {
                        fetch('/api/G2/Fan/control', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ action: 'turn_on' })
                        });
                    }
                    function turnOffFan() {
                        fetch('/api/G2/Fan/control', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ action: 'turn_off' })
                        });
                    }
                </script>
            </body>
        </html>
        """
        logging.debug("HTML content generated successfully")
        return Response(html, mimetype='text/html')

class FanControlAction(Resource):
    def post(self):
        data = request.get_json()
        action = data.get("action")
        logging.debug("Received action: %s", action)
        if action not in ['turn_on', 'turn_off']:
            logging.error("Invalid action: %s", action)
            abort(400, description="Invalid action")
        try:
            response = requests.post('http://localhost:8080/control_fan', json={'action': action})
            if response.status_code != 200:
                logging.error("Error performing action on fan: %s", response.text)
                abort(response.status_code, description="Could not perform action on the fan")
            return {'status': 'success', 'action': action}, 200
        except Exception as e:
            logging.error("Error performing action on fan: %s", str(e))
            abort(500, description=str(e))

api.add_resource(AllData, '/api/get_data')
api.add_resource(Gateways, '/api/<string:gateway_name>')
api.add_resource(GatewayDevice, '/api/<string:gateway_name>/<string:device_name>')
api.add_resource(FanControl, '/api/G2/Fan/control')
api.add_resource(FanControlAction, '/api/G2/Fan/control')

@app.route('/')
def home():
    return '<h1>REST API</h1>'

if __name__ == '__main__':
    app.run(port=8081, debug=True)
