#include <Adafruit_NeoPixel.h>

#define LED_PIN    9
#define LED_COUNT  150

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  strip.begin();
  strip.show();
}

void loop() {
  // Перелив от красного -> фиолетового -> синего -> фиолетового -> красного
  static int step = 0;
  static int dir = 1; // направление: 1 = к синему, -1 = к красному
  static uint8_t r = 255, b = 40; // начальное (розовый-фиолетовый)

  // плавная смена цвета
  if (dir == 1) {
    if (r > 40) r--;
    if (b < 255) b++;
    if (r == 40 && b == 255) dir = -1;
  } else {
    if (r < 255) r++;
    if (b > 40) b--;
    if (r == 255 && b == 40) dir = 1;
  }

  for (uint16_t i = 0; i < LED_COUNT; i++) {
    strip.setPixelColor(i, strip.Color(r, 0, b));
  }
  strip.show();
  delay(10); // скорость переливания (меньше — быстрее)
}
