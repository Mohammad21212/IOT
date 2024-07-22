#include <WiFi.h>
#include <ArduinoWebsockets.h>
#include <ArduinoJson.h>

const char* ssid = "Mohammad's A30";
const char* password = "mohammadjj80";
const char* websocket_server = "ws://192.168.159.19:8766";  // Correct IP address
const char* auth_token = "your_secret_token"; // The same token used in the server

using namespace websockets;

WebsocketsClient client;
bool sendData = false;

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

float readSensorData(int pin) {
    int sensorValue = analogRead(pin);  // Example sensor data
    float voltage = sensorValue * (3.3 / 4095.0); // Convert ADC reading to voltage
    Serial.print("Sensor Value: ");
    Serial.print(sensorValue);
    Serial.print(" Voltage: ");
    Serial.println(voltage);
    return voltage;
}

bool readActuatorData(int pin) {
    bool state = digitalRead(pin);  // Example actuator data
    Serial.print("Actuator State: ");
    Serial.println(state);
    return state;
}

void loop() {
    if (client.available()) {
        client.poll();
    } else {
        Serial.println("Client not available, reconnecting...");
        connectWebSocket();
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
