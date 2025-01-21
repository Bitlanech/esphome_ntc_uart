import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, uart
from esphome.const import CONF_ID

PLATFORMS = ["sensor"]
DEPENDENCIES = ["uart"]
CODEOWNERS = ["@Bitlanech"]

# Namespace, der zu deiner C++-Klasse passt
stm32_ntc_uart_ns = cg.esphome_ns.namespace("stm32_ntc_uart")

# Klasse, die NUR von Component + UARTDevice erbt (kein direkter sensor::Sensor!)
STM32NTCUARTMulti = stm32_ntc_uart_ns.class_(
    "STM32NTCUARTMulti",
    cg.Component,
    uart.UARTDevice
)

# Wir sagen ESPHome: "C++-Methode add_sensor(sensor::Sensor *s) existiert"
AddSensorMethod = STM32NTCUARTMulti.add_method(
    "add_sensor",
    cg.void,                        # Rückgabewert: void
    [sensor.Sensor.operator("ptr")] # Parameter: sensor::Sensor*
)

# Sub-Sensor-Schema: Alle üblichen sensor-Felder + OPTIONAL ein id-Feld
SUB_SENSOR_SCHEMA = sensor.SENSOR_SCHEMA.extend({
    cv.Optional(CONF_ID): cv.declare_id(sensor.Sensor),
})

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(STM32NTCUARTMulti),
    # Mehrere Sub-Sensoren möglich:
    cv.Required("sensors"): cv.ensure_list(SUB_SENSOR_SCHEMA),
}).extend(uart.UART_DEVICE_SCHEMA)

async def to_code(config):
    # 1) Hauptobjekt anlegen
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)

    # 2) Für jeden Sensor in der YAML-Liste "sensors"
    for i, sconf in enumerate(config["sensors"]):
        # a) Falls kein "id:" in YAML, generieren wir einen
        if CONF_ID not in sconf:
            sconf[CONF_ID] = cg.declare_id(sensor.Sensor)(f"auto_sub_sensor_{i}")

        sub_id = sconf[CONF_ID]

        # b) Ein sensor::Sensor-Objekt anlegen
        sub_sensor = cg.new_Pvariable(sub_id, sensor.Sensor)

        # c) Bei ESPHome registrieren => Name, Einheit, Filter etc. aus sconf
        await sensor.register_sensor(sub_sensor, sconf)

        # d) In unserer C++-Klasse verknüpfen
        cg.add(var.add_sensor(sub_sensor))
