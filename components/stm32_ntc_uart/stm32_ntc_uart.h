#pragma once

#include <vector>
#include "esphome/core/component.h"
#include "esphome/components/uart/uart.h"
#include "esphome/components/sensor/sensor.h"

namespace esphome {
namespace stm32_ntc_uart {

class STM32NTCUARTMulti : public Component,
                          public uart::UARTDevice {
 public:
  // Muss exakt so aussehen: add_sensor(sensor::Sensor *s)
  void add_sensor(sensor::Sensor *s) {
    this->sensors_.push_back(s);
  }

  void setup() override {
    ESP_LOGI("stm32_ntc_uart", "STM32NTCUARTMulti: Setup, %d Sensor(en).",
             (int) this->sensors_.size());
  }

  void loop() override {
    while (this->available()) {
      char c = this->read();
      if (c == '\n') {
        // Beispiel: parse float
        float val = std::strtof(this->read_buffer_.c_str(), nullptr);
        // Publiziere an alle Sub-Sensoren
        for (auto *s : this->sensors_) {
          s->publish_state(val);
        }
        this->read_buffer_.clear();
      } else {
        this->read_buffer_.push_back(c);
      }
    }
  }

 protected:
  std::string read_buffer_;
  std::vector<sensor::Sensor *> sensors_;
};

}  // namespace stm32_ntc_uart
}  // namespace esphome
