import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, uart
from esphome.const import CONF_ID

PLATFORMS = ["sensor"]
DEPENDENCIES = ["uart"]

stm32_ntc_uart_ns = cg.esphome_ns.namespace("stm32_ntc_uart")

MySubSensor = stm32_ntc_uart_ns.class_(
    "MySubSensor",  # Muss C++-Klassennamen entsprechen
    sensor.Sensor
)
# Parameterloser Konstruktor registrieren
# => KEIN return_type=... verwenden!
MySubSensor.add_constructor()

STM32NTCUARTMulti = stm32_ntc_uart_ns.class_(
    "STM32NTCUARTMulti",
    cg.Component,
    uart.UARTDevice
)
STM32NTCUARTMulti.add_method(
    "add_sensor",
    cg.void,
    [sensor.Sensor.operator("ptr")]  # sensor::Sensor*
)

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(STM32NTCUARTMulti),
    cv.Required("sensors"): cv.ensure_list(sensor.SENSOR_SCHEMA),
}).extend(uart.UART_DEVICE_SCHEMA)

async def to_code(config):
    # Hauptobjekt anlegen
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)

    # Liste "sensors:" durchgehen
    for i, sconf in enumerate(config["sensors"]):
        # Falls kein id: angegeben, generieren wir einen
        if CONF_ID not in sconf:
            sconf[CONF_ID] = cg.declare_id(MySubSensor)(f"auto_sub_{i}")

        sub_id = sconf[CONF_ID]

        # Ein Objekt vom Typ MySubSensor() anlegen
        sub_sensor = cg.new_Pvariable(sub_id, MySubSensor)
        await sensor.register_sensor(sub_sensor, sconf)

        # In C++ => var->add_sensor(sub_sensor);
        cg.add(var.add_sensor(sub_sensor))
