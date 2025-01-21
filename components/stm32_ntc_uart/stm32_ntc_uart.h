#pragma once

#include <cstdlib>  // strtof
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
    // UART-Daten Zeichen für Zeichen einlesen
    while (this->available()) {
      char c = this->read();
      // Zeilenende erkannt -> gesamte Zeile verarbeiten
      if (c == '\n') {
        process_line_(read_buffer_);
        read_buffer_.clear();
      } else {
        // Sonst Zeichen an den Puffer hängen
        read_buffer_.push_back(c);
      }
    }
  }

 protected:
  std::string read_buffer_;

  /// Zeile verarbeiten
  void process_line_(const std::string &line) {
    if (line.empty()) {
      ESP_LOGW("stm32_ntc_uart", "Leere Zeile, nichts zu parsen.");
      return;
    }

    // 1) Nur den Teil bis zum ersten Komma herausziehen – falls kein Komma existiert, nimm die ganze Zeile
    auto pos = line.find(',');
    std::string raw_value_str =
        (pos == std::string::npos) ? line : line.substr(0, pos);

    // 2) Säubere den String von Zeichen, die nicht zum Float-Parsing gehören
    //    Erlaubt sind nur Ziffern, +, -, und '.'
    std::string sanitized;
    sanitized.reserve(raw_value_str.size());
    for (char c : raw_value_str) {
      if ((c >= '0' && c <= '9') || c == '.' || c == '+' || c == '-') {
        sanitized.push_back(c);
      }
    }

    if (sanitized.empty()) {
      ESP_LOGW("stm32_ntc_uart", "Kein Zahlenwert in '%s'", raw_value_str.c_str());
      return;
    }

    // 3) Versuche, den bereinigten String als Float zu interpretieren
    char *endptr = nullptr;
    float value = std::strtof(sanitized.c_str(), &endptr);

    // endptr == sanitized.c_str() bedeutet, dass keine gültige Zahl geparst wurde
    if (endptr == sanitized.c_str()) {
      ESP_LOGW("stm32_ntc_uart", "Fehler beim Parsen von '%s' als float", sanitized.c_str());
      return;
    }

    // 4) Wert veröffentlichen
    ESP_LOGD("stm32_ntc_uart", "Gelesener Wert: %.2f °C (ganze Zeile: '%s')", value, line.c_str());
    this->publish_state(value);
  }
};

}  // namespace stm32_ntc_uart
}  // namespace esphome
