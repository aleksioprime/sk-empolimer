#include <SoftwareSerial.h>

// Пины для SoftwareSerial (можно изменить на любые свободные пины)
#define ESP_RX 8  // Arduino получает данные от ESP (ESP TX)
#define ESP_TX 9  // Arduino отправляет данные в ESP (ESP RX)

// Создаём виртуальный порт для связи с ESP
SoftwareSerial esp(ESP_RX, ESP_TX);

// Интервал между отправкой данных
unsigned long lastSend = 0;
const unsigned long sendInterval = 3000; // 3 секунды

void setup() {
  Serial.begin(9600);     // Основной порт — для отладки в Serial Monitor
  esp.begin(9600);        // Порт связи с ESP

  Serial.println("Инициализация завершена. Отправка данных через ESP начнётся через 3 секунды...");
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - lastSend >= sendInterval) {
    lastSend = currentMillis;

    // ==== Имитация показаний датчиков ====
    float temperature = random(200, 300) / 10.0;  // 20.0 - 30.0
    int humidity = random(40, 70);               // 40 - 70 %

    // ==== Формируем строки и отправляем в ESP ====
    String tempStr = "temp:" + String(temperature, 1);
    String humStr = "hum:" + String(humidity);

    // Печатаем в монитор (для отладки)
    Serial.println("Отправка в ESP:");
    Serial.println(tempStr);
    Serial.println(humStr);

    // Отправка по SoftwareSerial
    esp.println(tempStr);
    delay(10);
    esp.println(humStr);
  }
}
