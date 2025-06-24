// --- Выбери используемый модем ---
#define TINY_GSM_MODEM_SIM800  // Модем SIM800

#include <TinyGsmClient.h>  // Работа с GPRS-модемом по AT-командам
#include <PubSubClient.h>   // MQTT-клиент
#include <TroykaDHT.h>      // Работа с датчиком температуры и влажности DHT

// --- Датчик температуры и влажности ---
#define DHTPIN 8
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// Используем аппаратный Serial1 для модема (TX1=1, RX1=0 на Micro Pro)
TinyGsm modem(Serial1);
TinyGsmClient gsmClient(modem);
PubSubClient mqtt(gsmClient);

// --- MQTT параметры ---
const char* broker = "mqtt.dealgate.ru";
const int port = 1883;
const char* mqttUser = "alprime";
const char* mqttPass = "Techno0255";
const char* clientId = "empolimer_base";

// --- GPRS параметры ---
const char* apn = "internet.mts.ru";
const char* gprsUser = "mts";
const char* gprsPass = "mts";

// --- Интервалы ---
const unsigned long sensorInterval = 5000;      // Опрос DHT (мс)
const unsigned long mqttInterval = 15000;       // Публикация MQTT (мс)
const unsigned long gprsTimeout = 10000;        // Таймаут подключения к GPRS (мс)
const unsigned long gprsRetryInterval = 20000;  // Интервал попыток переподключения (мс)
const unsigned long mqttTryInterval = 7000;     // Интервал попыток MQTT connect (мс)

// --- Глобальные переменные ---
float cachedTemp = -100;
float cachedHum = -1;
unsigned long lastSensorRead = 0;
unsigned long lastMqttSend = 0;
unsigned long lastMqttTry = 0;

enum GprsState {
  GPRS_INIT,
  GPRS_CONNECTING,
  GPRS_CONNECTED,
  GPRS_ERROR
};
GprsState gprsState = GPRS_INIT;
unsigned long gprsStartTime = 0;
unsigned long lastGprsRetry = 0;

String getGsmTime() {
  String timeStr = "";
  modem.sendAT(GF("+CCLK?"));
  if (modem.waitResponse(1000L, timeStr) == 1) {
    int idx = timeStr.indexOf("+CCLK: ");
    if (idx >= 0) {
      int start = idx + 8;
      int end = timeStr.indexOf("\r", start);
      String dt = timeStr.substring(start, end);
      dt.replace("\"", "");
      return dt;  // Вернём строку типа "24/06/24,19:42:56+04"
    }
  }
  // Если времени нет — вернём пустую строку
  return "";
}

void mqttReconnect() {
  // 1. Проверяем связь с модемом, если нет — авария, всё сбрасываем!
  if (!modem.testAT()) {
    Serial.println("Модем не отвечает! Переподключение GPRS...");
    gprsState = GPRS_ERROR;
    return;
  }

  // 2. Пауза между попытками подключения к MQTT
  if (millis() - lastMqttTry < mqttTryInterval) {
    return;
  }
  lastMqttTry = millis();

  Serial.print("MQTT reconnecting...");
  if (mqtt.connect(clientId, mqttUser, mqttPass)) {
    Serial.println("OK!");
  } else {
    Serial.print(" failed, rc=");
    Serial.print(mqtt.state());
    Serial.println(" retry next loop");
  }
}

void setup() {
  Serial.begin(9600);
  delay(500);
  Serial.println("Ожидание модема...");
  delay(2000);
  Serial1.begin(9600);
  delay(500);

  Serial.println("Инициализация модема...");
  modem.restart();
  delay(2000);

  Serial.println("Инициализация датчика DHT...");
  dht.begin();

  gprsState = GPRS_INIT;

  // --- Попросим у SIM800L обновить время через сеть ---
  // Для некоторых операторов время может не устанавливаться автоматически,
  // но если работает - "AT+CLTS=1" (разрешить автомат. обновление времени)
  modem.sendAT("+CLTS=1");
  modem.sendAT("+CFUN=1");

  Serial.println("Готово! Основной цикл...");
}

void loop() {
  unsigned long now = millis();

  // --- Автомат GPRS, не блокирует цикл! ---
  switch (gprsState) {
    case GPRS_INIT:
      Serial.println("Попытка подключения к GPRS...");
      modem.gprsConnect(apn, gprsUser, gprsPass);  // Асинхронный запуск подключения!
      gprsState = GPRS_CONNECTING;
      gprsStartTime = now;
      break;
    case GPRS_CONNECTING:
      if (modem.isGprsConnected()) {
        Serial.println("GPRS подключено!");
        gprsState = GPRS_CONNECTED;
        mqtt.setServer(broker, port);
      } else if (now - gprsStartTime > gprsTimeout) {
        Serial.println("GPRS не подключился за таймаут! Ошибка.");
        gprsState = GPRS_ERROR;
        lastGprsRetry = now;
      }
      break;
    case GPRS_ERROR:
      if (now - lastGprsRetry > gprsRetryInterval) {
        Serial.println("Пытаемся переподключиться к GPRS...");
        modem.restart();
        delay(1000);
        modem.gprsDisconnect();
        delay(1000);
        gprsState = GPRS_INIT;  // Через loop снова начнём соединение!
      }
      break;
    case GPRS_CONNECTED:
      if (!modem.testAT()) {
        Serial.println("GSM-модуль не отвечает (GPRS_CONNECTED). Сброс...");
        gprsState = GPRS_ERROR;
        break;
      }
      if (!mqtt.connected()) {
        mqttReconnect();
      }
      mqtt.loop();

      // --- Публикация данных и времени ---
      if (mqtt.connected() && (now - lastMqttSend >= mqttInterval)) {
        lastMqttSend = now;
        String gsmTime = getGsmTime();

        // Преобразуем в ISO 8601: "24/06/24,19:42:56+04" -> "2024-06-24T19:42:56+04"
        gsmTime.replace("\"", "");
        if (gsmTime.length() >= 17) {
          // "24/06/24,19:42:56+04"
          String date = "20" + gsmTime.substring(0, 2) + "-" + gsmTime.substring(3, 5) + "-" + gsmTime.substring(6, 8);
          String time = gsmTime.substring(9, 17);
          String zone = gsmTime.substring(17);
          gsmTime = date + "T" + time + zone;  // "2024-06-24T19:42:56+04"
        }

        // Формируем JSON (темп и влажность)
        String json = "{\"datetime\":\"" + gsmTime + "\","
                                                     "\"temp\":"
                      + String(cachedTemp, 1) + ","
                                                "\"hum\":"
                      + String(cachedHum, 1) + "}";

        mqtt.publish("empolimer_base/air", json.c_str(), true);
        Serial.print("Published: ");
        Serial.println(json);
      }
      break;
    default:
      break;
  }

  // --- Опрос DHT11 (работает всегда!) ---
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
      cachedTemp = -100;
      cachedHum = -1;
    }
  }
}
