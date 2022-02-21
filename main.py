import random

import BAC0
import time

from BAC0.core.devices.local.models import (
    analog_input,
    analog_output,
    analog_value,
    binary_input,
    binary_output,
    binary_value,
    multistate_input,
    multistate_output,
    multistate_value,
    date_value,
    datetime_value,
    temperature_input,
    temperature_value,
    humidity_input,
    humidity_value,
    character_string,
)
from BAC0.core.devices.local.object import ObjectFactory

# bacnet = BAC0.lite(ip="192.168.1.40/24")
device_app = BAC0.lite(ip="192.168.1.40/24", port=47808, deviceId=101)

time.sleep(1)
_new_objects = analog_input(
        instance=0,
        name="RT",
        properties={"units": "degreesCelsius"},
        description="Room Temperature",
        presentValue=17,
    )
_new_objects = analog_value(
        instance=0,
        name="VT",
        properties={"units": "degreesCelsius"},
        description="Wanted Temperature",
        presentValue=22,
    )
_new_objects = binary_input(
        instance=0,
        name="BI",
        description="Device ON/OFF",
        presentValue=True,
    )


_new_objects.add_objects_to_application(device_app)

i = 0
previousTemperature = actualTemperature = device_app["RT"].presentValue
counter = 0
randCounter = random.randint(45, 90)


while True:
    actualTemperature = device_app["RT"].presentValue
    wantedTemperature = device_app["VT"].presentValue
    devState = device_app["BI"].presentValue

    print(actualTemperature)
    print(devState)

    if devState != "inactive":
        temp = previousTemperature + 0.05 * (wantedTemperature - actualTemperature)
    else:
        temp = actualTemperature - 0.2


    if counter < randCounter:
        counter += 1
        rand = random.randint(0, 3) * 0.1
    elif counter == randCounter:
        counter += 1
        rand = random.randint(0, 3) * 0.22
    elif counter > randCounter and (counter < randCounter + 3):
        counter += 1
        rand = random.randint(0, 3) * 0.1
    else:
        counter = 0
        randCounter = random.randint(45, 90)
        rand = 0

    if randCounter > 70:
        rand = -rand


    device_app["RT"].presentValue = temp - rand


    previousTemperature = temp
    time.sleep(1)







input("prompt: ")