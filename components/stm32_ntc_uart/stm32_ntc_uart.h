#ifndef STM32_NTC_UART_H
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