import logging
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
# from BAC0.core.devices.local.object import ObjectFactory

# bacnet = BAC0.lite(ip="192.168.1.40/24")
# BAC0.log_level("debug")
# BAC0.log_level(log_file=logging.DEBUG, stdout=logging.DEBUG, stderr=logging.CRITICAL)
# bacnet = BAC0.lite(ip="192.168.1.101/24", port=47810)
device = BAC0.lite(ip="10.0.0.9/24", port=47809, deviceId=101)


_new_objects = analog_input(
        instance=0,
        name="RT",
        properties={"units": "degreesCelsius"},
        description="Room Temperature",
        presentValue=17,
    )
_new_objects = analog_output(
        instance=0,
        name="WT",
        properties={"units": "degreesCelsius"},
        description="Wanted Temperature",
        presentValue=22,
    )
_new_objects = binary_output(
        instance=0,
        name="BO",
        description="Device ON/OFF",
        presentValue=True,
    )


_new_objects.add_objects_to_application(device)


# bacnet = BAC0.lite(ip="192.168.1.101/24", port=47810)
# mycontroller = BAC0.device("192.168.1.101/24:47809", 101, bacnet)
# mycontroller["WT"] = 50
# mycontroller["WT"].out_of_service()
# mycontroller["WT"] = "auto" (releasuje override priority 8) zapsané pomocí controler příkazu výše na defaultní hodnotu
#   mycontroller["WT"].default(number)
# mycontroller["WT"].write(34, priority=13)
# mycontroller["WT"].write("null", priority=13)


# bacnet.write('192.168.1.101/24:47809 analogOutput 0 presentValue 50 - 14')
# priorities = bacnet.read('192.168.1.101/24:47809 analogOutput 0 priorityArray')

i = 0
previousTemperature = actualTemperature = device["RT"].presentValue
counter = 0
randCounter = random.randint(45, 90)
prop = ('analogOutput', 0, 'priorityArray')

while True:
    actualTemperature = device["RT"].presentValue
    wantedTemperature = device["WT"].presentValue
    devState = device["BO"].presentValue

    print("Actual: ", actualTemperature)
    print("Wanted: ", wantedTemperature)

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
        rand = - rand

    device["RT"].presentValue = temp - rand
    # device.points
    # device["WT"].write_property(, value=25, priority=14)
    # print(device.read(prop))

    previousTemperature = temp
    time.sleep(1)







input("prompt: ")