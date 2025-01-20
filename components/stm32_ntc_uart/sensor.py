import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, uart
from esphome.const import (
    CONF_ID,
    UNIT_CELSIUS,
    ICON_THERMOMETER,
    DEVICE_CLASS_TEMPERATURE,
    STATE_CLASS_MEASUREMENT,
)

# Sagt ESPHome, dass dieses Verzeichnis eine Sensor-Plattform enthält
PLATFORMS = ["sensor"]

# Wir brauchen "uart" als Abhängigkeit
DEPENDENCIES = ["uart"]

# (Optional) wer betreut diesen Code
CODEOWNERS = ["@DeinGitHubUser"]

# Namespace anlegen
stm32_ntc_uart_ns = cg.esphome_ns.namespace("stm32_ntc_uart")

# Aus stm32_ntc_uart_ns die Klasse STM32NTCUART "importieren"
# (Name + Basisklassen müssen zum C++-Code passen!)
STM32NTCUART = stm32_ntc_uart_ns.class_(
    "STM32NTCUART",   # C++-Klassenname
    cg.Component,     # erbt in C++ von esphome::Component
    uart.UARTDevice,  # erbt von esphome::uart::UARTDevice
    sensor.Sensor     # erbt von esphome::sensor::Sensor
)

# CONFIG_SCHEMA:
# Da du "sensor::Sensor" beerbst, nutzen wir sensor.sensor_schema(...)
CONFIG_SCHEMA = sensor.sensor_schema(
    STM32NTCUART,
    unit_of_measurement=UNIT_CELSIUS,
    icon=ICON_THERMOMETER,
    accuracy_decimals=1,
    device_class=DEVICE_CLASS_TEMPERATURE,
    state_class=STATE_CLASS_MEASUREMENT,
).extend({
    cv.GenerateID(): cv.declare_id(STM32NTCUART),
}).extend(uart.UART_DEVICE_SCHEMA)


def to_code(config):
    """Wird von ESPHome aufgerufen, um das C++-Objekt anzulegen."""
    # Holt das UART-Objekt (z. B. id: my_uart_bus) aus config
    parent = yield cg.get_variable(config[uart.CONF_UART_ID])
    # Erstellt ein C++-Objekt vom Typ STM32NTCUART
    var = cg.new_Pvariable(config[CONF_ID], parent)

    # Registrierung bei ESPHome:
    cg.register_component(var, config)
    cg.register_uart_device(var, config)
    sensor.register_sensor(var, config)
