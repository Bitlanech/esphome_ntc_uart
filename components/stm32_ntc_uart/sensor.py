import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, uart
from esphome.const import CONF_ID

PLATFORMS = ["sensor"]
DEPENDENCIES = ["uart"]

stm32_ntc_uart_ns = cg.esphome_ns.namespace("stm32_ntc_uart")

# Deine C++-Klasse: Erbt nur von Component+UARTDevice, keine direkte Sensor-Vererbung
STM32NTCUARTMulti = stm32_ntc_uart_ns.class_(
    "STM32NTCUARTMulti",
    cg.Component,
    uart.UARTDevice
)

# Angeben, dass in C++ eine Methode existiert:
#    void add_sensor(sensor::Sensor *s)
AddSensorMethod = STM32NTCUARTMulti.add_method(
    "add_sensor",
    cg.void,
    [sensor.Sensor.operator("ptr")]  # "ptr" statt "*"
)

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(STM32NTCUARTMulti),
    cv.Required("sensors"): cv.ensure_list(sensor.SENSOR_SCHEMA),
}).extend(uart.UART_DEVICE_SCHEMA)

async def to_code(config):
    # 1) Haupt-C++-Objekt anlegen
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)

    # 2) Für jeden Eintrag in "sensors" ein Sub-Sensor erzeugen
    for sconf in config["sensors"]:
        # a) Roh-Objekt erstellen (ohne ID)
        sub_sensor = cg.new_Pvariable(None, sensor.Sensor)

        # b) bei ESPHome "registrieren", damit Name, Filters etc. aus sconf angewendet werden
        await sensor.register_sensor(sub_sensor, sconf)

        # c) in C++-Klasse einhängen
        cg.add(var.add_sensor(sub_sensor))
