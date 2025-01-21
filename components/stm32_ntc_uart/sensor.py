import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, uart
from esphome.const import CONF_ID

PLATFORMS = ["sensor"]
DEPENDENCIES = ["uart"]
CODEOWNERS = ["@Bitlanech"]

stm32_ntc_uart_ns = cg.esphome_ns.namespace("stm32_ntc_uart")

# Deine C++-Klasse, die NICHT von sensor::Sensor erbt, sondern Sub-Sensoren verwaltet
STM32NTCUARTMulti = stm32_ntc_uart_ns.class_(
    "STM32NTCUARTMulti",
    cg.Component,
    uart.UARTDevice
)

# Anmelden der Methode: void add_sensor(sensor::Sensor *s)
# Achte auf .operator("ptr")!
AddSensorMethod = STM32NTCUARTMulti.add_method(
    "add_sensor",
    cg.void,
    [sensor.Sensor.operator("ptr")]
)

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(STM32NTCUARTMulti),
    cv.Required("sensors"): cv.ensure_list(sensor.SENSOR_SCHEMA),
}).extend(uart.UART_DEVICE_SCHEMA)

async def to_code(config):
    # 1) Hauptobjekt erzeugen
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)

    # 2) Für jeden Sensor in der YAML-Liste ein Sensor-Objekt anlegen
    for sconf in config["sensors"]:
        sub_sensor = await sensor.new_sensor_item(sconf)
        # Registrieren bei ESPHome (damit publish_state(), name etc. funktionieren)
        await sensor.register_sensor(sub_sensor, sconf)

        # 3) In C++ var->add_sensor(...) aufrufen
        cg.add(var.add_sensor(sub_sensor))
