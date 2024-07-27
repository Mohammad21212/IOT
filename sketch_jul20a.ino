#include <WiFi.h>
#include <ArduinoWebsockets.h>
#include <ArduinoJson.h>

const char* ssid = "Mohammad's A30";
const char* password = "mohammadjj80";
const char* auth_token = "your_secret_token"; // The same token used in the server

using namespace websockets;

WebsocketsClient client;
bool sendData = false;
bool dataSent = false;  // New flag to ensure data is sent only once

// Fan control pins
const int fanPin = 26; // DAC1 pin
const int controlPin = 27; // DAC2 pin

// Touch sensor and built-in LED pins
const int touchPin = 4; // Touch pin (T0 is GPIO4)
const int blueLEDPin = 2; // Built-in LED pin (usually GPIO2)

// Timing variables for touch sensor
volatile bool touchDetected = false;
unsigned long touchStartTime = 0;
unsigned long lastTouchTime = 0;
const unsigned long debounceDelay = 50; // Debounce delay in milliseconds
const int touchThreshold = 30; // Adjust this value as needed

// Generate a unique gateway identifier in the format G*******
String generateGatewayID() {
    String gateway_id = "G" + String(random(1000000, 9999999));  // Generate a random 7-digit number
    return gateway_id;
}

// Function to generate a random 16-bit token string
String generateToken() {
    String tokenString = "";
    for (int i = 0; i < 10; i++) { // Generate 10 random 16-bit numbers
        uint16_t randomToken = random(0, 65536); // Generate a 16-bit random number
        tokenString += String(randomToken); // Append the random number to the token string
    }
    return tokenString;
}

String gateway1_id = generateGatewayID();
String gateway1_token = generateToken();
String gateway1_name = "G1";

String gateway2_id = generateGatewayID();
String gateway2_token = generateToken();
String gateway2_name = "G2";
String websocket_server;

// Function to generate a random value and its dtype
void generateRandomValue(JsonObject& device) {
    int type = random(3); // Randomly choose between 0, 1, 2
    if (type == 0) {
        device["value"] = random(0, 100); // int value
        device["dtype"] = "int";
    } else if (type == 1) {
        int intValue = random(0, 100); // random integer part
        float floatValue = intValue + random(1, 6) / 10.0; // add a decimal part between .1 and .5
        device["value"] = floatValue;
        device["dtype"] = "float";
    } else {
        device["value"] = random(0, 2); // binary value (0 or 1)
        device["dtype"] = "binary";
    }
}

// Function to generate random devices including a fan as one of the actuators
void generateRandomDevices(JsonArray& devices, bool includeFan = false, bool includeTouchSensor = false) {
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
    if (includeFan) {
        JsonObject fan = devices.createNestedObject();
        fan["id"] = "A" + String(random(1000000, 9999999));
        fan["token"] = generateToken();
        fan["type"] = "actuator";
        fan["name"] = "Fan";
        fan["value"] = 0;  // Initially off
        fan["dtype"] = "binary";
    }
    if (includeTouchSensor) {
        JsonObject touchSensor = devices.createNestedObject();
        touchSensor["id"] = "T" + String(random(1000000, 9999999));
        touchSensor["token"] = generateToken();
        touchSensor["type"] = "sensor";
        touchSensor["name"] = "Touch Sensor";
        touchSensor["value"] = 0;  // Initially not touched
        touchSensor["dtype"] = "binary";
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
    } else if (message.data() == "Turn On Fan") {
        digitalWrite(fanPin, HIGH);  // Turn on fan
        digitalWrite(controlPin, HIGH);  // Ensure control pin is also set
    } else if (message.data() == "Turn Off Fan") {
        digitalWrite(fanPin, LOW);    // Turn off fan
        digitalWrite(controlPin, LOW);    // Ensure control pin is also set
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

void connectWebSocket(const char* ws_server) {
    Serial.println("Connecting to WebSocket server...");
    bool result = client.connect(ws_server);
    if (result) {
        Serial.println("WebSocket connected");
        client.send(auth_token); // Send the authentication token
    } else {
        Serial.println("WebSocket connection failed");
    }
}

// Touch sensor callback function
void IRAM_ATTR touchCallback() {
    unsigned long currentTime = millis();
    if (currentTime - lastTouchTime > debounceDelay) {
        touchDetected = true;
        touchStartTime = currentTime;
        lastTouchTime = currentTime;
    }
}

void readSerialInput(char* buffer, int length) {
  int index = 0;
  while (true) {
    if (Serial.available() > 0) {
      char incomingByte = Serial.read();
      if (incomingByte == '\n') {
        buffer[index] = '\0';
        break;
      } else if (index < length - 1) {
        buffer[index++] = incomingByte;
      }
    }
  }
}

char ipAddress[16];
int port;

void setup() {
    Serial.begin(115200);
    Serial.println("Enter IP address:");

    // Read the IP address from the serial monitor
    readSerialInput(ipAddress, sizeof(ipAddress));
    Serial.print("IP Address set to: ");
    Serial.println(ipAddress);

    Serial.println("Enter Port:");
    
    // Read the port from the serial monitor
    while (true) {
      if (Serial.available() > 0) {
        port = Serial.parseInt();
        if (port > 0) {
          break;
        }
      }
    }
    Serial.print("Port set to: ");
    Serial.println(port);

    websocket_server = "ws://" + String(ipAddress) + ":" + String(port);
    Serial.println(websocket_server);

    setup_wifi();

    client.onMessage(onMessageCallback);
    client.onEvent(onEventsCallback);

    connectWebSocket(websocket_server.c_str());

    pinMode(controlPin, OUTPUT);
    pinMode(fanPin, OUTPUT);
    digitalWrite(controlPin, LOW);  // Set control pin to LOW
    digitalWrite(fanPin, LOW);  // Initialize fan as off

    // Initialize built-in LED pin as output
    pinMode(blueLEDPin, OUTPUT);
    digitalWrite(blueLEDPin, LOW); // Turn off LED initially

    // Configure touch sensor
    touchAttachInterrupt(touchPin, touchCallback, touchThreshold);
}

void loop() {
    if (client.available()) {
        client.poll();
    } else {
        Serial.println("Client not available, reconnecting...");
        connectWebSocket(websocket_server.c_str());
    }

    if (sendData) {
        // Send data for gateway 1
        StaticJsonDocument<512> doc1;
        doc1["id"] = gateway1_id;
        doc1["token"] = gateway1_token;
        doc1["name"] = gateway1_name;
        JsonArray devices1 = doc1.createNestedArray("devices");
        generateRandomDevices(devices1, false, true);  // Include touch sensor

        String jsonString1;
        serializeJson(doc1, jsonString1);

        bool send_result1 = client.send(jsonString1);
        Serial.print("Send result for gateway 1: ");
        Serial.println(send_result1 ? "Success" : "Failed");

        // Send data for gateway 2 with fan
        StaticJsonDocument<512> doc2;
        doc2["id"] = gateway2_id;
        doc2["token"] = gateway2_token;
        doc2["name"] = gateway2_name;
        JsonArray devices2 = doc2.createNestedArray("devices");
        generateRandomDevices(devices2, true);  // Include fan

        String jsonString2;
        serializeJson(doc2, jsonString2);

        bool send_result2 = client.send(jsonString2);
        Serial.print("Send result for gateway 2: ");
        Serial.println(send_result2 ? "Success" : "Failed");

        sendData = false;  // Reset flag after sending data
    }

    // Handle touch sensor LED logic
    if (touchDetected) {
        if (millis() - touchStartTime < 5000) {
            digitalWrite(blueLEDPin, HIGH); // Turn on LED
        } else {
            digitalWrite(blueLEDPin, LOW); // Turn off LED after 5 seconds
            touchDetected = false; // Reset flag
        }
    }

    // Check if the fan is on and blink the blue LED
    if (digitalRead(fanPin) == HIGH) {
        static unsigned long lastBlinkTime = 0;
        unsigned long currentTime = millis();
        if (currentTime - lastBlinkTime >= 1000) { // Toggle every second
            digitalWrite(blueLEDPin, !digitalRead(blueLEDPin)); // Toggle LED state
            lastBlinkTime = currentTime;
        }
    } else {
        if (!touchDetected) {
            digitalWrite(blueLEDPin, LOW); // Ensure the LED is off if the fan is off and no touch detected
        }
    }
}
