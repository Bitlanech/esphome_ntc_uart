#pragma once

#include <cstdlib>  // Für strtof
#include "esphome/core/component.h"
#include "esphome/components/uart/uart.h"
#include "esphome/components/sensor/sensor.h"

namespace esphome {
namespace stm32_ntc_uart {

class STM32NTCUARTSensor : public Component,
                           public uart::UARTDevice,
                           public sensor::Sensor {
 public:
  void setup() override {
    ESP_LOGI("stm32_ntc_uart", "STM32NTCUARTSensor setup done");
  }

  void loop() override {
    // UART-Daten sammeln
    while (this->available()) {
      char c = this->read();
      if (c == '\n') {
        // Zeilenende -> Zeile verarbeiten
        process_line_(read_buffer_);
        read_buffer_.clear();
      } else {
        read_buffer_.push_back(c);
      }
    }
  }

 protected:
  std::string read_buffer_;

  void process_line_(const std::string &line) {
    if (line.empty()) {
      ESP_LOGW("stm32_ntc_uart", "Leere Zeile, nichts zu parsen.");
      return;
    }

    // Beispiel: nimm nur den Teil vor dem ersten Komma
    auto pos = line.find(',');
    std::string first_value_str;
    if (pos == std::string::npos) {
      first_value_str = line;
    } else {
      first_value_str = line.substr(0, pos);
    }

    // Parsen ohne Exceptions
    bool success;
    float value = parse_float_(first_value_str, &success);
    if (!success) {
      ESP_LOGW("stm32_ntc_uart", "Fehler beim Parsen von '%s' als float", first_value_str.c_str());
      return;
    }

    // Falls alles gut: publish
    ESP_LOGD("stm32_ntc_uart", "Erster Wert: %.2f °C", value);
    this->publish_state(value);
  }

  /// Hilfsfunktion: Parst 'str' via strtof. Gibt via *ok=true zurück, wenn es geklappt hat.
  float parse_float_(const std::string &str, bool *ok) {
    // strtof bricht beim ersten ungültigen Zeichen ab
    // endptr zeigt dann auf die Stelle, ab der nicht mehr geparsed werden konnte
    char *endptr = nullptr;
    float val = std::strtof(str.c_str(), &endptr);

    // endptr == str.c_str() -> Keine gültige Zahl geparst
    if (endptr == str.c_str()) {
      *ok = false;
    } else {
      *ok = true;
    }
    return val;
  }
};

}  // namespace stm32_ntc_uart
}  // namespace esphome
