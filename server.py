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

connected_clients = {}
data_sending_enabled = {}
latest_data = {}

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

async def save_data(gateway_name, data):
    try:
        logging.debug(f"Saving data for gateway {gateway_name}: {data}")
        folder_path = "data"
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, f"{gateway_name}.json")
        with open(file_path, 'w') as f:
            json.dump(data, f)
        latest_data[gateway_name] = data
        logging.info(f"Data saved to {file_path}")
    except Exception as e:
        logging.error(f"Error saving data: {e}")
        logging.error(traceback.format_exc())

async def handler(websocket, path):
    global data_sending_enabled
    logging.info(f"New connection from {websocket.remote_address}")
    if not await authenticate(websocket, path):
        return

    client_id = websocket.remote_address
    connected_clients[client_id] = websocket
    data_sending_enabled[client_id] = False
    logging.info(f"Client connected: {client_id}")

    try:
        async for message in websocket:
            logging.info(f"Received message from {client_id}: {message}")
            data = json.loads(message)
            gateway_name = data.get("name")
            if data_sending_enabled[client_id]:
                await save_data(gateway_name, data)
            response = f"Processed: {message}"
            await websocket.send(response)
            logging.info(f"Sent response to {client_id}: {response}")
    except websockets.exceptions.ConnectionClosed as e:
        logging.warning(f"Client disconnected: {client_id}")
        logging.warning(traceback.format_exc())
    finally:
        del connected_clients[client_id]
        del data_sending_enabled[client_id]
        logging.info(f"Client {client_id} unregistered")

async def start_send():
    global data_sending_enabled
    for client_id, websocket in connected_clients.items():
        data_sending_enabled[client_id] = True
        await websocket.send("Start Sending Data")
    logging.info("Data sending enabled for all clients")

async def stop_send():
    global data_sending_enabled
    for client_id, websocket in connected_clients.items():
        data_sending_enabled[client_id] = False
        await websocket.send("Stop Sending Data")
    logging.info("Data sending disabled for all clients")

async def turn_on_fan():
    for client_id, websocket in connected_clients.items():
        await websocket.send("Turn On Fan")
    gateway_name = 'G2'
    if gateway_name in latest_data:
        for device in latest_data[gateway_name]['devices']:
            if device['name'] == 'Fan':
                device['value'] = 1
    logging.info("Fan turned on")

async def turn_off_fan():
    for client_id, websocket in connected_clients.items():
        await websocket.send("Turn Off Fan")
    gateway_name = 'G2'
    if gateway_name in latest_data:
        for device in latest_data[gateway_name]['devices']:
            if device['name'] == 'Fan':
                device['value'] = 0
    logging.info("Fan turned off")

async def control_fan(request):
    data = await request.json()
    action = data.get("action")
    if action == "turn_on":
        await turn_on_fan()
        return web.Response(text="Fan turned on")
    elif action == "turn_off":
        await turn_off_fan()
        return web.Response(text="Fan turned off")
    else:
        return web.Response(status=400, text="Invalid action")

async def get_latest_data(request):
    gateway_name = request.query.get('gateway_name')
    if gateway_name:
        if gateway_name in latest_data:
            return web.json_response(latest_data[gateway_name])
        else:
            return web.json_response({"error": "No data found for the specified gateway"}, status=404)
    return web.json_response(latest_data)

async def main():
    try:
        server = await websockets.serve(handler, "0.0.0.0", 8766, ping_interval=120, ping_timeout=60)
        logging.info("WebSocket server started")

        app = web.Application()
        app.router.add_post('/control_fan', control_fan)
        app.router.add_get('/get_data', get_latest_data)
        app.router.add_get('/start_send', lambda request: start_send())
        app.router.add_get('/stop_send', lambda request: stop_send())
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        await site.start()
        logging.info("HTTP server started on port 8080")

        await asyncio.Future()
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







