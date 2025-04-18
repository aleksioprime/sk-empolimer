#include <SPI.h>               // Библиотека для SPI (нужна для дисплея)
#include <Adafruit_GFX.h>      // Графическая библиотека от Adafruit
#include <Adafruit_PCD8544.h>  // Библиотека для дисплея Nokia 5110
#include <DHT.h>               // Библиотека для работы с датчиком DHT11
#include <SoftwareSerial.h>    // Библиотека для виртуального (программного) порта

// --- Настройки дисплея Nokia 5110 ---
// Подключение дисплея: (CLK, DIN, D/C, CS, RST)
Adafruit_PCD8544 display = Adafruit_PCD8544(7, 6, 5, 4, 3);

// --- Настройки датчика DHT11 ---
#define DHTPIN  A0           // Пин, к которому подключён DHT11
#define DHTTYPE DHT11        // Используем именно DHT11
DHT dht11(DHTPIN, DHTTYPE);  // Создание объекта датчика

// --- Переменные для отображения ---
char temperature[] = "00.0 C";
char humidity[]    = "00.0 %";

// --- Настройки виртуального порта для связи с ESP ---
#define ESP_RX 8  // Arduino получает данные от ESP (ESP TX)
#define ESP_TX 9  // Arduino отправляет данные в ESP (ESP RX)
SoftwareSerial esp(ESP_RX, ESP_TX); // Создаём SoftwareSerial

// --- Таймер для отправки данных на ESP ---
unsigned long lastSend = 0;
const unsigned long sendInterval = 3000;  // Интервал отправки: 3 секунды

void setup() {
  delay(1000);  // Ждём старта платы

  // --- Инициализация дисплея ---
  display.begin();             // Инициализация дисплея
  display.setContrast(50);     // Настройка контрастности
  display.clearDisplay();      // Очистка экрана

  // --- Отрисовка статичного интерфейса ---
  display.drawFastHLine(0, 23, display.width(), BLACK); // Горизонтальная линия
  display.setTextSize(1);
  display.setTextColor(BLACK, WHITE);
  display.setCursor(6, 0);
  display.print("TEMPERATURE:");
  display.setCursor(15, 28);
  display.print("HUMIDITY:");
  display.display(); // Обновление экрана

  // --- Инициализация DHT11 ---
  dht11.begin();

  // --- Инициализация портов ---
  Serial.begin(9600);  // Основной порт для отладки
  esp.begin(9600);     // Виртуальный порт для ESP
}

void loop() {
  // --- Чтение данных с датчика ---
  byte RH = dht11.readHumidity();        // Влажность (целое значение)
  byte Temp = dht11.readTemperature();   // Температура (целое значение)

  // --- Обновление массивов символов для дисплея ---
  temperature[0] = Temp / 10 + '0';
  temperature[1] = Temp % 10 + '0';
  humidity[0]    = RH   / 10 + '0';
  humidity[1]    = RH   % 10 + '0';

  // --- Отображение температуры на дисплее ---
  display.setCursor(24, 12);
  display.print(temperature);

  // --- Отображение влажности на дисплее ---
  display.setCursor(24, 40);
  display.print(humidity);

  // --- Рисуем символ "градусы" (°) как квадрат 3x3 пикселя ---
  display.drawRect(50, 12, 3, 3, BLACK);

  // --- Обновляем дисплей ---
  display.display();

  // --- Отправка данных на ESP раз в 3 секунды ---
  unsigned long currentMillis = millis();
  if (currentMillis - lastSend >= sendInterval) {
    lastSend = currentMillis;

    // --- Формирование строк ---
    String tempStr = "temp:" + String(Temp);  // Без дробей, так как DHT11 — целые значения
    String humStr = "hum:" + String(RH);

    // --- Отладочный вывод в Serial Monitor ---
    Serial.print("Отправка в ESP: ");
    Serial.print(tempStr);
    Serial.print(", ");
    Serial.println(humStr);

    // --- Отправка данных в ESP через виртуальный порт ---
    esp.println(tempStr);
    delay(10); // Небольшая задержка для стабильности
    esp.println(humStr);
  }

  delay(1000); // Пауза между обновлениями дисплея
}
