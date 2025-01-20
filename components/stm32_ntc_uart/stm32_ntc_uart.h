#pragma once

#include "esphome/core/component.h"
#include "esphome/components/uart/uart.h"
#include "esphome/components/sensor/sensor.h"

namespace esphome {
namespace stm32_ntc_uart {

// Klassenname: STM32NTCUARTSensor (entspricht dem in sensor.py)
class STM32NTCUARTSensor : public Component,
                           public uart::UARTDevice,
                           public sensor::Sensor {
 public:
  void setup() override {
    ESP_LOGI("stm32_ntc_uart", "STM32NTCUARTSensor setup done");
  }

  void loop() override {
    // Beispiel: UART-Daten einfach einlesen
    while (this->available()) {
      char c = this->read();
      // Hier kannst du z.B. in einen Buffer schreiben und parsen
    }

    // Publish einen Dummy-Wert alle 10 Sek
    if (millis() - last_update_ > 10000) {
      last_update_ = millis();
      this->publish_state(42.0f);  // DUMMY: 42°C
    }
  }

 protected:
  unsigned long last_update_{0};
};

}  // namespace stm32_ntc_uart
}  // namespace esphome
