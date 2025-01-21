#pragma once

#include <vector>
#include "esphome/core/component.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/uart/uart.h"

namespace esphome {
namespace stm32_ntc_uart {

// 1) Abgeleitete Klasse MySubSensor
//    Sie hat implizit einen Standardkonstruktor und erbt von sensor::Sensor.
class MySubSensor : public sensor::Sensor {
 public:
  // Leer oder custom code
};

// 2) Hauptklasse: Speichert Sub-Sensoren
class STM32NTCUARTMulti : public Component,
                          public uart::UARTDevice {
 public:
  void add_sensor(sensor::Sensor *s) {
    this->sensors_.push_back(s);
  }

  void setup() override {
    ESP_LOGI("stm32_ntc_uart", "Setup done, %d Sub-Sensor(en).",
             (int) this->sensors_.size());
  }

  void loop() override {
    // Beispiel: Empfange UART, parse float
    while (this->available()) {
      char c = this->read();
      if (c == '\n') {
        float val = std::strtof(buffer_.c_str(), nullptr);
        // Alle Sub-Sensoren mit dem Wert updaten
        for (auto *sens : sensors_) {
          sens->publish_state(val);
        }
        buffer_.clear();
      } else {
        buffer_.push_back(c);
      }
    }
  }

 protected:
  std::string buffer_;
  std::vector<sensor::Sensor *> sensors_;
};

}  // namespace stm32_ntc_uart
}  // namespace esphome
