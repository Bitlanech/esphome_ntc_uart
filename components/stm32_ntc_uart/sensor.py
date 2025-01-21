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
CODEOWNERS = ["@Bitlanech"]

stm32_ntc_uart_ns = cg.esphome_ns.namespace("stm32_ntc_uart")

# Die C++-Klasse (für mehrere Sensoren)
STM32NTCUARTMulti = stm32_ntc_uart_ns.class_(
    "STM32NTCUARTMulti",  # Name muss zur .h passen
    cg.Component,         # erbt nur Component + UARTDevice
    uart.UARTDevice
)

# Diese Methode erlauben wir, um Sub-Sensoren "anzuhängen"
AddSensorMethod = STM32NTCUARTMulti.operator("add_sensor").bind(sensor.Sensor)

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(STM32NTCUARTMulti),
    cv.Optional("sensor_count", default=1): cv.int_range(min=1, max=8),
}).extend(uart.UART_DEVICE_SCHEMA)

# 'to_code' registriert die Multi-Klasse, legt Sub-Sensoren an und hängt sie an
async def to_code(config):
    # 1) Haupt-C++-Objekt anlegen
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)

    # 2) Schleife über "sensor_count"
    count = config["sensor_count"]
    for i in range(count):
        # Einen neuen Sensor anlegen
        sub_sensor = sensor.new_sensor(
            unit_of_measurement=UNIT_CELSIUS,
            icon=ICON_THERMOMETER,
            accuracy_decimals=1,
            device_class=DEVICE_CLASS_TEMPERATURE,
            state_class=STATE_CLASS_MEASUREMENT,
            # Du kannst auch 'name' angeben, falls jeder Sensor
            # seinen eigenen Namen in HA haben soll.
            name=f"STM32 NTC Sensor {i+1}"
        )
        # sub_sensor: vom Typ sensor::Sensor

        # Damit ESPHome weiß, dass wir ihn in der YAML config "drin" haben
        await sensor.register_sensor(sub_sensor, {})

        # Jetzt das Sub-Sensor-Objekt an unsere C++-Klasse anhängen
        cg.add(var.add_sensor(sub_sensor))
