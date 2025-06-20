#include <Adafruit_GFX.h>
#include <Adafruit_PCD8544.h>

// Пины
#define PIN_SCE   10
#define PIN_RST   11
#define PIN_DC    6
#define PIN_DIN   5
#define PIN_SCLK  4


Adafruit_PCD8544 display = Adafruit_PCD8544(PIN_SCLK, PIN_DIN, PIN_DC, PIN_SCE, PIN_RST);

void setup() {
  display.begin();
  display.setContrast(50); // Контрастность
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(BLACK);
  display.setCursor(0,0);
  display.println("Hello, world!");
  display.display(); // Обновление дисплея
}

void loop() {
}