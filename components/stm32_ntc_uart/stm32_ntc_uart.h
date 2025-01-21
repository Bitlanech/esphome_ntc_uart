#pragma once

#include <vector>
#include <cstdlib>  // strtof
#include "esphome/core/component.h"
#include "esphome/components/uart/uart.h"
#include "esphome/components/sensor/sensor.h"

namespace esphome {
namespace stm32_ntc_uart {

// 1. Sub-Sensor-Klasse, erbt von sensor::Sensor
class MySubSensor : public sensor::Sensor {
 public:
  // Parameterloser Konstruktor
  MySubSensor() {
    // Optional: Initialisierung oder Logging
    // ESP_LOGD("mysubsensor", "MySubSensor Konstruktor aufgerufen");
  }
};

// 2. Hauptklasse zur Verwaltung mehrerer Sub-Sensoren
class STM32NTCUARTMulti : public Component, public uart::UARTDevice {
 public:
  // Methode zum Hinzufügen von Sub-Sensoren
  void add_sensor(sensor::Sensor *s) {
    this->sensors_.push_back(s);
  }

  void setup() override {
    ESP_LOGI("stm32_ntc_uart", "Setup done. Anzahl Sensoren: %d",
             (int)this->sensors_.size());
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
  std::vector<sensor::Sensor *> sensors_;

  // Funktion zum Verarbeiten der empfangenen Zeile
  void process_line_(const std::string &line) {
    if (line.empty()) {
      ESP_LOGW("stm32_ntc_uart", "Leere Zeile empfangen, ignorieren.");
      return;
    }

    // Zeile an Semikolon trennen
    std::vector<std::string> tokens;
    size_t start = 0;
    while (true) {
      size_t pos = line.find(';', start);
      if (pos == std::string::npos) {
        tokens.push_back(line.substr(start));
        break;
      } else {
        tokens.push_back(line.substr(start, pos - start));
        start = pos + 1;
      }
    }

    // Anzahl der zu verarbeitenden Sensoren
    size_t count = std::min(tokens.size(), sensors_.size());

    for (size_t i = 0; i < count; i++) {
      float value;
      if (parse_float_(tokens[i], value)) {
        ESP_LOGD("stm32_ntc_uart", "Sensor #%d: %.2f (Token: '%s')",
                 (int)(i + 1), value, tokens[i].c_str());
        sensors_[i]->publish_state(value);
      } else {
        ESP_LOGW("stm32_ntc_uart", "Fehler beim Parsen von '%s' (Sensor %d)",
                 tokens[i].c_str(), (int)(i + 1));
      }
    }

    // Überzählige Tokens ignorieren
  }

  // Hilfsfunktion zum Parsen eines Floats ohne Exceptions
  bool parse_float_(const std::string &raw, float &out_val) {
    // Unerwünschte Zeichen entfernen
    std::string sanitized;
    sanitized.reserve(raw.size());
    for (char c : raw) {
      if ((c >= '0' && c <= '9') || c == '.' || c == '+' || c == '-')
        sanitized.push_back(c);
    }
    if (sanitized.empty()) {
      return false;
    }

    // strtof zum Parsen verwenden
    char *endptr = nullptr;
    float val = std::strtof(sanitized.c_str(), &endptr);
    if (endptr == sanitized.c_str()) {
      // Keine gültige Zahl geparst
      return false;
    }
    out_val = val;
    return true;
  }
};

}  // namespace stm32_ntc_uart
}  // namespace esphome
