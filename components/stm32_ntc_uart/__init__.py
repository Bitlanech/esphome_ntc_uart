import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, uart
from esphome.const import (
    CONF_ID,
    UNIT_CELSIUS,
    ICON_THERMOMETER,
    DEVICE_CLASS_TEMPERATURE,
    STATE_CLASS_MEASUREMENT,
)

# Sagt ESPHome, dass dieser Ordner eine Sensor-Plattform enthält
PLATFORMS = ["sensor"]

# Wir hängen von UART ab, weil unsere C++-Klasse 'uart::UARTDevice' nutzt
DEPENDENCIES = ["uart"]

# (Optionale) Metadaten
CODEOWNERS = ["@DeinGitHubUsername"]

# Einen C++-Namespace anlegen: esphome::stm32_ntc_uart
stm32_ntc_uart_ns = cg.esphome_ns.namespace("stm32_ntc_uart")

# Deklariere die Klasse STM32NTCUART, wie sie in stm32_ntc_uart.h heißt.
STM32NTCUART = stm32_ntc_uart_ns.class_(
    "STM32NTCUART",     # C++-Klassenname
    cg.Component,       # erbt in C++ von esphome::Component
    uart.UARTDevice,    # erbt in C++ von esphome::uart::UARTDevice
    sensor.Sensor       # erbt in C++ von esphome::sensor::Sensor
)

# YAML-Konfigschema definieren
# Hier: ein normaler Sensor (Temperatur in °C)
CONFIG_SCHEMA = sensor.sensor_schema(
    STM32NTCUART, 
    unit_of_measurement=UNIT_CELSIUS,
    icon=ICON_THERMOMETER,
    accuracy_decimals=1,
    device_class=DEVICE_CLASS_TEMPERATURE,
    state_class=STATE_CLASS_MEASUREMENT,
).extend({
    cv.GenerateID(): cv.declare_id(STM32NTCUART),  # ID für unsere Klasse
}).extend(uart.UART_DEVICE_SCHEMA)                 # Erbt Felder wie uart_id, tx_pin, rx_pin usw.

# to_code() wird aufgerufen, wenn ESPHome die C++-Instanz anlegt
def to_code(config):
    # Hole die Instanz des UART-Gerätes
    parent = yield cg.get_variable(config[uart.CONF_UART_ID])

    # Erzeuge ein C++-Objekt vom Typ STM32NTCUART
    var = cg.new_Pvariable(config[CONF_ID], parent)

    # Registrierung bei ESPHome
    cg.register_component(var, config)      # für setup()/loop()
    cg.register_uart_device(var, config)    # damit es UART nutzen darf
    sensor.register_sensor(var, config)     # damit publish_state(...) etc. funktionieren
