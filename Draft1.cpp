#include <Arduino.h>
#include <M5StickC.h>


void setup() {
  M5.begin();
  M5.Imu.Init();
  M5.Lcd.begin();
  M5.Lcd.setRotation(1);
  M5.Lcd.setTextSize(1);
  M5.Lcd.fillScreen(BLACK);
  M5.Lcd.setCursor(0, 0);

  Serial.begin(115200);
  
}

void loop() {
  

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

  

  delay(1000);
}
