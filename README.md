# IOT
IOT Project / mapna2

# 1. REST API

## Setup Database
Type this command in your terminal :
```
$ py create_db.py
```

## Explain api code
### Models
First we create User Model & Device Model & Sensor Model & Actuator Model that shows the features of each fields and then we add argument for each one :
#### a. User
```
class UserModel(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    userrequest = db.Column(db.String(80), nullable=False)

    def __repr__(self): 
        return f"User(username = {self.username}, password = {self.password}, userrequest = {self.userrequest})"

user_args = reqparse.RequestParser()
user_args.add_argument('username', type=str, required=True, help="Username cannot be blank")
user_args.add_argument('password', type=str, required=True, help="Password cannot be blank")
user_args.add_argument('userrequest', type=str, required=True, help="Userrequest cannot be blank")
```
#### b. Device and Sensor
```
class DeviceModel(db.Model):
    __tablename__ = 'devices'
    type = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    value = db.Column(db.Integer, nullable=False)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id'), nullable=False)
    sensor = db.relationship('SensorModel', backref=db.backref('devices', lazy=True))

    def __repr__(self):
        return f"Device(type={self.type}, name={self.name}, value={self.value})"

class SensorModel(db.Model): 
    __tablename__ = 'sensors'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(80), unique=True, nullable=False)
    devices = db.relationship('DeviceModel', backref='sensor', lazy=True)

    def __repr__(self): 
        return f"Sensor(id = {self.id}, token = {self.token}, devices={self.devices})"

sensor_args = reqparse.RequestParser()
sensor_args.add_argument('token', type=str, required=True, help="Token od sensor cannot be blank")

device_args = reqparse.RequestParser()
device_args.add_argument('type', type=str, required=True, help="Type of device cannot be blank")
device_args.add_argument('name', type=str, required=True, help="Name cannot be blank")
device_args.add_argument('value', type=int, required=True, help="Value cannot be blank")
```
#### c. Actuator
```
class ActuatorModel(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(80), unique=True, nullable=False)
    type = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(80), nullable=False)

    def __repr__(self): 
        return f"User(token = {self.token}, type = {self.type}, location = {self.location}, status = {self.status})"

actuator_args = reqparse.RequestParser()
actuator_args.add_argument('token', type=str, required=True, help="Token of Actuatr cannot be blank")
actuator_args.add_argument('type', type=str, required=True, help="Type of Actuator cannot be blank")
actuator_args.add_argument('location', type=str, required=True, help="Location cannot be blank")
actuator_args.add_argument('status', type=str, required=True, help="Status cannot be blank")
```

**_NOTE:_**  Important part is that devices are in side of sensor, for example or JSON look like this :
```
{
        'ID' : 'S-0235694',
        'Token' : 'T-197354'
        'Devices' : [
            {
                'type' : 'sensor',
                'name' : 'temp0',
                'value' : 18.5
            },
            {
                'type' : 'act',
                'name' : 'lamp0',
                'value' : 1
            },
            {
                'type' : 'act',
                'name' : 'lamp1',
                'value' : 0
            }
        ]
}
```

### Fields
Then we create fields and show what type they accept :
#### a. User
```
userFields = {
    'id':fields.Integer,
    'username':fields.String,
    'password':fields.String,
    'userrequest':fields.String,
}
```
#### b. Device and Sensor
```
class DeviceSchema(ModelSchema):
    class Meta:
        model = DeviceModel
        sqla_session = db.session

deviceFields = {
    'type': fields.String,
    'name': fields.String,
    'value': fields.Integer,
    'sensor_id': fields.Integer,
}

sensorFields = {
    'id': fields.Integer,
    'token': fields.String,
    'devices': fields.Nested(DeviceSchema, many=True),
}
```
#### c. Actuator
```
actuatorFields = {
    'id': fields.Integer,
    'token': fields.String,
    'type': fields.String,
    'location': fields.String,
    'status': fields.String,
}
```
### Add get, post, patch and delete for Users :
In ```class Users(Resource)``` we create ```def get(self)``` to show all the users with the fields that we described and then in ```def post(self)``` we can add new user :
```
class Users(Resource):
    @marshal_with(userFields)
    def get(self):
        users = UserModel.query.all() 
        return users 

    @marshal_with(userFields)
    def post(self):
        args = user_args.parse_args()
        user = UserModel(username=args["username"], password=args["password"], userrequest=args["userrequest"])
        db.session.add(user) 
        db.session.commit()
        users = UserModel.query.all()
        return users, 201
```
For the second class ```class User(Resource)``` we create ```def get(self, id)``` for get user form there id (like search with id) , in ```def patch(self, id)``` we can update a user by there id , at the end we create ```def delete(self, id)``` that we can delete user by there id :
```
class Users(Resource):
    @marshal_with(userFields)
    def get(self):
        users = UserModel.query.all() 
        return users

    @marshal_with(userFields)
    def post(self):
        args = user_args.parse_args()
        user = UserModel(username=args["username"], password=args["password"], userrequest=args["userrequest"])
        db.session.add(user) 
        db.session.commit()
        users = UserModel.query.all()
        return users, 201

class User(Resource):
    @marshal_with(userFields)
    def get(self, id):
        user = UserModel.query.filter_by(id=id).first() 
        if not user: 
            abort(404, message="User not found")
        return user 
    
    @marshal_with(userFields)
    def patch(self, id):
        args = user_args.parse_args()
        user = UserModel.query.filter_by(id=id).first() 
        if not user: 
            abort(404, message="User not found")
        user.username = args["username"]
        user.password = args["password"]
        user.userrequest = args["userrequest"]
        db.session.commit()
        return user 
    
    @marshal_with(userFields)
    def delete(self, id):
        user = UserModel.query.filter_by(id=id).first() 
        if not user: 
            abort(404, message="User not found")
        db.session.delete(user)
        db.session.commit()
        users = UserModel.query.all()
        return users
```
**_NOTE:_**  We do the same function for devices, device, sensors, sensor, actuators and actuator .


# Server

The `server.py` script implements a WebSocket server that authenticates clients using a token, receives data from connected clients, and saves the data to JSON files. Additionally, it provides HTTP endpoints for controlling data transmission from clients.

## Features

- **WebSocket Server**: Listens for incoming WebSocket connections from clients.
- **Authentication**: Uses a simple token-based authentication mechanism.
- **Data Handling**: Receives data from clients and saves it to JSON files based on the data type (e.g., sensors, actuators).
- **HTTP Control**: Provides HTTP endpoints to start/stop data transmission from clients and a simple control page.

## Requirements

- Python 3.7+
- aiohttp
- websockets

## Installation

1. Install the required Python packages:
   ```sh
   pip install aiohttp websockets
   ```

2. Run the server:
   ```sh
   python server.py
   ```

## Endpoints

- **WebSocket**: `ws://<server_ip>:8766`
- **HTTP**:
  - `GET /`: Returns a simple greeting.
  - `GET /start_send`: Enables data sending for all connected clients.
  - `GET /stop_send`: Disables data sending for all connected clients.
  - `GET /control`: Serves a simple control page for starting/stopping data sending.

## Configuration

- **AUTH_TOKEN**: Set your authentication token in the `AUTH_TOKEN` variable in the `server.py` script.

## Code Explanation

### Import Libraries and Configure Logging

```python
import asyncio
import json
import os
import logging
import traceback
from aiohttp import web
import websockets
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
```

- **Import Libraries**: Import necessary libraries for asynchronous operations, JSON handling, file operations, logging, and WebSocket/HTTP functionality.
- **Configure Logging**: Set up logging configuration to output debug-level logs with timestamps and log levels.

### Global Variables and Authentication Function

```python
# A dictionary to store connected clients (gateways) and their addresses
connected_clients = {}
data_sending_enabled = {}

# Simple token-based authentication
AUTH_TOKEN = "your_secret_token"

async def authenticate(websocket, path):
    """
    Handle authentication of the client using a simple token.
    """
    try:
        auth_message = await websocket.recv()  # Receive authentication message
        logging.debug(f"Received authentication message: {auth_message} from {websocket.remote_address}")
        if auth_message == AUTH_TOKEN:
            await websocket.send("Authentication Successful")  # Send success message
            logging.debug(f"Authentication successful for {websocket.remote_address}")
            return True
        else:
            await websocket.send("Authentication Failed")  # Send failure message
            logging.warning(f"Authentication failed for {websocket.remote_address}")
            await websocket.close()  # Close connection if authentication fails
            return False
    except Exception as e:
        logging.error(f"Authentication error: {e} for {websocket.remote_address}")
        logging.error(traceback.format_exc())
        return False
```

- **Global Variables**: Define dictionaries to store connected clients and their data sending status.
- **AUTH_TOKEN**: Define a simple authentication token.
- **authenticate Function**: Handles client authentication using the provided token.

### Save Data Function

```python
async def save_data(data_type, data):
    """
    Save the received data to a JSON file in the appropriate directory.
    """
    try:
        logging.debug(f"Saving data: {data} to {data_type}")
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')
        folder_path = f"data/{data_type}"
        os.makedirs(folder_path, exist_ok=True)  # Create directory if it doesn't exist
        file_path = os.path.join(folder_path, f"{timestamp}.json")
        with open(file_path, 'w') as f:
            json.dump(data, f)  # Save data as JSON
        logging.info(f"Data saved to {file_path}")
    except Exception as e:
        logging.error(f"Error saving data: {e}")
        logging.error(traceback.format_exc())
```

- **save_data Function**: Saves the received data to a JSON file in the specified directory.

### WebSocket Handler

```python
async def handler(websocket, path):
    """
    Main handler for WebSocket connections.
    """
    global data_sending_enabled
    logging.info(f"New connection from {websocket.remote_address}")
    if not await authenticate(websocket, path):
        return

    # Register the client
    client_id = websocket.remote_address
    connected_clients[client_id] = websocket
    data_sending_enabled[client_id] = False  # Default to not sending data
    logging.info(f"Client connected: {client_id}")

    try:
        async for message in websocket:
            logging.info(f"Received message from {client_id}: {message}")
            data = json.loads(message)
            if data_sending_enabled[client_id]:
                if data.get("id") == 34:  # Example check for sensor ID
                    await save_data("sensors", data)
                elif data.get("id") == 12:  # Example check for actuator ID
                    await save_data("actuators", data)
                else:
                    logging.warning(f"Unknown data type: {data}")
            response = f"Processed: {message}"
            await websocket.send(response)  # Send response back to the client
            logging.info(f"Sent response to {client_id}: {response}")
    except websockets.exceptions.ConnectionClosed as e:
        logging.warning(f"Client disconnected: {client_id}")
        logging.warning(traceback.format_exc())
    finally:
        # Unregister the client
        del connected_clients[client_id]
        del data_sending_enabled[client_id]
        logging.info(f"Client {client_id} unregistered")
```

- **handler Function**: Main handler for WebSocket connections, including authentication, data processing, and client registration/unregistration.

### HTTP Handlers

```python
async def hello(request):
    """
    Simple HTTP handler that returns a greeting.
    """
    return web.Response(text="Hello, world")

async def start_send(request):
    """
    HTTP handler to enable data sending for all connected clients.
    """
    global data_sending_enabled
    for client_id, websocket in connected_clients.items():
        data_sending_enabled[client_id] = True
        await websocket.send("Start Sending Data")
    return web.Response(text="Data sending enabled")

async def stop_send(request):
    """
    HTTP handler to disable data sending for all connected clients.
    """
    global data_sending_enabled
    for client_id, websocket in connected_clients.items():
        data_sending_enabled[client_id] = False
        await websocket.send("Stop Sending Data")
    return web.Response(text="Data sending disabled")

async def control_page(request):
    """
    HTTP handler to serve a simple control page for starting/stopping data sending.
    """
    html = """
    <html>
        <head>
            <title>Control Page</title>
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
            <button class="button" onclick="startSend()">Start Sending Data</button>
            <button class="button button-red" onclick="stopSend()">Stop Sending Data</button>
            <script>
                function startSend() {
                    fetch('/start_send');
                }
                function stopSend() {
                    fetch('/stop_send');
                }
            </script>
        </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')
```

- **hello Function**: Returns a simple greeting message.
- **start_send Function**: Enables data sending for all connected clients.
- **stop_send Function**: Disables data sending for all connected clients.
- **control_page Function**: Serves an HTML control page with buttons to start/stop data sending.

### Main Function

```python
async def main():
    """
    Main function to start the WebSocket and HTTP servers.
    """
    try:
        server = await websockets.serve(handler, "

0.0.0.0", 8766)
        logging.info("WebSocket server started")

        app = web.Application()
        app.router.add_get('/', hello)
        app.router.add_get('/start_send', start_send)
        app.router.add_get('/stop_send', stop_send)
        app.router.add_get('/control', control_page)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        await site.start()
        logging.info("HTTP server started on port 8080")

        await asyncio.Future()  # Run forever
    except Exception as e:
        logging.error("Unexpected error:")
        logging.error(traceback.format_exc())
    finally:
        if 'server' in locals():
            server.close()
            await server.wait_closed()
            logging.info("WebSocket server stopped")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server manually interrupted")
    except Exception as e:
        logging.error("Unexpected error in __main__:")
        logging.error(traceback.format_exc())
```

- **main Function**: Starts the WebSocket and HTTP servers.
- **__main__ Block**: Runs the main function and handles keyboard interruption.

# Gateway

The `gateway.ino` script is an Arduino program that connects to a WiFi network, establishes a WebSocket connection with the server, and sends sensor and actuator data. It also listens for control messages from the server to start/stop data transmission.

## Features

- **WiFi Connection**: Connects to a specified WiFi network.
- **WebSocket Client**: Connects to the WebSocket server and sends authentication token.
- **Data Sending**: Sends sensor and actuator data to the server.
- **Control Commands**: Responds to start/stop data transmission commands from the server.

## Requirements

- Arduino board (e.g., ESP32)
- Arduino IDE
- ArduinoWebsockets library
- ArduinoJson library

## Installation

1. Open the `gateway.ino` file in Arduino IDE.
2. Set the WiFi credentials and WebSocket server address in the code.
3. Upload the code to the Arduino board.

## Code Explanation

### Include Libraries and Define Constants

```cpp
#include <WiFi.h>
#include <ArduinoWebsockets.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "Your_SSID";
const char* password = "Your_PASSWORD";

// WebSocket server address and authentication token
const char* websocket_server = "ws://<server_ip>:8766";  // Correct IP address
const char* auth_token = "your_secret_token"; // The same token used in the server

using namespace websockets;

WebsocketsClient client;
bool sendData = false;  // Flag to control data sending
```

- **Include Libraries**: Import necessary libraries for WiFi, WebSocket, and JSON functionality.
- **Define Constants**: Set WiFi credentials, WebSocket server address, and authentication token.

### Setup WiFi Connection

```cpp
void setup_wifi() {
    // Initialize serial communication
    Serial.begin(115200);
    delay(10);
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);

    // Connect to WiFi
    WiFi.begin(ssid, password);

    // Wait for the connection to establish
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println();
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
}
```

- **setup_wifi Function**: Connects to the specified WiFi network and prints the IP address.

### WebSocket Callbacks

```cpp
// Callback for handling received messages
void onMessageCallback(WebsocketsMessage message) {
    Serial.print("Received: ");
    Serial.println(message.data());
    if (message.data() == "Start Sending Data") {
        sendData = true;
    } else if (message.data() == "Stop Sending Data") {
        sendData = false;
    }
}

// Callback for handling WebSocket events
void onEventsCallback(WebsocketsEvent event, String data) {
    if (event == WebsocketsEvent::ConnectionOpened) {
        Serial.println("WebSocket connection opened");
    } else if (event == WebsocketsEvent::ConnectionClosed) {
        Serial.println("WebSocket connection closed");
    } else if (event == WebsocketsEvent::GotPing) {
        Serial.println("Got a Ping!");
    } else if (event == WebsocketsEvent::GotPong) {
        Serial.println("Got a Pong!");
    } else {
        Serial.print("Event: ");
        Serial.println(data);
    }
}
```

- **onMessageCallback**: Handles messages received from the server and updates the `sendData` flag based on the command.
- **onEventsCallback**: Handles WebSocket events such as connection opened, connection closed, and ping/pong messages.

### Connect to WebSocket Server

```cpp
// Connect to the WebSocket server
void connectWebSocket() {
    Serial.println("Connecting to WebSocket server...");
    bool result = client.connect(websocket_server);
    if (result) {
        Serial.println("WebSocket connected");
        client.send(auth_token); // Send the authentication token
    } else {
        Serial.println("WebSocket connection failed");
    }
}
```

- **connectWebSocket Function**: Connects to the WebSocket server and sends the authentication token.

### Setup Function

```cpp
void setup() {
    Serial.begin(115200);
    setup_wifi();

    // Set callbacks for WebSocket events
    client.onMessage(onMessageCallback);
    client.onEvent(onEventsCallback);

    // Connect to WebSocket server
    connectWebSocket();
}
```

- **setup Function**: Initializes the serial communication, sets up the WiFi connection, assigns WebSocket callbacks, and connects to the WebSocket server.

### Sensor and Actuator Data Functions

```cpp
// Read sensor data (example: analog pin)
float readSensorData(int pin) {
    int sensorValue = analogRead(pin);  // Example sensor data
    float voltage = sensorValue * (3.3 / 4095.0); // Convert ADC reading to voltage
    Serial.print("Sensor Value: ");
    Serial.print(sensorValue);
    Serial.print(" Voltage: ");
    Serial.println(voltage);
    return voltage;
}

// Read actuator data (example: digital pin)
bool readActuatorData(int pin) {
    bool state = digitalRead(pin);  // Example actuator data
    Serial.print("Actuator State: ");
    Serial.println(state);
    return state;
}
```

- **readSensorData Function**: Reads data from an analog sensor and converts it to voltage.
- **readActuatorData Function**: Reads data from a digital actuator.

### Main Loop

```cpp
void loop() {
    if (client.available()) {
        client.poll();  // Poll for incoming messages
    } else {
        Serial.println("Client not available, reconnecting...");
        connectWebSocket();  // Reconnect if the client is not available
    }

    if (sendData) {
        // Read sensor and actuator data
        float sensor_voltage = readSensorData(34);  // Example sensor data
        bool actuator_state = readActuatorData(12);  // Example actuator data

        // Create JSON object for sensor data
        StaticJsonDocument<200> sensorDoc;
        sensorDoc["id"] = 34;
        sensorDoc["token"] = auth_token;
        sensorDoc["data"] = sensor_voltage;

        // Serialize JSON to string for sensor data
        String sensorJson;
        serializeJson(sensorDoc, sensorJson);

        // Send JSON data for sensor
        bool send_result = client.send(sensorJson);
        Serial.print("Send result (sensor): ");
        Serial.println(send_result ? "Success" : "Failed");

        // Create JSON object for actuator data
        StaticJsonDocument<200> actuatorDoc;
        actuatorDoc["id"] = 12;
        actuatorDoc["token"] = auth_token;
        actuatorDoc["data"] = actuator_state;

        // Serialize JSON to string for actuator data
        String actuatorJson;
        serializeJson(actuatorDoc, actuatorJson);

        // Send JSON data for actuator
        send_result = client.send(actuatorJson);
        Serial.print("Send result (actuator): ");
        Serial.println(send_result ? "Success" : "Failed");

        delay(1000);  // Send data every second
    }
}
```

- **loop Function**: Polls for incoming WebSocket messages and handles reconnection if the client is not available. If `sendData` is true, reads sensor and actuator data, creates JSON objects, and sends the data to the server every second.

---








