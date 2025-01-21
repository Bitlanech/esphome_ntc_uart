#pragma once

#include <vector>
#include "esphome/core/component.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/uart/uart.h"

namespace esphome {
namespace stm32_ntc_uart {

// 1) Subsensor-Klasse, erbt von sensor::Sensor
class MySubSensor : public sensor::Sensor {
 public:
  // Expliziter, parameterloser Konstruktor (ermöglicht new MySubSensor())
  MySubSensor() {
    // optional: ESP_LOGD("mysubsensor", "Konstruktor aufgerufen");
  }
};

// 2) Hauptklasse
class STM32NTCUARTMulti : public Component, public uart::UARTDevice {
 public:
  // Im Python-Code rufen wir var.add_sensor(sub_sensor)
  void add_sensor(sensor::Sensor *s) {
    this->sensors_.push_back(s);
  }

  void setup() override {
    ESP_LOGI("stm32_ntc_uart", "Setup done, %d Sub-Sensor(en).",
             (int) this->sensors_.size());
  }

  void loop() override {
    while (this->available()) {
      char c = this->read();
      if (c == '\n') {
        // parse float
        float val = std::strtof(buffer_.c_str(), nullptr);
        // Alle Sub-Sensoren erhalten diesen Wert
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
