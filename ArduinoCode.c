#include <Adafruit_NeoPixel.h>

#define LED_COUNT 60
#define LED_PIN 6

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  Serial.begin(9600);
  strip.begin();
  strip.show();
}

void loop() {
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    if (data == "0") {
      strip.clear();
      strip.show();
      Serial.println("All LEDs turned off");
    } else {
      int led_num_end = data.indexOf('-');
      int color_start_index = led_num_end + 1;
      String led_nums_str = data.substring(0, led_num_end);
      char color = data[color_start_index];
      turn_on_leds(led_nums_str, color);
    }
  }
}

void turn_on_leds(String led_nums_str, char color) {
  // Parse comma-separated LED numbers
  int comma_index = -1;
  while ((comma_index = led_nums_str.indexOf(',')) != -1) {
    int led_num = led_nums_str.substring(0, comma_index).toInt() - 1;
    turn_on_led(led_num, color);
    led_nums_str = led_nums_str.substring(comma_index + 1);
  }

  // Turn on the last LED
  int last_led_num = led_nums_str.toInt() - 1;
  turn_on_led(last_led_num, color);
}

void turn_on_led(int led_num, char color) {
  // Set the LED color based on the color code
  uint32_t led_color;
  switch (color) {
    case 'R': led_color = strip.Color(255, 0, 0); break;  // Red
    case 'G': led_color = strip.Color(0, 255, 0); break;  // Green
    case 'Y': led_color = strip.Color(255, 255, 0); break;  // Yellow
    case 'B': led_color = strip.Color(0, 0, 255); break;  // Blue
    default: led_color = strip.Color(0, 0, 0); break;  // Off
  }

  // Turn on the LED with the specified color
  strip.setPixelColor(led_num, led_color);
  strip.show();

  // Send information back to Python
  String message = "Turned on LED " + String(led_num + 1) + " with color " + color;
  Serial.println(message);
}
