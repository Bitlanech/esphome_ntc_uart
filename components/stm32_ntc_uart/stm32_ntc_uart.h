#pragma once

#include <vector>
#include <cstdlib>  // strtof
#include "esphome/core/component.h"
#include "esphome/components/uart/uart.h"
#include "esphome/components/sensor/sensor.h"

namespace esphome {
namespace stm32_ntc_uart {

class STM32NTCUARTMulti : public Component,
                          public uart::UARTDevice {
 public:
  // Muss genau so sein: void add_sensor(sensor::Sensor *s)
  void add_sensor(sensor::Sensor *s) {
    this->sensors_.push_back(s);
  }

  void setup() override {
    ESP_LOGI("stm32_ntc_uart", "Setup done, habe %d Sensor(en).",
             (int) this->sensors_.size());
  }

  void loop() override {
    // UART-Daten einsammeln
    while (this->available()) {
      char c = this->read();
      if (c == '\n') {
        // Beispiel: parse float
        float val = std::strtof(this->buffer_.c_str(), nullptr);
        // Veröffentliche an alle Sensoren
        for (auto *sens : sensors_) {
          sens->publish_state(val);
        }
        this->buffer_.clear();
      } else {
        this->buffer_.push_back(c);
      }
    }
  }

 protected:
  std::string buffer_;
  std::vector<sensor::Sensor *> sensors_;
};

}  // namespace stm32_ntc_uart
}  // namespace esphome
