// ==== Подключение библиотек ====
#include <TroykaDHT.h>            // Для работы с датчиком температуры и влажности DHT11
#include <Adafruit_GFX.h>         // Графическая библиотека от Adafruit
#include <Adafruit_PCD8544.h>     // Драйвер дисплея Nokia 5110
#include <GPRS_Shield_Arduino.h>  // Библиотека для управления GPRS Shield
#include <SoftwareSerial.h>       // Для создания виртуального (программного) последовательного порта
#include <PubSubClient.h>

// ==== Инициализация DHT11 ====
DHT dht(12, DHT11);  // Датчик подключен к пину 12, используется тип DHT11

// ==== Настройка пинов дисплея Nokia 5110 ====
#define PIN_SCE 11
#define PIN_RST 7
#define PIN_DC 6
#define PIN_DIN 5
#define PIN_SCLK 4
Adafruit_PCD8544 display = Adafruit_PCD8544(PIN_SCLK, PIN_DIN, PIN_DC, PIN_SCE, PIN_RST);

// ==== Инициализация GPRS (используется аппаратный Serial порт) ====
// Можно заменить на SoftwareSerial при необходимости
// SoftwareSerial mySerial(9, 8);
// GPRS gprs(mySerial);
GPRS gprs(Serial);

// ==== MQTT настройки ====
const char* broker = "mqtt.dealgate.ru";  // Адрес MQTT брокера
const int port = 1883;                    // Порт MQTT (обычно 1883)
const char* topicTemp = "arduino/temp";   // Топик для температуры
const char* topicHum = "arduino/hum";     // Топик для влажности
const char* clientId = "ArduinoGPRS";     // Имя клиента
const char* mqtt_user = "alprime";        // Имя пользователя
const char* mqtt_pass = "Techno0255";     // Пароль

// ==== Статус соединений ====
String gprsStatus = "-";        // Статус подключения GPRS
String mqttStatus = "-";         // Статус MQTT
bool isTryingReconnect = false;  // Флаг попытки переподключения

// ==== Переменные для интервалов ====
unsigned long lastSensorRead = 0;
unsigned long lastMqttSend = 0;
unsigned long lastReconnectAttempt = 0;
const unsigned long sensorInterval = 2000;     // интервал обновления датчика
const unsigned long mqttInterval = 5000;       // интервал отправки MQTT
const unsigned long reconnectInterval = 2000;  // интервал переподключения

bool gprsConnected = false;
bool tcpConnected = false;
bool mqttConnected = false;

// ==== Кэш значений температуры и влажности ====
float cachedTemp = -1;
float cachedHum = -1;

// ==== Функция отображения статуса на дисплее ====
void displayStatus(String gprs, String mqtt, float temp = -1, float hum = -1) {
  display.clearDisplay();

  display.setCursor(0, 0);
  display.setTextSize(1);

  // Если данные с датчика есть — выводим
  if (temp >= 0) {
    display.print("T: ");
    display.println(temp, 1);
    display.print("H: ");
    display.println(hum, 1);
  } else {
    display.println("No sensor data");  // иначе сообщение об ошибке
  }

  // Строки GPRS и MQTT внизу
  display.setTextSize(0);  // мелкий шрифт
  display.setCursor(0, 24);
  display.print("GPRS: ");
  display.println(gprs);
  display.print("MQTT: ");
  display.println(mqtt);

  display.display();
}

// ==== Функция для вывода временного сообщения ====
void showLiveStatus(const String& msg) {
  display.fillRect(0, 40, 84, 8, WHITE);  // очистить нижнюю строку
  display.setCursor(0, 40);
  display.setTextSize(1);
  display.setTextColor(BLACK);
  display.print(msg);
  display.display();
}

// ==== Очистка буфера Serial ====
void flushSerial() {
  while (Serial.available()) {
    Serial.read();
  }
}

void debugBytes(const String& title, const String& data, int groupSize = 8, int delayMs = 1500) {
  int len = data.length();
  for (int i = 0; i < len; i += groupSize) {
    String row = title + " ";
    for (int j = 0; j < groupSize && (i + j) < len; j++) {
      byte b = data[i + j];
      if (b < 16) row += "0";
      row += String(b, HEX) + " ";
    }
    showLiveStatus(row);
    delay(delayMs);
  }
}

void forceGprsClose() {
  Serial.println("+++");
  delay(100);
  Serial.println("AT+CIPCLOSE");
  delay(500);
  Serial.println("AT+CIPSHUT");
  delay(1500);
  flushSerial();
}

// ==== SETUP ====
void setup() {
  Serial.begin(9600);  // основной Serial порт

  dht.begin();         // инициализация датчика
  display.begin();     // инициализация дисплея
  display.setContrast(50);
  display.setTextSize(1);
  display.setTextColor(BLACK);

  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("Starting...");
  display.display();

  gprs.powerOn();  // включение GPRS модуля
  showLiveStatus("Init GPRS...");

  gprs.init();
}

// ==== LOOP ====
void loop() {
  unsigned long now = millis();

  // ==== Чтение датчика ====
  if (now - lastSensorRead >= sensorInterval) {
    lastSensorRead = now;
    dht.read();
    if (dht.getState() == DHT_OK) {
      cachedTemp = dht.getTemperatureC();
      cachedHum = dht.getHumidity();
    } else {
      cachedTemp = -1;
      cachedHum = -1;
    }
    displayStatus(gprsStatus, mqttStatus, cachedTemp, cachedHum);
  }

  // ==== GPRS соединение (держим между перезагрузками) ====
  if (!gprsConnected) {
    showLiveStatus("GPRS join...");
    if (gprs.init() && gprs.join("internet.mts.ru", "mts", "mts")) {
      gprsStatus = "OK";
      gprsConnected = true;
      showLiveStatus("GPRS OK");
    } else {
      gprsStatus = "-";
      mqttStatus = "-";
      showLiveStatus("GPRS FAIL");
      delay(5000);  // Даем время модему отдохнуть
      return;
    }
    displayStatus(gprsStatus, mqttStatus, cachedTemp, cachedHum);
    delay(1000);
  }

  // ==== TCP + MQTT-сессия (живет, пока не отвалится) ====
  if (!mqtt.connected()) {
    mqttStatus = "-";
    showLiveStatus("MQTT reconn...");
    while (!mqtt.connect(clientId, mqttUser, mqttPass)) {
      showLiveStatus("MQTT retry...");
      delay(2000);
    }
    mqttStatus = "OK";
    showLiveStatus("MQTT OK");
    delay(500);
  }
  mqtt.loop();

  // ==== Публикация в MQTT ====
  if (mqtt.connected() && (now - lastMqttSend >= mqttInterval)) {
    lastMqttSend = now;
    if (cachedTemp > -50 && cachedTemp < 100)
      mqtt.publish("arduino/temp", String(cachedTemp, 1).c_str());
    if (cachedHum >= 0 && cachedHum <= 100)
      mqtt.publish("arduino/hum", String(cachedHum, 1).c_str());
    showLiveStatus("MQTT SEND");
    delay(200);
  }
}
