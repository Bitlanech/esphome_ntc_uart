import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, uart
from esphome.const import (
    CONF_ID,
)

# Deklariere: "Dieses Verzeichnis stellt eine Sensor-Plattform bereit"
PLATFORMS = ["sensor"]

# Wir brauchen UART, da wir 'uart::UARTDevice' nutzen
DEPENDENCIES = ["uart"]
CODEOWNERS = ["@Bitlanech"]

# Namespace (muss zu deinem C++-Namespace passen)
stm32_ntc_uart_ns = cg.esphome_ns.namespace("stm32_ntc_uart")

# Hier definieren wir eine Klasse, die NUR Component+UARTDevice erbt
# (keine direkte sensor::Sensor-Vererbung)
STM32NTCUARTMulti = stm32_ntc_uart_ns.class_(
    "STM32NTCUARTMulti",
    cg.Component,
    uart.UARTDevice
)

# Eine "add_sensor"-Methode, um Sub-Sensoren an die C++-Klasse zu hängen
# (die Signatur in C++ wird "void add_sensor(sensor::Sensor *);")
AddSensorMethod = STM32NTCUARTMulti.operator("add_sensor").bind(sensor.Sensor)

# Schema: Wir erwarten, dass der User eine Liste "sensors:" angeben kann
# Jeder Eintrag in "sensors" muss ein valides sensor.SENSOR_SCHEMA sein
CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(STM32NTCUARTMulti),
    cv.Required("sensors"): cv.ensure_list(sensor.SENSOR_SCHEMA),
}).extend(uart.UART_DEVICE_SCHEMA)

# Asynchrone to_code-Funktion
async def to_code(config):
    # 1) Erzeugung der C++-Hauptinstanz
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)

    # 2) Für jeden Eintrag in "sensors" erzeugen wir ein Sensor-Objekt
    for i, sconf in enumerate(config["sensors"]):
        # Erstellt ein sensor::Sensor-Objekt
        sub_sensor = await sensor.new_sensor_item(sconf)

        # "Anmelden" bei ESPHome (damit publish_state, name etc. greifen)
        # WICHTIG: Auf neueren ESPHome-Versionen async + await
        await sensor.register_sensor(sub_sensor, sconf)

        # 3) An unsere C++-Klasse anhängen
        cg.add(var.add_sensor(sub_sensor))
