#pragma once

#include <vector>
#include <cstdlib>
#include "esphome/core/component.h"
#include "esphome/components/uart/uart.h"
#include "esphome/components/sensor/sensor.h"

namespace esphome {
namespace stm32_ntc_uart {

class STM32NTCUARTMulti : public Component,
                          public uart::UARTDevice {
 public:
  // Muss exakt "void add_sensor(sensor::Sensor *s)" sein
  void add_sensor(sensor::Sensor *s) {
    this->sensors_.push_back(s);
  }

  void setup() override {
    ESP_LOGI("stm32_ntc_uart", "Setup done, %d Sensor(en).",
             (int) this->sensors_.size());
  }

  void loop() override {
    while (this->available()) {
      char c = this->read();
      if (c == '\n') {
        process_line_(this->read_buffer_);
        this->read_buffer_.clear();
      } else {
        this->read_buffer_.push_back(c);
      }
    }
  }

 protected:
  std::string read_buffer_;
  std::vector<sensor::Sensor*> sensors_;

  void process_line_(const std::string &line) {
    if (line.empty()) {
      return;
    }
    // Beispiel: float parsen
    float val = std::strtof(line.c_str(), nullptr);

    // An alle Sub-Sensoren publishen
    for (auto *s : sensors_) {
      s->publish_state(val);
    }
  }
};

}  // namespace stm32_ntc_uart
}  // namespace esphome
