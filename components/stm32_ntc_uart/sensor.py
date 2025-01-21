import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, uart
from esphome.const import CONF_ID, CONF_NAME

PLATFORMS = ["sensor"]
DEPENDENCIES = ["uart"]

# 1) Namespace
stm32_ntc_uart_ns = cg.esphome_ns.namespace("stm32_ntc_uart")

# 2) Abgeleitete Klasse MySubSensor : public sensor::Sensor
#    => Damit hat ESPHome einen definierbaren Konstruktor
MySubSensor = stm32_ntc_uart_ns.class_(
    "MySubSensor",
    sensor.Sensor
)
# Erkläre dem Codegen, dass es einen Standardkonstruktor "MySubSensor()" gibt
MySubSensor.add_constructor()

# 3) Die Hauptklasse STM32NTCUARTMulti
STM32NTCUARTMulti = stm32_ntc_uart_ns.class_(
    "STM32NTCUARTMulti",
    cg.Component,
    uart.UARTDevice
)

# Wir sagen: In STM32NTCUARTMulti gibt es eine Methode:
#    void add_sensor(sensor::Sensor *s)
AddSensorMethod = STM32NTCUARTMulti.add_method(
    "add_sensor",
    cg.void,
    [sensor.Sensor.operator("ptr")]
)

# 4) Schema für Sub-Sensoren
SUB_SENSOR_SCHEMA = sensor.SENSOR_SCHEMA.extend({
    # optional ein ID, damit man "id: my_sub_id" angeben kann
    cv.Optional(CONF_ID): cv.declare_id(MySubSensor),
})

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(STM32NTCUARTMulti),
    cv.Required("sensors"): cv.ensure_list(SUB_SENSOR_SCHEMA),
}).extend(uart.UART_DEVICE_SCHEMA)


async def to_code(config):
    # Hauptobjekt anlegen
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)

    # Für jeden Eintrag in "sensors" => MySubSensor anlegen
    for i, sconf in enumerate(config["sensors"]):
        # Falls kein ID da, generieren wir einen
        if CONF_ID not in sconf:
            sconf[CONF_ID] = cg.declare_id(MySubSensor)(f"auto_sub_sensor_{i}")

        sub_id = sconf[CONF_ID]

        # Erzeuge "MySubSensor()" im Code
        sub_sensor = cg.new_Pvariable(sub_id, MySubSensor)

        # Wende name, unit_of_measurement etc. an
        await sensor.register_sensor(sub_sensor, sconf)

        # Nun in C++ => var->add_sensor(sub_sensor);
        cg.add(var.add_sensor(sub_sensor))
