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

PLATFORMS = ["sensor"]
DEPENDENCIES = ["uart"]

stm32_ntc_uart_ns = cg.esphome_ns.namespace("stm32_ntc_uart")
STM32NTCUARTSensor = stm32_ntc_uart_ns.class_(
    "STM32NTCUARTSensor",
    cg.Component,       # Erbt von esphome::Component
    uart.UARTDevice,    # Erbt von esphome::uart::UARTDevice
    sensor.Sensor       # Erbt von esphome::sensor::Sensor
)

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


async def to_code(config):
    # 1) Erzeuge/„declariere” das C++-Objekt
    var = cg.new_Pvariable(config[CONF_ID])

    # 2) Registriere es als Komponente (setup() / loop())
    yield cg.register_component(var, config)

    # 3) Registriere es als UART-Device
    yield uart.register_uart_device(var, config)

    # 4) Registriere es als Sensor (publish_state, Name etc.)
    yield sensor.register_sensor(var, config)
