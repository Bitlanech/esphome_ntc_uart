import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, uart
from esphome.const import CONF_ID

PLATFORMS = ["sensor"]
DEPENDENCIES = ["uart"]
CODEOWNERS = ["@Bitlanech"]

# Namespace passend zu deiner C++-Namespace
stm32_ntc_uart_ns = cg.esphome_ns.namespace("stm32_ntc_uart")

# 1. Sub-Sensor-Klasse, die von sensor::Sensor erbt
MySubSensor = stm32_ntc_uart_ns.class_("MySubSensor", sensor.Sensor)

# 2. Parameterlosen Konstruktor hinzufügen
MySubSensor.add_constructor([])

# 3. Hauptklasse zur Verwaltung mehrerer Sub-Sensoren
STM32NTCUARTMulti = stm32_ntc_uart_ns.class_(
    "STM32NTCUARTMulti",
    cg.Component,
    uart.UARTDevice
)

# 4. Methode zur Hinzufügung von Sub-Sensoren deklarieren
STM32NTCUARTMulti.add_method(
    "add_sensor",
    cg.void,
    [sensor.Sensor.operator("ptr")]  # sensor::Sensor* Parameter
)

# 5. Schema für Sub-Sensoren definieren
SUB_SENSOR_SCHEMA = sensor.SENSOR_SCHEMA.extend({
    cv.Optional(CONF_ID): cv.declare_id(MySubSensor),
})

# 6. Gesamtes Konfigurationsschema
CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(STM32NTCUARTMulti),
    cv.Required("sensors"): cv.ensure_list(SUB_SENSOR_SCHEMA),
}).extend(uart.UART_DEVICE_SCHEMA)

# 7. Asynchrone to_code-Funktion
async def to_code(config):
    # Hauptobjekt anlegen
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)

    # Für jeden Sub-Sensor in der YAML-Liste
    for i, sconf in enumerate(config["sensors"]):
        # Falls kein 'id' angegeben ist, automatisch generieren
        if CONF_ID not in sconf:
            # Generiere einen eindeutigen ID-Namen
            sconf[CONF_ID] = cg.new_id(MySubSensor)

        sub_id = sconf[CONF_ID]

        # Sub-Sensor-Objekt erstellen (parameterloser Konstruktor)
        sub_sensor = cg.new_Pvariable(sub_id, MySubSensor)

        # Sensor-Konfiguration anwenden (Name, Einheit etc.)
        await sensor.register_sensor(sub_sensor, sconf)

        # In der C++-Klasse den Sub-Sensor hinzufügen
        cg.add(var.add_sensor(sub_sensor))
