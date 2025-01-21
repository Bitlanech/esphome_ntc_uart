import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, uart
from esphome.const import CONF_ID

# Unsere neue Sensor-Plattform
PLATFORMS = ["sensor"]
DEPENDENCIES = ["uart"]
CODEOWNERS = ["@Bitlanech"]

stm32_ntc_uart_ns = cg.esphome_ns.namespace("stm32_ntc_uart")

# Die C++-Klasse erbt von Component+UARTDevice
STM32NTCUARTMulti = stm32_ntc_uart_ns.class_(
    "STM32NTCUARTMulti",
    cg.Component,
    uart.UARTDevice
)

# Diese Zeile sagt ESPHome: 
# "Es gibt eine Methode add_sensor(...) in STM32NTCUARTMulti mit Signatur void(sensor::Sensor *)"
AddSensorMethod = STM32NTCUARTMulti.add_method(
    "add_sensor",
    cg.void,
    [cg.pointer_to(sensor.Sensor)],
)

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(STM32NTCUARTMulti),
    cv.Required("sensors"): cv.ensure_list(sensor.SENSOR_SCHEMA),
}).extend(uart.UART_DEVICE_SCHEMA)

async def to_code(config):
    # Haupt-C++-Objekt
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)

    # Für jeden Eintrag in "sensors" legen wir einen Sensor an
    for i, sconf in enumerate(config["sensors"]):
        sub_sensor = await sensor.new_sensor_item(sconf)
        await sensor.register_sensor(sub_sensor, sconf)
        # C++-Methode aufrufen
        cg.add(var.add_sensor(sub_sensor))
