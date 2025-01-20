#pragma once

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
    // Zeichen vom UART sammeln
    while (this->available()) {
      char c = this->read();
      if (c == '\n') {
        // Zeilenende -> verarbeiten
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
      ESP_LOGW("stm32_ntc_uart", "Empfangene Zeile ist leer, wird ignoriert.");
      return;
    }

    // Nur den Teil vor dem ersten Komma verwenden
    // Beispiel: "25.4,blabla" -> wir interpretieren nur "25.4" als Float
    auto pos = line.find(',');
    std::string first_value_str;
    if (pos == std::string::npos) {
      // Kein Komma in der Zeile -> gesamte Zeile als Wert
      first_value_str = line;
    } else {
      // Substring von Anfang bis Komma
      first_value_str = line.substr(0, pos);
    }

    // Jetzt versuchen, das als Float zu interpretieren
    try {
      float value = std::stof(first_value_str);
      ESP_LOGD("stm32_ntc_uart", "Erster Temperaturwert: %.2f °C", value);
      this->publish_state(value);
    } catch (...) {
      ESP_LOGW("stm32_ntc_uart", "Fehler beim Parsen von '%s' als float", first_value_str.c_str());
    }

    // Alles hinter dem ersten Komma bleibt unberücksichtigt.
  }
};

}  // namespace stm32_ntc_uart
}  // namespace esphome
