stm32_ntc_uart.h:
#pragma once

#include <cstdlib>  // strtof
#include <vector>
#include "esphome/core/component.h"
#include "esphome/components/uart/uart.h"
#include "esphome/components/sensor/sensor.h"

namespace esphome {
namespace stm32_ntc_uart {

class STM32NTCUARTSensor : public Component,
                           public uart::UARTDevice {
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

  void add_sensor(sensor::Sensor *sensor) {
    sensors_.push_back(sensor);
  }

 protected:
  std::string read_buffer_;
  std::vector<sensor::Sensor *> sensors_;

  /// Zeile verarbeiten
  void process_line_(const std::string &line) {
    if (line.empty()) {
      ESP_LOGW("stm32_ntc_uart", "Leere Zeile, nichts zu parsen.");
      return;
    }

    // CSV-Zeile in Werte aufteilen
    size_t start = 0;
    size_t end = 0;
    size_t sensor_index = 0;

    while ((end = line.find(';', start)) != std::string::npos) {
      if (sensor_index >= sensors_.size()) {
        ESP_LOGW("stm32_ntc_uart", "Mehr Werte als Sensoren vorhanden.");
        break;
      }

      publish_sensor_value(line.substr(start, end - start), sensor_index);
      start = end + 1;
      sensor_index++;
    }

    // Letzter Wert (nach dem letzten Semikolon)
    if (sensor_index < sensors_.size()) {
      publish_sensor_value(line.substr(start), sensor_index);
    }
  }

  void publish_sensor_value(const std::string &raw_value_str, size_t index) {
    // Bereinigen und in Float konvertieren
    std::string sanitized;
    for (char c : raw_value_str) {
      if ((c >= '0' && c <= '9') || c == '.' || c == '+' || c == '-') {
        sanitized.push_back(c);
      }
    }

    if (sanitized.empty()) {
      ESP_LOGW("stm32_ntc_uart", "Kein Zahlenwert in '%s'", raw_value_str.c_str());
      return;
    }

    char *endptr = nullptr;
    float value = std::strtof(sanitized.c_str(), &endptr);
    if (endptr == sanitized.c_str()) {
      ESP_LOGW("stm32_ntc_uart", "Fehler beim Parsen von '%s' als float", sanitized.c_str());
      return;
    }

    // Wert veröffentlichen
    if (index < sensors_.size() && sensors_[index] != nullptr) {
      ESP_LOGD("stm32_ntc_uart", "Sensor %d: %.2f °C", index, value);
      sensors_[index]->publish_state(value);
    }
  }
};

}  // namespace stm32_ntc_uart
}  // namespace esphome
