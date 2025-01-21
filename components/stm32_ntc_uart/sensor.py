import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, uart
from esphome.const import CONF_ID

PLATFORMS = ["sensor"]
DEPENDENCIES = ["uart"]

# Namespace
stm32_ntc_uart_ns = cg.esphome_ns.namespace("stm32_ntc_uart")

# C++-Klasse, erbt Component+UARTDevice
STM32NTCUARTMulti = stm32_ntc_uart_ns.class_(
    "STM32NTCUARTMulti",
    cg.Component,
    uart.UARTDevice
)

# Hier definieren wir, dass es eine Methode
#   void add_sensor(sensor::Sensor *s)
# in der C++-Klasse gibt.
AddSensorMethod = STM32NTCUARTMulti.add_method(
    "add_sensor",
    cg.void,
    [sensor.Sensor.operator("*")]  # <-- Wichtig: operator("*")
)

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(STM32NTCUARTMulti),
    cv.Required("sensors"): cv.ensure_list(sensor.SENSOR_SCHEMA),
}).extend(uart.UART_DEVICE_SCHEMA)

async def to_code(config):
    # Haupt-Objekt anlegen
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)

    # Für jeden Eintrag in "sensors" in der YAML
    for i, sconf in enumerate(config["sensors"]):
        # Erstellt ein sensor::Sensor-Objekt
        sub_sensor = await sensor.new_sensor_item(sconf)
        # Registriert den Sensor bei ESPHome
        await sensor.register_sensor(sub_sensor, sconf)
        # Ruft in C++ var->add_sensor(sub_sensor) auf
        cg.add(var.add_sensor(sub_sensor))
