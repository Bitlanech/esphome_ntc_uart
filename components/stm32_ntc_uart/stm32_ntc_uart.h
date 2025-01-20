/*#ifndef STM32_NTC_UART_H
#define STM32_NTC_UART_H

#include "esphome.h"

namespace esphome {
namespace stm32_ntc_uart {

class STM32NTCUART : public Component, public UARTDevice {
public:
  STM32NTCUART(UARTComponent *parent) : UARTDevice(parent) {}

  void setup() override {
    // Setup, falls nötig
  }

  void loop() override {
    if (available()) {
      std::string data = readStringUntil('\n');
      process_data(data);
    }
  }

private:
  void process_data(const std::string &data) {
    // Daten verarbeiten (CSV-Parsing)
    std::vector<float> temperatures;
    size_t start = 0;
    size_t end = data.find(',');

    while (end != std::string::npos) {
      temperatures.push_back(std::stof(data.substr(start, end - start)));
      start = end + 1;
      end = data.find(',', start);
    }
    if (start < data.size()) {
      temperatures.push_back(std::stof(data.substr(start)));
    }

    for (size_t i = 0; i < temperatures.size(); ++i) {
      ESP_LOGD("STM32NTCUART", "Sensor %d: %.2f °C", i + 1, temperatures[i]);
    }
  }
};

}
}

#endif
*/

#pragma once

#include "esphome/core/component.h"
#include "esphome/components/uart/uart.h"
#include "esphome/components/sensor/sensor.h"

// Wir definieren einen Namespace, damit ESPHome-Codegen dich findet:
namespace esphome {
namespace stm32_ntc_uart {

class STM32NTCUART : public Component,      // Komponente, damit setup()/loop() aufgerufen werden
                     public uart::UARTDevice, // UART-„Abhängigkeit“ in ESPHome
                     public sensor::Sensor    // Wir verhalten uns wie ein einzelner Sensor
{
 public:
  // Konstruktor bekommt das UART-Objekt
  explicit STM32NTCUART(uart::UARTComponent *parent) : UARTDevice(parent) {}

  void setup() override {
    // Falls du bei Start noch init-Code brauchst ...
  }

  void loop() override {
    // Hier liest du z. B. zeilenweise von UART
    while (this->available()) {
      char c = this->read();
      if (c == '\n') {
        // Zeile parsen → float-Wert
        float value = parse_line_(buffer_);
        // Sensor-Messwert veröffentlichen
        this->publish_state(value);
        // Puffer zurücksetzen
        buffer_.clear();
      } else {
        buffer_.push_back(c);
      }
    }
  }

 protected:
  // Beispiel: Minimale Funktion, um aus dem empfangenen String (buffer_) eine Zahl zu generieren
  float parse_line_(const std::string &line) {
    // Dein Parser. Hier nur Fake: immer 21.5
    return 21.5f; 
  }

  // Wir sammeln hier Zeichen bis zum nächsten \n
  std::string buffer_;
};

}  // namespace stm32_ntc_uart
}  // namespace esphome
