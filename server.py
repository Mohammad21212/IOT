# server.py
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

# A dictionary to store connected clients (gateways) and their addresses
connected_clients = {}
data_sending_enabled = {}
latest_data = []

# Simple token-based authentication
AUTH_TOKEN = "your_secret_token"

async def authenticate(websocket, path):
    try:
        auth_message = await websocket.recv()
        logging.debug(f"Received authentication message: {auth_message} from {websocket.remote_address}")
        if auth_message == AUTH_TOKEN:
            await websocket.send("Authentication Successful")
            logging.debug(f"Authentication successful for {websocket.remote_address}")
            return True
        else:
            await websocket.send("Authentication Failed")
            logging.warning(f"Authentication failed for {websocket.remote_address}")
            await websocket.close()
            return False
    except Exception as e:
        logging.error(f"Authentication error: {e} for {websocket.remote_address}")
        logging.error(traceback.format_exc())
        return False

async def save_data(data_type, data):
    try:
        logging.debug(f"Saving data: {data} to {data_type}")
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')
        folder_path = f"data/{data_type}"
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, f"{timestamp}.json")
        with open(file_path, 'w') as f:
            json.dump(data, f)
        latest_data.append(data)  # Store the latest data
        logging.info(f"Data saved to {file_path}")
    except Exception as e:
        logging.error(f"Error saving data: {e}")
        logging.error(traceback.format_exc())

async def handler(websocket, path):
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
            devices = data.get("Devices", [])
            if data_sending_enabled[client_id]:
                for device in devices:
                    device_type = device.get("type")
                    logging.debug(f"Device data received: {device}")
                    if device_type == "sensor":
                        await save_data("sensors", device)
                    elif device_type == "actuator":
                        await save_data("actuators", device)
            response = f"Processed: {message}"
            await websocket.send(response)
            logging.info(f"Sent response to {client_id}: {response}")
    except websockets.exceptions.ConnectionClosed as e:
        logging.warning(f"Client disconnected: {client_id}")
        logging.warning(traceback.format_exc())
    finally:
        # Unregister the client
        del connected_clients[client_id]
        del data_sending_enabled[client_id]
        logging.info(f"Client {client_id} unregistered")

async def hello(request):
    return web.Response(text="Hello, world")

async def start_send(request):
    global data_sending_enabled
    for client_id, websocket in connected_clients.items():
        data_sending_enabled[client_id] = True
        await websocket.send("Start Sending Data")
    return web.Response(text="Data sending enabled")

async def stop_send(request):
    global data_sending_enabled
    for client_id, websocket in connected_clients.items():
        data_sending_enabled[client_id] = False
        await websocket.send("Stop Sending Data")
    return web.Response(text="Data sending disabled")

async def control_page(request):
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

async def get_latest_data(request):
    return web.json_response(latest_data)

async def main():
    try:
        server = await websockets.serve(handler, "0.0.0.0", 8766, ping_interval=120, ping_timeout=60)
        logging.info("WebSocket server started")

        app = web.Application()
        app.router.add_get('/', hello)
        app.router.add_get('/start_send', start_send)
        app.router.add_get('/stop_send', stop_send)
        app.router.add_get('/control', control_page)
        app.router.add_get('/get_data', get_latest_data)  # Add this line for the new endpoint
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
