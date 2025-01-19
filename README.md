# STM32 NTC UART Component

Diese ESPHome-Komponente liest Temperaturdaten über UART und verarbeitet diese.

## Verzeichnisstruktur
- `stm32_ntc_uart.h`: Header-Datei mit der Definition der Klasse `STM32NTCUART`.
- `stm32_ntc_uart.cpp`: Implementierung der Klasse (aktuell keine weiteren Inhalte).

## Verwendung
Fügen Sie Folgendes zu Ihrer `esphome.yaml` hinzu:
```yaml
external_components:
  - source:
      type: git
      url: https://github.com/USERNAME/stm32_ntc_uart_component
uart:
  - id: uart_bus
    tx_pin: TX_PIN
    rx_pin: RX_PIN
    baud_rate: 9600

custom_component:
  - lambda: |-
      auto my_uart = new STM32NTCUART(id(uart_bus));
      App.register_component(my_uart);
