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

# Wir definieren eine Sensor-Plattform
PLATFORMS = ["sensor"]
DEPENDENCIES = ["uart"]

# (Optional) wer sich kümmert
CODEOWNERS = ["@DeinGitHubUser"]

# Namespace passend zu deinem .h (z. B. namespace esphome::stm32_ntc_uart)
stm32_ntc_uart_ns = cg.esphome_ns.namespace("stm32_ntc_uart")

# Der Klassenname muss zum .h passen (z. B. class STM32NTCUARTSensor)
STM32NTCUARTSensor = stm32_ntc_uart_ns.class_(
    "STM32NTCUARTSensor",
    cg.Component,       # erbt von esphome::Component
    uart.UARTDevice,    # erbt von esphome::uart::UARTDevice
    sensor.Sensor       # erbt von esphome::sensor::Sensor
)

# YAML-Konfiguration: definieren, was man angeben darf
CONFIG_SCHEMA = sensor.sensor_schema(
    STM32NTCUARTSensor,
    unit_of_measurement=UNIT_CELSIUS,
    icon=ICON_THERMOMETER,
    accuracy_decimals=1,
    device_class=DEVICE_CLASS_TEMPERATURE,
    state_class=STATE_CLASS_MEASUREMENT,
).extend({
    cv.GenerateID(): cv.declare_id(STM32NTCUARTSensor),
}).extend(uart.UART_DEVICE_SCHEMA)

# Asynchrone to_code-Funktion:
# Verwende await, NICHT yield!
async def to_code(config):
    # C++-Objekt anlegen
    var = cg.new_Pvariable(config[CONF_ID])

    # 1) Komponente registrieren (setup/loop)
    await cg.register_component(var, config)

    # 2) UART registrieren
    await uart.register_uart_device(var, config)

    # 3) Sensor registrieren (publish_state, name etc.)
    await sensor.register_sensor(var, config)