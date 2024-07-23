#include <WiFi.h>
#include <ArduinoWebsockets.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>

const char* ssid = "Mohammad's A30";
const char* password = "mohammadjj80";
const char* websocket_server = "ws://192.168.107.19:8766";  // Correct IP address
const char* auth_token = "your_secret_token"; // The same token used in the server

using namespace websockets;

WebsocketsClient client;
bool sendData = false;

// Function to generate a random token from the UUID API
String generateToken() {
    HTTPClient http;
    http.begin("https://www.uuidgenerator.net/api/version4");
    int httpCode = http.GET();
    String payload;
    if (httpCode > 0) {
        payload = http.getString();
    }
    http.end();
    payload.trim();
    return payload;
}

// Function to generate a random value and its dtype
void generateRandomValue(JsonObject& device) {
    int type = random(3); // Randomly choose between 0, 1, 2
    if (type == 0) {
        device["value"] = random(0, 100); // int value
        device["dtype"] = "int";
    } else if (type == 1) {
        device["value"] = random(0, 100) / 1.0; // float value
        device["dtype"] = "float";
    } else {
        device["value"] = random(0, 2); // binary value (0 or 1)
        device["dtype"] = "binary";
    }
}

// Function to generate random devices
void generateRandomDevices(JsonArray& devices) {
    for (int i = 0; i < 5; i++) {
        JsonObject sensor = devices.createNestedObject();
        sensor["id"] = "S" + String(random(1000000, 9999999));
        sensor["token"] = generateToken();
        sensor["type"] = "sensor";
        sensor["name"] = "Sensor " + String(i + 1);
        generateRandomValue(sensor); // Assign random value and dtype
    }
    for (int i = 0; i < 5; i++) {
        JsonObject actuator = devices.createNestedObject();
        actuator["id"] = "A" + String(random(1000000, 9999999));
        actuator["token"] = generateToken();
        actuator["type"] = "actuator";
        actuator["name"] = "Actuator " + String(i + 1);
        generateRandomValue(actuator); // Assign random value and dtype
    }
}


void setup_wifi() {
    Serial.begin(115200);
    delay(10);
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);

    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println();
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
}

void onMessageCallback(WebsocketsMessage message) {
    Serial.print("Received: ");
    Serial.println(message.data());
    if (message.data() == "Start Sending Data") {
        sendData = true;
    } else if (message.data() == "Stop Sending Data") {
        sendData = false;
    }
}

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

void setup() {
    Serial.begin(115200);
    setup_wifi();

    client.onMessage(onMessageCallback);
    client.onEvent(onEventsCallback);

    connectWebSocket();
}

void loop() {
    if (client.available()) {
        client.poll();
    } else {
        Serial.println("Client not available, reconnecting...");
        connectWebSocket();
    }

    if (sendData) {
        StaticJsonDocument<512> doc;
        JsonArray devices = doc.createNestedArray("Devices");
        generateRandomDevices(devices);

        String jsonString;
        serializeJson(doc, jsonString);

        bool send_result = client.send(jsonString);
        Serial.print("Send result: ");
        Serial.println(send_result ? "Success" : "Failed");

        delay(1000);  
    }
}
