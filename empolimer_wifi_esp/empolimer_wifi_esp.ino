#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// ====== WiFi и MQTT настройки ======
const char* ssid = "название WiFi-сети";
const char* password = "пароль WiFi-сети";

const char* mqtt_server = "mqtt.dealgate.ru";
const int mqtt_port = 1883;
const char* mqtt_user = "имя пользователя";
const char* mqtt_pass = "пароль пользователя";

// ====== Клиенты ======
WiFiClient espClient;
PubSubClient mqttClient(espClient);
WiFiServer server(80);

// ====== Последние данные от Arduino ======
String latestTemp = "-";
String latestHum = "-";

// ====== Настройка подключения ======
void setup() {
  Serial.begin(9600);  // Связь с Arduino UNO по UART

  // Подключение к Wi-Fi
  WiFi.begin(ssid, password);
  Serial.println("Подключение к WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi подключен. IP: " + WiFi.localIP().toString());

  // Настройка MQTT
  mqttClient.setServer(mqtt_server, mqtt_port);

  // Запуск веб-сервера
  server.begin();
}

// ====== Переподключение к MQTT при необходимости ======
void reconnect() {
  while (!mqttClient.connected()) {
    if (mqttClient.connect("ESP8266Client", mqtt_user, mqtt_pass)) {
      Serial.println("MQTT подключен");
    } else {
      Serial.print("Ошибка MQTT: ");
      Serial.println(mqttClient.state());
      delay(5000);
    }
  }
}

// ====== Главный цикл ======
void loop() {
  // Поддержка MQTT-соединения
  if (!mqttClient.connected()) reconnect();
  mqttClient.loop();

  // Чтение данных от Arduino
  while (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();

    // Пример строки: temp:25.4
    int sep = line.indexOf(':');
    if (sep > 0) {
      String key = line.substring(0, sep);
      String value = line.substring(sep + 1);

      // Обновляем переменные и отправляем в MQTT
      if (key == "temp") latestTemp = value;
      else if (key == "hum") latestHum = value;

      String topic = "arduino/" + key;
      mqttClient.publish(topic.c_str(), value.c_str());
      Serial.println("MQTT → " + topic + ": " + value);
    }
  }

  // Обработка HTTP-запросов
  WiFiClient client = server.available();
  if (client) {
    while (client.connected()) {
      if (client.available()) {
        String req = "";
        while (client.available()) {
          char c = client.read();
          req += c;
          if (req.endsWith("\r\n\r\n")) break;
        }

        // JSON-ответ
        if (req.indexOf("GET /data") >= 0) {
          String json = "{\"temp\":\"" + latestTemp + "\",\"hum\":\"" + latestHum + "\"}";
          client.println("HTTP/1.1 200 OK");
          client.println("Content-Type: application/json");
          client.println("Connection: close");
          client.println();
          client.println(json);
          delay(1);  // важный короткий таймер для отправки!
          client.stop();
          return;
        }

        // HTML-страница
        String html = generateHTMLPage();
        client.println("HTTP/1.1 200 OK");
        client.println("Content-Type: text/html");
        client.println("Connection: close");
        client.println();
        client.println(html);
        delay(1);  // важный короткий таймер
        client.stop();
        return;
      }
    }
  }
}

// ====== Функция генерации HTML-страницы ======
String generateHTMLPage() {
  String html;
  html += "<!DOCTYPE html><html><head><meta charset='UTF-8'><title>ЕмПолимер: микроклимат</title></head>";
  html += "<body style='font-family:sans-serif;text-align:center;margin-top:50px'>";
  html += "<h1>Данные микроклимата ЕмПолимер</h1>";
  html += "<p><strong>Температура:</strong> <span id='temp'>...</span> °C</p>";
  html += "<p><strong>Влажность:</strong> <span id='hum'>...</span> %</p>";
  html += "<script>";
  html += "function update() {";
  html += "  fetch('/data').then(r => r.json()).then(d => {";
  html += "    document.getElementById('temp').innerText = d.temp;";
  html += "    document.getElementById('hum').innerText = d.hum;";
  html += "  });";
  html += "}";
  html += "setInterval(update, 3000); update();";
  html += "</script>";
  html += "</body></html>";
  return html;
}
