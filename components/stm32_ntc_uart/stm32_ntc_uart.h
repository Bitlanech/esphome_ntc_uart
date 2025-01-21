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
  // Muss EXACT diese Signatur haben:
  //   void add_sensor(sensor::Sensor *s)
  void add_sensor(sensor::Sensor *s) {
    this->sensors_.push_back(s);
  }

  void setup() override {
    ESP_LOGI("stm32_ntc_uart", "Setup done: %d Sensoren", (int)this->sensors_.size());
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
    // Beispiel: 1 Wert für alle Sensoren
    float val = std::strtof(line.c_str(), nullptr);
    for (auto *s : sensors_) {
      s->publish_state(val);
    }
  }
};

}  // namespace stm32_ntc_uart
}  // namespace esphome
