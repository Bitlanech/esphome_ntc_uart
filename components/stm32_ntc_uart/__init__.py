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

CODEOWNERS = ["@Bitlanch"]  # optional
DEPENDENCIES = ["uart"]           # Wir brauchen den UART

# Erzeuge einen Namespace "stm32_ntc_uart" in esphome
stm32_ntc_uart_ns = cg.esphome_ns.namespace("stm32_ntc_uart")

# Die C++-Klasse, wie sie im Header definiert ist:
STM32NTCUART = stm32_ntc_uart_ns.class_(
    "STM32NTCUART",   # Klassenname in C++
    cg.Component,     # erbt von esphome::Component
    uart.UARTDevice,  # erbt von esphome::uart::UARTDevice
    sensor.Sensor     # erbt von esphome::sensor::Sensor
)

# YAML-Konfiguration: wir bauen eine "Sensor-Plattform"
# - Standard-Felder wie Name, Unit, Icon, ...
# - plus das UART-Device-Schema
CONFIG_SCHEMA = sensor.sensor_schema(
    STM32NTCUART,
    unit_of_measurement=UNIT_CELSIUS,
    icon=ICON_THERMOMETER,
    accuracy_decimals=1,
    device_class=DEVICE_CLASS_TEMPERATURE,
    state_class=STATE_CLASS_MEASUREMENT
).extend({
    cv.GenerateID(): cv.declare_id(STM32NTCUART),
}).extend(uart.UART_DEVICE_SCHEMA)

# to_code() wird aufgerufen, wenn ESPHome die C++-Instanzen erzeugt
def to_code(config):
    # Hole das Objekt von "uart_id: ..." aus der YAML
    # (Dieser Key kommt aus `uart.UART_DEVICE_SCHEMA`)
    parent = yield cg.get_variable(config[uart.CONF_UART_ID])
    # Neues C++-Objekt anlegen
    var = cg.new_Pvariable(config[CONF_ID], parent)
    # Komponente registrieren (damit setup(), loop() etc. laufen)
    cg.register_component(var, config)
    # UART registrieren
    cg.register_uart_device(var, config)
    # Sensor registrieren (damit publish_state() etc. weiß, wie er heißen soll)
    sensor.register_sensor(var, config)
