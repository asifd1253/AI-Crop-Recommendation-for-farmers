#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

// ================= WiFi =================
const char* ssid = "harvest";
const char* password = "12345678";

// ================= ThingSpeak =================
String apiKey = "L2NG4S0BJRYKVDSR";
const char* server = "http://api.thingspeak.com/update";

// ================= Pins =================
#define PH_PIN 34
#define RAIN_PIN 35
#define DHTPIN 4
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

// ================= pH Calibration (UPDATED) =================
float slope = 4.7675;
float offset = -0.2796;

// ================= Variables =================
float phValue = 0;
float temperature = 0;
float humidity = 0;
int rainValue = 0;

// ================= Timing =================
unsigned long previousSensorMillis = 0;
unsigned long previousUploadMillis = 0;

const long sensorInterval = 2000;   // 2 seconds
const long uploadInterval = 15000;  // 15 seconds (ThingSpeak limit)

// =====================================================
void connectWiFi() {
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected ✅");
}

// =====================================================
void readSensors() {

  // ----- Take multiple samples for stable pH -----
  float voltageSum = 0;

  for (int i = 0; i < 10; i++) {
    voltageSum += analogRead(PH_PIN);
    delay(10);
  }

  float phRaw = voltageSum / 10.0;
  float voltage = phRaw * (3.3 / 4095.0);

  // Apply calibrated formula
  phValue = (slope * voltage) + offset;

  rainValue = analogRead(RAIN_PIN);

  temperature = dht.readTemperature();
  humidity = dht.readHumidity();

  Serial.println("---- Sensor Update ----");
  Serial.print("Voltage: "); Serial.println(voltage, 3);
  Serial.print("pH: "); Serial.println(phValue, 2);
  Serial.print("Temp: "); Serial.println(temperature);
  Serial.print("Humidity: "); Serial.println(humidity);
  Serial.print("Rain: "); Serial.println(rainValue);
}

// =====================================================
void sendToThingSpeak() {

  if (WiFi.status() == WL_CONNECTED) {

    HTTPClient http;

    String url = server;
    url += "?api_key=" + apiKey;
    url += "&field1=" + String(phValue);
    url += "&field2=" + String(temperature);
    url += "&field3=" + String(humidity);
    url += "&field4=" + String(rainValue);

    http.begin(url);
    int httpResponseCode = http.GET();

    Serial.println("---- Uploading to ThingSpeak ----");

    if (httpResponseCode > 0) {
      Serial.println("Upload Success ✅");
    } else {
      Serial.print("Error Code: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  }
}

// =====================================================
void setup() {
  Serial.begin(115200);
  dht.begin();
  connectWiFi();
}

// =====================================================
void loop() {

  unsigned long currentMillis = millis();

  // ===== Sensor reading every 2 seconds =====
  if (currentMillis - previousSensorMillis >= sensorInterval) {
    previousSensorMillis = currentMillis;
    readSensors();
  }

  // ===== Upload every 15 seconds =====
  if (currentMillis - previousUploadMillis >= uploadInterval) {
    previousUploadMillis = currentMillis;
    sendToThingSpeak();
  }
}