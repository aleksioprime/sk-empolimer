#include <SPI.h>
#include <SD.h>

const int chipSelect = 10; // CS-пин SD-карты

void setup() {
  Serial.begin(9600);

  // Инициализация SD-карты
  if (!SD.begin(chipSelect)) {
    Serial.println("Ошибка SD-карты!");
    while (true); // Стоп
  }
  Serial.println("SD-карта инициализирована.");

  // Добавим заголовки, если файл ещё не существует
  if (!SD.exists("data.csv")) {
    File file = SD.open("data.csv", FILE_WRITE);
    if (file) {
      file.println("timestamp,temperature,humidity");
      file.close();
      Serial.println("Файл создан с заголовками.");
    }
  }
}

void loop() {
  // Имитация данных
  float temperature = random(200, 350) / 10.0;  // 20.0 - 35.0 °C
  float humidity = random(300, 800) / 10.0;     // 30.0 - 80.0 %
  unsigned long timestamp = millis() / 1000;    // Секунды с момента запуска

  // Открытие файла
  File file = SD.open("data.csv", FILE_WRITE);
  if (file) {
    file.print(timestamp);
    file.print(",");
    file.print(temperature, 1);
    file.print(",");
    file.println(humidity, 1);
    file.close();
    Serial.println("Данные записаны в CSV.");
  } else {
    Serial.println("Не удалось открыть файл.");
  }

  delay(5000); // Пауза 5 секунд
}
