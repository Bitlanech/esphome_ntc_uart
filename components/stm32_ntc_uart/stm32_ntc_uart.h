#pragma once

#include <vector>
#include <cstdlib>  // strtof
#include "esphome/core/component.h"
#include "esphome/components/uart/uart.h"
#include "esphome/components/sensor/sensor.h"

namespace esphome {
namespace stm32_ntc_uart {

class STM32NTCUARTMulti : public Component,
                          public uart::UARTDevice {
 public:
  /// Wird von der Python-Seite via var.add_sensor(...) aufgerufen.
  void add_sensor(sensor::Sensor *s) {
    this->sensors_.push_back(s);
  }

  void setup() override {
    ESP_LOGI("stm32_ntc_uart", "STM32NTCUARTMulti setup done with %d sensor(s).",
             (int)this->sensors_.size());
  }

  void loop() override {
    // UART-Daten sammeln, bis wir ein Newline finden.
    while (this->available()) {
      char c = this->read();
      if (c == '\n') {
        // Zeile fertig -> parsende Logik
        process_line_(this->read_buffer_);
        this->read_buffer_.clear();
      } else {
        this->read_buffer_.push_back(c);
      }
    }
  }

 protected:
  std::string read_buffer_;
  // Hier werden die Sensoren gespeichert, die via add_sensor() hinzugefügt wurden.
  std::vector<sensor::Sensor *> sensors_;

  void process_line_(const std::string &line) {
    if (line.empty()) {
      ESP_LOGW("stm32_ntc_uart", "Leere Zeile empfangen, ignoriere...");
      return;
    }

    // 1) Zeile in Token zerlegen, getrennt durch Semikolon (;).
    std::vector<std::string> tokens;
    {
      size_t start = 0;
      while (true) {
        size_t pos = line.find(';', start);
        if (pos == std::string::npos) {
          // letztes Token
          tokens.push_back(line.substr(start));
          break;
        } else {
          tokens.push_back(line.substr(start, pos - start));
          start = pos + 1;
        }
      }
    }

    // 2) Wir haben tokens.size() Werte, z.B. ["23.4", "25.0", "99.9", ...]
    //    Wir haben sensors_.size() Sensoren. Verarbeiten wir min(tokens.size(), sensors_.size()).
    size_t count = std::min(tokens.size(), sensors_.size());
    for (size_t i = 0; i < count; i++) {
      float value;
      if (this->parse_float_(tokens[i], value)) {
        ESP_LOGD("stm32_ntc_uart", "Sensor %d: %.2f (Token '%s')", 
                 (int) i+1, value, tokens[i].c_str());
        sensors_[i]->publish_state(value);
      } else {
        ESP_LOGW("stm32_ntc_uart", "Fehler beim Parsen von '%s' (Sensor %d)",
                 tokens[i].c_str(), (int) i+1);
      }
    }

    // Falls mehr Tokens als Sensoren existieren, ignorieren wir einfach die restlichen.
    // Falls weniger Tokens als Sensoren, dann bekommen die restlichen Sensoren diesmal keinen Wert.
  }

  // Hilfsfunktion zum Parsen eines Floats ohne Exceptions
  bool parse_float_(const std::string &raw, float &out_value) {
    // 1) "Säubern": Nur [0-9], +, -, '.' erlaubt
    std::string sanitized;
    sanitized.reserve(raw.size());
    for (char c : raw) {
      if ((c >= '0' && c <= '9') || c == '.' || c == '+' || c == '-')
        sanitized.push_back(c);
    }
    if (sanitized.empty()) {
      return false;
    }

    // 2) strtof
    char *endptr = nullptr;
    float val = std::strtof(sanitized.c_str(), &endptr);
    if (endptr == sanitized.c_str()) {
      // Keine gültige Zahl geparst
      return false;
    }
    out_value = val;
    return true;
  }
};

}  // namespace stm32_ntc_uart
}  // namespace esphome
