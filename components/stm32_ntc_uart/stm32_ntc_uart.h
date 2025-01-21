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
  void add_sensor(sensor::Sensor *s) {
    this->sensors_.push_back(s);
  }

  void setup() override {
    ESP_LOGI("stm32_ntc_uart", "Setup done, habe %d Sensor(en).",
             (int) this->sensors_.size());
  }

  void loop() override {
    while (this->available()) {
      char c = this->read();
      if (c == '\n') {
        // z. B. parse float und an alle Sub-Sensoren senden
        float val = std::strtof(this->read_buffer_.c_str(), nullptr);
        for (auto *sens : this->sensors_) {
          sens->publish_state(val);
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
