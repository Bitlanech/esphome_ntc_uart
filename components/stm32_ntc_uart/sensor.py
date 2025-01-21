import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, uart
from esphome.const import CONF_ID

PLATFORMS = ["sensor"]
DEPENDENCIES = ["uart"]

# Namespace
stm32_ntc_uart_ns = cg.esphome_ns.namespace("stm32_ntc_uart")

# Deklariere die Sub-Sensor-Klasse, die in C++ MySubSensor heißt
# und erbt von sensor::Sensor
MySubSensor = stm32_ntc_uart_ns.class_(
    "MySubSensor",
    sensor.Sensor
)
# Sag ESPHome: "Es gibt einen parameterlosen Konstruktor MySubSensor()"
MySubSensor.add_constructor([], return_type=MySubSensor)

# Hauptklasse
STM32NTCUARTMulti = stm32_ntc_uart_ns.class_(
    "STM32NTCUARTMulti",
    cg.Component,
    uart.UARTDevice
)

# Meldung, dass es in STM32NTCUARTMulti eine Methode add_sensor(sensor::Sensor*) gibt
STM32NTCUARTMulti.add_method(
    "add_sensor",
    cg.void,
    [sensor.Sensor.operator("ptr")]
)

# Schema: mehrere Sub-Sensoren
CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(STM32NTCUARTMulti),
    cv.Required("sensors"): cv.ensure_list(sensor.SENSOR_SCHEMA),
}).extend(uart.UART_DEVICE_SCHEMA)

async def to_code(config):
    # 1) Hauptobjekt
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)

    # 2) Schleife über die Sub-Sensoren
    for i, sconf in enumerate(config["sensors"]):
        # Falls kein id: in YAML, legen wir ein Auto-ID an
        if CONF_ID not in sconf:
            sconf[CONF_ID] = cg.declare_id(MySubSensor)(f"auto_sub_{i}")

        sub_id = sconf[CONF_ID]

        # 3) Erzeuge ein Objekt: MySubSensor()
        sub_sensor = cg.new_Pvariable(sub_id, MySubSensor)
        # Parameter aus sconf anwenden (name, unit_of_measurement etc.)
        await sensor.register_sensor(sub_sensor, sconf)
        # 4) In C++ add_sensor(sub_sensor) aufrufen
        cg.add(var.add_sensor(sub_sensor))
