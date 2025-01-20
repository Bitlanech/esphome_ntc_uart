import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, uart
from esphome.const import (
    CONF_ID,
    DEVICE_CLASS_TEMPERATURE,
    ICON_THERMOMETER,
    STATE_CLASS_MEASUREMENT,
    UNIT_CELSIUS,
)

# Wir brauchen UART
DEPENDENCIES = ["uart"]

# (Optional) Codeowner
CODEOWNERS = ["@DeinGitHubUser"]

# Namespace anlegen (muss zum C++-Namespace passen)
stm32_ntc_uart_ns = cg.esphome_ns.namespace("stm32_ntc_uart")

# C++-Klasse (Name muss zur .h-Datei passen)
STM32NTCUARTSensor = stm32_ntc_uart_ns.class_(
    "STM32NTCUARTSensor",
    cg.Component,
    uart.UARTDevice,
    sensor.Sensor,
)

# YAML-Konfigschema:
CONFIG_SCHEMA = sensor.sensor_schema(
    STM32NTCUARTSensor,
    unit_of_measurement=UNIT_CELSIUS,
    icon=ICON_THERMOMETER,
    accuracy_decimals=1,
    device_class=DEVICE_CLASS_TEMPERATURE,
    state_class=STATE_CLASS_MEASUREMENT
).extend({
    cv.GenerateID(): cv.declare_id(STM32NTCUARTSensor),
}).extend(uart.UART_DEVICE_SCHEMA)


def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    cg.register_component(var, config)
    cg.register_uart_device(var, config)
    sensor.register_sensor(var, config)
