#include <Arduino.h>
#include <M5StickC.h>
#include <WiFi.h>
#include <PubSubClient.h>

// WiFi settings
const char* ssid = "Tree Learning";
const char* password = "minitui1";

// MQTT settings
const char* mqtt_server = "broker.emqx.io"; // หรือใส่ IP เซิร์ฟเวอร์ EMQX ของคุณ
const int mqtt_port = 1883;
const char* mqtt_client_id = "Aueaphum_M5StickC";
const char* topic_sub = "thammasat/aueaphum/led";
const char* topic_pub_acc = "thammasat/aueaphum/sensor/acc";
const char* topic_pub_gyro = "thammasat/aueaphum/sensor/gyro";

WiFiClient espClient;
PubSubClient client(espClient);

// WiFi connect
void setup_wifi() {
  WiFi.begin(ssid, password);
  M5.Lcd.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    M5.Lcd.print(".");
  }
  Serial.println("WiFi connected");
  M5.Lcd.println("\nWiFi connected");
}

// Callback for MQTT subscription
void callback(char* topic, byte* message, unsigned int length) {
  if (message[0] == '1') {
    digitalWrite(10, LOW);  // ON
  } else {
    digitalWrite(10, HIGH); // OFF
  }
}

// MQTT setup
void setup_mqtt() {
  pinMode(10, OUTPUT);
  digitalWrite(10, HIGH); // default OFF
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

// MQTT reconnect loop
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect(mqtt_client_id)) {
      Serial.println("connected");
      client.subscribe(topic_sub);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 1 sec");
      delay(1000);
    }
  }
}

void setup() {
  M5.begin();
  M5.Imu.Init();
  M5.Lcd.begin();
  M5.Lcd.setRotation(1);
  M5.Lcd.setTextSize(1);
  M5.Lcd.fillScreen(BLACK);
  M5.Lcd.setCursor(0, 0);

  Serial.begin(115200);
  setup_wifi();
  setup_mqtt();

  Serial.println("Starting...");
  M5.Lcd.println("Starting...");
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  M5.update();

  float ax, ay, az;
  float gx, gy, gz;
  char sensor_buf[150];

  // Read IMU data
  M5.Imu.getAccelData(&ax, &ay, &az);
  M5.Imu.getGyroData(&gx, &gy, &gz);

  // Print to Serial
  Serial.printf("ACC: X: %.2f, Y: %.2f, Z: %.2f\n", ax, ay, az);
  Serial.printf("GYRO: GX: %.2f, GY: %.2f, GZ: %.2f\n", gx, gy, gz);

  // Print to screen
  M5.Lcd.fillScreen(BLACK);
  M5.Lcd.setCursor(0, 0);
  M5.Lcd.printf("ACC\nX: %.2f\nY: %.2f\nZ: %.2f\n", ax, ay, az);
  M5.Lcd.printf("\nGYRO\nGX: %.2f\nGY: %.2f\nGZ: %.2f", gx, gy, gz);

  // Combine data and publish to single topic
  sprintf(sensor_buf, "AX:%.2f,AY:%.2f,AZ:%.2f,GX:%.2f,GY:%.2f,GZ:%.2f", ax, ay, az, gx, gy, gz);
  client.publish("thammasat/aueaphum/sensor", sensor_buf);

  delay(1000);
}
