// --- Выбери используемый модем ---
#define TINY_GSM_MODEM_SIM800  // Модем SIM800

#include <TinyGsmClient.h>
#include <PubSubClient.h>

// --- Используем аппаратный Serial1 для модема ---
TinyGsm modem(Serial1);
TinyGsmClient gsmClient(modem);
PubSubClient mqtt(gsmClient);

// --- Настройки устройства и MQTT ---
const char* deviceName = "demo";
const char* broker = "empolimer.ru";
const int   port   = 1883;
const char* mqttUser = "empolimer";
const char* mqttPass = "Techno2025";
const char* clientId = "device_demo";

// --- GPRS параметры ---
const char* apn = "internet.mts.ru";
const char* gprsUser = "mts";
const char* gprsPass = "mts";

// --- Интервалы ---
const unsigned long sensorInterval    = 10000;  // опрос "датчика" (мс)
const unsigned long mqttInterval      = 30000;  // публикация MQTT (мс)
const unsigned long gprsTimeout       = 20000;  // таймаут подключения к GPRS (мс)
const unsigned long gprsRetryInterval = 20000;  // интервал переподключения (мс)

// --- Глобальные переменные ---
float cachedTemp = NAN, cachedHum = NAN;
unsigned long lastSensorRead = 0, lastMqttSend = 0;
bool dataReady = false;

// --- Состояния GPRS ---
enum GprsState { GPRS_INIT, GPRS_CONNECTING, GPRS_CONNECTED, GPRS_ERROR, GPRS_OFF };
GprsState gprsState = GPRS_INIT;
unsigned long gprsStartTime = 0, lastGprsRetry = 0;

void setup() {
  Serial.begin(9600);         // Для отладки
  Serial1.begin(9600);        // Для SIM800
  delay(1000);
  Serial.println("=== EmPolimer GSM IoT Device ===");

  modemHardReset();
  delay(2000);

  gprsConnect();
  Serial.println("Запуск основного цикла...");
}

// --- Подключение к GPRS ---
void gprsConnect() {
  Serial.println("Подключение к GPRS...");
  modem.gprsDisconnect();
  delay(1000);
  if (!modem.init()) {
    Serial.println("Модем не инициализируется (нет ответа)!");
    gprsState = GPRS_OFF;
    return;
  }
  modem.gprsConnect(apn, gprsUser, gprsPass);
  gprsState = GPRS_CONNECTING;
  gprsStartTime = millis();
}

// --- Главный цикл ---
void loop() {
  unsigned long now = millis();

  // --- Генерация "датчика" ---
  if (now - lastSensorRead >= sensorInterval) {
    lastSensorRead = now;
    cachedTemp = random(150, 300) / 10.0;  // 15.0–30.0
    cachedHum  = random(200, 800) / 10.0;  // 20.0–80.0
    dataReady = true;
  }

  // --- FSM подключения GSM/GPRS ---
  switch (gprsState) {
    case GPRS_OFF:
      if (now - lastGprsRetry > gprsRetryInterval) {
        Serial.println("Пробуем реинициализировать модем после отключения...");
        modemHardReset();
        delay(2000);
        gprsConnect();
        lastGprsRetry = now;
      }
      break;
    case GPRS_CONNECTING:
      if (modem.isGprsConnected()) {
        Serial.println("GPRS подключено!");
        gprsState = GPRS_CONNECTED;
        mqtt.setServer(broker, port);
      } else if (now - gprsStartTime > gprsTimeout) {
        Serial.println("Ошибка GPRS подключения!");
        gprsState = GPRS_ERROR;
        lastGprsRetry = now;
      }
      break;
    case GPRS_ERROR:
      if (now - lastGprsRetry > gprsRetryInterval) {
        Serial.println("Переподключение к GPRS...");
        gprsConnect();
        lastGprsRetry = now;
      }
      break;
    case GPRS_INIT:
      gprsConnect();
      break;
    case GPRS_CONNECTED:
      if (!modem.isGprsConnected()) {
        Serial.println("GPRS соединение потеряно!");
        gprsState = GPRS_ERROR;
        lastGprsRetry = now;
        break;
      }
      if (!mqtt.connected()) {
        mqttReconnect();
      }
      mqtt.loop();

      // Публикация новых данных
      if (dataReady && mqtt.connected() && (now - lastMqttSend >= mqttInterval)) {
        lastMqttSend = now;
        String dt = getFormattedGsmTime();
        String payload = "{\"datetime\":\"" + dt + "\",\"temp\":" + String(cachedTemp,1) + ",\"hum\":" + String(cachedHum,1) + "}";
        String topic = "devices/" + String(deviceName) + "/air";
        bool ok = mqtt.publish(topic.c_str(), payload.c_str());

        // Для Serial: простой формат, удобно парсить
        // Пример: 2024-06-26T18:44:15.123+00:00;23.5;53.1
        String serialLine = dt + ";" + String(cachedTemp,1) + ";" + String(cachedHum,1);
        Serial.println(serialLine);

        Serial.print("MQTT publish to ");
        Serial.print(topic);
        Serial.print(" : ");
        Serial.println(payload);
        Serial.println(ok ? "MQTT publish done" : "MQTT publish failed");
        dataReady = false;
      }

      // Статус подключения раз в 10 секунд
      static unsigned long lastStatus = 0;
      if (now - lastStatus > 10000) {
        lastStatus = now;
        Serial.print("GPRS: ");
        Serial.print(modem.isGprsConnected() ? "OK" : "FAIL");
        Serial.print(" | MQTT: ");
        Serial.println(mqtt.connected() ? "OK" : "FAIL");
      }
      break;
  }
}

// --- Подключение к MQTT ---
void mqttReconnect() {
  if (!mqtt.connected()) {
    Serial.print("MQTT reconnecting...");
    if (mqtt.connect(clientId, mqttUser, mqttPass)) {
      Serial.println("OK!");
    } else {
      Serial.print(" failed, rc=");
      Serial.print(mqtt.state());
      Serial.println(" retry next loop");
    }
  }
}

// --- Управление модемом ---
void modemHardReset() {
  // Если модуль подключён через PowerKey, здесь можно сделать полный ресет по питанию
  // Например, цифровым пином: digitalWrite(PIN_PWRKEY, LOW); delay(200); digitalWrite(PIN_PWRKEY, HIGH);
  // Здесь просто переинициализация:
  Serial.println("Полная переинициализация модема...");
  Serial1.end(); delay(1000);
  Serial1.begin(9600); delay(1000);
  modem.restart();
  modem.init();
}

// Возвращает строку UTC в формате ISO: "YYYY-MM-DDTHH:MM:SS+00:00"
String getFormattedGsmTime() {
  String response, result = "1970-01-01T00:00:00+00:00";
  modem.sendAT("+CCLK?");
  if (modem.waitResponse(1000, response) == 1) {
    int pos = response.indexOf("\"");
    int pos2 = response.indexOf("\"", pos + 1);
    if (pos >= 0 && pos2 > pos) {
      String raw = response.substring(pos + 1, pos2); // "24/06/26,21:44:15+12"
      int y = 2000 + raw.substring(0,2).toInt();
      int M = raw.substring(3,5).toInt();
      int d = raw.substring(6,8).toInt();
      int h = raw.substring(9,11).toInt();
      int m = raw.substring(12,14).toInt();
      int s = raw.substring(15,17).toInt();

      // Смещение: четверти часа (+12 = +3 часа, -08 = -2 часа)
      int tz_sign = (raw[17] == '+') ? 1 : -1;
      int tz_q = raw.substring(18, 20).toInt();
      int tz_offset_min = tz_sign * tz_q * 15;

      // --- Переводим локальное время в минуты и применяем смещение ---
      long total_min = h * 60 + m - tz_offset_min;

      // --- Корректируем часы, дни, месяцы, годы ---
      // 1. Корректируем назад по дням, если выходим за пределы суток
      while (total_min < 0) {
        total_min += 24 * 60;
        d--;
      }
      while (total_min >= 24 * 60) {
        total_min -= 24 * 60;
        d++;
      }
      h = total_min / 60;
      m = total_min % 60;

      // 2. Корректируем день, месяц, год
      const int daysInMonth[12] = {31,28,31,30,31,30,31,31,30,31,30,31};
      auto isLeap = [](int year) {
        return ((year % 4 == 0 && year % 100 != 0) || (year % 400 == 0));
      };

      // Назад по датам (например, ушли на прошлый месяц/год)
      while (d < 1) {
        M--;
        if (M < 1) {
          M = 12;
          y--;
        }
        int dim = daysInMonth[M - 1];
        if (M == 2 && isLeap(y)) dim++; // февраль
        d += dim;
      }
      // Вперёд по датам (например, превысили число дней в месяце)
      while (true) {
        int dim = daysInMonth[M - 1];
        if (M == 2 && isLeap(y)) dim++;
        if (d > dim) {
          d -= dim;
          M++;
          if (M > 12) {
            M = 1;
            y++;
          }
        } else {
          break;
        }
      }

      // --- Формируем строку ---
      char buf[30];
      sprintf(buf, "%04d-%02d-%02dT%02d:%02d:%02d+00:00", y, M, d, h, m, s);
      result = String(buf);
    }
  }
  return result;
}