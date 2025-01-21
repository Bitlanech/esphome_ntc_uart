#pragma once

#include <vector>
#include <cstdlib>
#include "esphome/core/component.h"
#include "esphome/components/uart/uart.h"
#include "esphome/components/sensor/sensor.h"

namespace esphome {
namespace stm32_ntc_uart {

// 1) Sub-Sensor-Klasse (erbt von sensor::Sensor)
class MySubSensor : public sensor::Sensor {
 public:
  // Expliziter, parameterloser Konstruktor (Verhinderung von Codegen-Bugs)
  MySubSensor() {
    // Optional: Logging oder Initialisierung
    // ESP_LOGD("mysubsensor", "MySubSensor() Konstruktor aufgerufen");
  }
};

// 2) Die Multi-Klasse, die Sub-Sensoren verwaltet
class STM32NTCUARTMulti : public Component, public uart::UARTDevice {
 public:
  // Diesen Funktionskopf muss Python kennen:  void add_sensor(sensor::Sensor *s)
  void add_sensor(sensor::Sensor *s) {
    this->sensors_.push_back(s);
  }

  void setup() override {
    ESP_LOGI("stm32_ntc_uart", "Setup done: %d Sub-Sensor(en)", (int)sensors_.size());
  }

  void loop() override {
    // Beispiel: bis \n einlesen
    while (this->available()) {
      char c = this->read();
      if (c == '\n') {
        // parse float
        float val = std::strtof(buffer_.c_str(), nullptr);
        // an alle Sub-Sensoren ausgeben
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
