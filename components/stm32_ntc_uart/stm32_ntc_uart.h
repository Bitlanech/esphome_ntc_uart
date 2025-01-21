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
  /// Aus Python-Seite: var.add_sensor(...)
  void add_sensor(sensor::Sensor *s) {
    this->sensors_.push_back(s);
  }

  void setup() override {
    ESP_LOGI("stm32_ntc_uart", "Setup done. Anzahl Sensoren: %d",
             (int) this->sensors_.size());
  }

  void loop() override {
    // UART-Daten sammeln, bis zum Newline
    while (this->available()) {
      char c = this->read();
      if (c == '\n') {
        // Zeile fertig -> verarbeiten
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

  /// Diese Funktion zerlegt den Zeileninhalt an Semikolon
  /// und verteilt die Werte auf die Sensoren.
  void process_line_(const std::string &line) {
    if (line.empty()) {
      ESP_LOGW("stm32_ntc_uart", "Leere Zeile empfangen, ignorieren.");
      return;
    }

    // 1) Zerlege 'line' an jedem ';'
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

    // 2) Wir verarbeiten minimal(tokens.size(), sensors_.size())
    //    d.h. wenn mehr Tokens als Sensoren vorhanden sind, wird der Rest ignoriert
    size_t count = std::min(tokens.size(), sensors_.size());

    for (size_t i = 0; i < count; i++) {
      float value;
      // parse_float_() wandelt den String in float um (ohne Exceptions)
      if (this->parse_float_(tokens[i], value)) {
        ESP_LOGD("stm32_ntc_uart", "Sensor #%d: %.2f (Token: '%s')",
                 (int)i + 1, value, tokens[i].c_str());
        // Wert an den i-ten Sub-Sensor
        sensors_[i]->publish_state(value);
      } else {
        ESP_LOGW("stm32_ntc_uart",
                 "Fehler beim Parsen von '%s' (Sensor %d)",
                 tokens[i].c_str(), (int)i + 1);
      }
    }
  }

  /// Hilfsfunktion: Verwandelt einen String in float (strtof),
  /// entfernt vorab unbrauchbare Zeichen.
  bool parse_float_(const std::string &raw, float &out_val) {
    // a) Unerwünschte Zeichen entfernen
    std::string sanitized;
    sanitized.reserve(raw.size());
    for (char c : raw) {
      if ((c >= '0' && c <= '9') || c == '.' || c == '+' || c == '-') {
        sanitized.push_back(c);
      }
    }
    if (sanitized.empty()) {
      return false;
    }

    // b) strtof
    char *endptr = nullptr;
    float val = std::strtof(sanitized.c_str(), &endptr);
    if (endptr == sanitized.c_str()) {
      // Keine gültige Zahl gelesen
      return false;
    }

    out_val = val;
    return true;
  }
};

}  // namespace stm32_ntc_uart
}  // namespace esphome
