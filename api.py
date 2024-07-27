from flask import Flask, request, abort, Response
from flask_restful import Resource, Api
import requests
import logging
import json

app = Flask(__name__)
api = Api(app)

# Setup basic logging
logging.basicConfig(level=logging.DEBUG)

# Replace with the actual IP address of the server device (Device A)
SERVER_IP = "192.168.1.100"  # Updated to the IP address of Device A
SERVER_PORT = 8080  # Ensure this matches the port used by server.py

class AllData(Resource):
    def get(self):
        try:
            response = requests.get(f'http://{SERVER_IP}:{SERVER_PORT}/get_data')
            if response.status_code != 200:
                abort(response.status_code, description="Could not fetch data from the server")
            return response.json(), 200
        except Exception as e:
            logging.error("Error fetching all data: %s", str(e))
            abort(500, description=str(e))

class Gateways(Resource):
    def get(self, gateway_name):
        try:
            response = requests.get(f'http://{SERVER_IP}:{SERVER_PORT}/get_data?gateway_name={gateway_name}')
            if response.status_code != 200:
                abort(response.status_code, description="Could not fetch data from the server")
            return response.json(), 200
        except Exception as e:
            logging.error("Error fetching gateway data: %s", str(e))
            abort(500, description=str(e))

class GatewayDevice(Resource):
    def get(self, gateway_name, device_name):
        try:
            response = requests.get(f'http://{SERVER_IP}:{SERVER_PORT}/get_data?gateway_name={gateway_name}')
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
            response = requests.post(f'http://{SERVER_IP}:{SERVER_PORT}/control_fan', json={'action': action})
            if response.status_code != 200:
                logging.error("Error performing action on fan: %s", response.text)
                abort(response.status_code, description="Could not perform action on the fan")
            return {'status': 'success', 'action': action}, 200
        except Exception as e:
            logging.error("Error performing action on fan: %s", str(e))
            abort(500, description=str(e))

class StartSendData(Resource):
    def get(self):
        try:
            response = requests.get(f'http://{SERVER_IP}:{SERVER_PORT}/start_send')
            if response.status_code != 200:
                abort(response.status_code, description="Could not start sending data")
            return response.json(), 200
        except Exception as e:
            logging.error("Error starting data send: %s", str(e))
            abort(500, description=str(e))

class StopSendData(Resource):
    def get(self):
        try:
            response = requests.get(f'http://{SERVER_IP}:{SERVER_PORT}/stop_send')
            if response.status_code != 200:
                abort(response.status_code, description="Could not stop sending data")
            return response.json(), 200
        except Exception as e:
            logging.error("Error stopping data send: %s", str(e))
            abort(500, description=str(e))

class DataControlPage(Resource):
    def get(self):
        logging.debug("Rendering data control page")
        html = """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Data Control</title>
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
                <button class="button" onclick="startSending()">Start Sending Data</button>
                <button class="button button-red" onclick="stopSending()">Stop Sending Data</button>
                <script>
                    function startSending() {
                        fetch('/api/start_send', {
                            method: 'GET'
                        });
                    }
                    function stopSending() {
                        fetch('/api/stop_send', {
                            method: 'GET'
                        });
                    }
                </script>
            </body>
        </html>
        """
        logging.debug("HTML content generated successfully")
        return Response(html, mimetype='text/html')

class DisplayDataPage(Resource):
    def get(self):
        try:
            response = requests.get(f'http://{SERVER_IP}:{SERVER_PORT}/get_data')
            if response.status_code != 200:
                abort(response.status_code, description="Could not fetch data from the server")
            
            data = response.json()
            html = "<!DOCTYPE html><html><head><title>Data Display</title></head><body>"
            html += f"<h1>Gateway Data</h1><pre>{json.dumps(data, indent=4)}</pre>"
            html += "</body></html>"
            
            return Response(html, mimetype='text/html')
        except Exception as e:
            logging.error("Error reading data: %s", str(e))
            return Response("<h1>Error reading data</h1>", mimetype='text/html')

api.add_resource(AllData, '/api/get_data')
api.add_resource(Gateways, '/api/<string:gateway_name>')
api.add_resource(GatewayDevice, '/api/<string:gateway_name>/<string:device_name>')
api.add_resource(FanControl, '/api/G2/Fan/control')
api.add_resource(FanControlAction, '/api/G2/Fan/control')
api.add_resource(StartSendData, '/api/start_send')
api.add_resource(StopSendData, '/api/stop_send')
api.add_resource(DataControlPage, '/api/data_control')
api.add_resource(DisplayDataPage, '/api/display_data')

@app.route('/')
def home():
    return '<h1>REST API</h1>'

if __name__ == '__main__':
    app.run(port=8081, debug=True)
