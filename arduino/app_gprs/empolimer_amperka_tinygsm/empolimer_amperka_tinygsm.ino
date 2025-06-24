// --- Выбери используемый модем ---
#define TINY_GSM_MODEM_SIM800  // Модем SIM800

#include <TinyGsmClient.h>  // Работа с GPRS-модемом по AT-командам
#include <PubSubClient.h>   // MQTT-клиент
#include <TroykaDHT.h>      // Работа с датчиком температуры и влажности DHT

// --- Датчик DHT ---
DHT dht(8, DHT11);  // DHT11 на пине 12

// --- Используем аппаратный Serial для модема ---
TinyGsm modem(Serial);  // TinyGsm через Serial (Serial1 для Mega)
TinyGsmClient gsmClient(modem);
PubSubClient mqtt(gsmClient);

// --- MQTT параметры ---
const char* broker = "mqtt.dealgate.ru";
const int port = 1883;
const char* mqttUser = "alprime";
const char* mqttPass = "Techno0255";
const char* clientId = "gprstest1";

// --- GPRS параметры ---
const char* apn = "internet.mts.ru";
const char* gprsUser = "mts";
const char* gprsPass = "mts";

// --- Интервалы ---
const unsigned long sensorInterval = 5000;      // Опрос DHT (мс)
const unsigned long mqttInterval = 15000;       // Публикация MQTT (мс)
const unsigned long gprsTimeout = 20000;        // Таймаут подключения к GPRS (мс)
const unsigned long gprsRetryInterval = 20000;  // Интервал попыток переподключения (мс)

// --- Глобальные переменные ---
float cachedTemp = -1;             // Последняя температура
float cachedHum = -1;              // Последняя влажность
unsigned long lastSensorRead = 0;  // Время последнего опроса DHT
unsigned long lastMqttSend = 0;    // Время последней публикации MQTT

// --- Состояние GPRS ---
enum GprsState {
  GPRS_INIT,        // Только запускаем
  GPRS_CONNECTING,  // Идёт подключение к GPRS
  GPRS_CONNECTED,   // Подключено к GPRS
  GPRS_ERROR        // Ошибка подключения
};
GprsState gprsState = GPRS_INIT;
unsigned long gprsStartTime = 0;  // Время старта подключения GPRS
unsigned long lastGprsRetry = 0;  // Время последней попытки переподключения

// --- Включение SIM800 через PowerKey (PK) ---
void powerOnSim800() {
  pinMode(PIN_PWRKEY, OUTPUT);
  digitalWrite(PIN_PWRKEY, LOW);  // Держим LOW ~1-1.5 сек для включения
  delay(1200);
  digitalWrite(PIN_PWRKEY, HIGH);  // Отпускаем
  delay(5000);                     // Ждём запуска модуля
}

// --- Переподключение к MQTT ---
void mqttReconnect() {
  if (!mqtt.connected()) {
    Serial.print("MQTT reconnecting...");
    if (mqtt.connect(clientId, mqttUser, mqttPass)) {
      Serial.println("OK!");
    } else {
      Serial.print(" failed, rc=");
      Serial.print(mqtt.state());
      Serial.println(" retry next loop");
      // Без delay — попробует снова на следующей итерации
    }
  }
}

void setup() {
  Serial.begin(9600);
  delay(1000);

  Serial.println("Перезапуск модема...");
  powerOnSim800();  // Включаем SIM800
  delay(2000);      // Дожидаемся запуска

  Serial.println("Инициализация модема...");
  modem.init();  // Инициализируем модем

  Serial.println("Инициализация датчика DHT...");
  dht.begin();  // Инициализация датчика DHT

  // --- Первое подключение к GPRS ---
  Serial.println("Первое подключение к GPRS...");
  modem.gprsConnect(apn, gprsUser, gprsPass);
  gprsState = GPRS_CONNECTING;
  gprsStartTime = millis();

  Serial.println("Старт основного цикла...");
}

void loop() {
  unsigned long now = millis();

  // --- Управление подключением к GPRS ---
  if (gprsState == GPRS_CONNECTING) {
    if (modem.isGprsConnected()) {
      Serial.println("GPRS подключено!");
      gprsState = GPRS_CONNECTED;
      mqtt.setServer(broker, port);  // Теперь можно настраивать MQTT
    } else if (now - gprsStartTime > gprsTimeout) {
      Serial.println("Ошибка GPRS подключения!");
      gprsState = GPRS_ERROR;
      lastGprsRetry = now;  // Сохраняем время ошибки для старта таймера переподключения
    }
    // Здесь можно выполнять другие задачи (опрос датчиков, обновление экрана и т.п.)
  }

  // --- Переподключение GPRS при ошибке ---
  if (gprsState == GPRS_ERROR) {
    if (now - lastGprsRetry > gprsRetryInterval) {
      Serial.println("Пытаемся переподключиться к GPRS...");
      modem.gprsDisconnect();                      // Отключаем старое соединение (если было)
      delay(2000);                                 // Короткая пауза для корректного отключения
      modem.gprsConnect(apn, gprsUser, gprsPass);  // Пробуем подключиться снова
      gprsState = GPRS_CONNECTING;
      gprsStartTime = millis();
      lastGprsRetry = now;
    }
  }

  // --- Основная работа, если GPRS подключено ---
  if (gprsState == GPRS_CONNECTED) {
    // 1. Поддерживаем MQTT-соединение
    if (!mqtt.connected()) {
      mqttReconnect();
    }
    mqtt.loop();

    // 2. Публикация данных в MQTT по расписанию
    if (mqtt.connected() && (now - lastMqttSend >= mqttInterval)) {
      lastMqttSend = now;
      bool published = false;
      if (cachedTemp > -50 && cachedTemp < 100) {
        mqtt.publish("arduino/temp", String(cachedTemp, 1).c_str());
        Serial.print("Published temp: ");
        Serial.println(cachedTemp, 1);
        published = true;
      }
      if (cachedHum >= 0 && cachedHum <= 100) {
        mqtt.publish("arduino/hum", String(cachedHum, 1).c_str());
        Serial.print("Published hum: ");
        Serial.println(cachedHum, 1);
        published = true;
      }
      if (published)
        Serial.println("MQTT publish done");
    }
  }

  // --- Опрос датчика по расписанию ---
  if (now - lastSensorRead >= sensorInterval) {
    lastSensorRead = now;
    dht.read();

    if (dht.getState() == DHT_OK) {
      cachedTemp = dht.getTemperatureC();
      cachedHum = dht.getHumidity();
      Serial.print("Sensor: T=");
      Serial.print(cachedTemp, 1);
      Serial.print(" H=");
      Serial.println(cachedHum, 1);
    } else {
      Serial.print("Sensor error: ");
      Serial.println(dht.getState());
      cachedTemp = -1;
      cachedHum = -1;
    }
  }

  // --- (Здесь можно добавить код обновления экрана, работы с кнопками, LED-индикации и т.д.) ---
}
