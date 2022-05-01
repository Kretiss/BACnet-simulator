import random

from bacpypes.primitivedata import Real
from numpy import real
import BAC0
import time
from BAC0.core.devices.local.models import (
    analog_input,
    analog_output,
    binary_output,
)

# Define device

device = BAC0.lite(ip="10.0.0.34/24", port=47809, deviceId=101)

# Define device objects
_new_objects = analog_input(
    instance=10,
    name="RoomOneTemperature",
    properties={"units": "degreesCelsius"},
    description="Room 1 Temperature",
    presentValue=20.0,
)
_new_objects = analog_input(
    instance=20,
    name="RoomTwoTemperature",
    properties={"units": "degreesCelsius"},
    description="Room 2 Temperature",
    presentValue=21.0,
)
_new_objects = analog_output(
    instance=10,
    name="RoomOneSetPoint",
    properties={"units": "degreesCelsius"},
    description="Room one set point",
    presentValue=21.0,
)
_new_objects = analog_output(
    instance=20,
    name="RoomTwoSetPoint",
    properties={"units": "degreesCelsius"},
    description="Room two set point",
    presentValue=22.0,
)
_new_objects = binary_output(
    instance=10,
    name="RoomOneHeating",
    description="Room one heating state",
    presentValue=True,
)
_new_objects = binary_output(
    instance=20,
    name="RoomTwoHeating",
    description="Room two heating state",
    presentValue=True,
)

# Assign object to device
_new_objects.add_objects_to_application(device)

# Constants

# Rozměry: 2.5x4x4, VxŠxH
# 1) https://www.prirodnistavba.cz/popup/soucinitel-tepelne-vodivosti-33e.html
# 2) https://stavba.tzb-info.cz/tabulky-a-vypocty/58-hodnoty-fyzikalnich-velicin-vybranych-stavebnich-materialu
# 3) https://cs.wikipedia.org/wiki/M%C4%9Brn%C3%A1_tepeln%C3%A1_kapacita
# 4) https://e-konstrukter.cz/prakticka-informace/vlastnosti-vzduchu

outside_temperature = 15
inner_wall_depth = 0.16
outer_wall_depth = 0.25
wall_surface = 10  # 2.5x4m
room_size = 40  # 2.5x4x4m
inner_wall_sigma = 0.36  # objemová hmotnost 1700kg/m3, měrná tepelná kapacita 840 J/kg*K, řádek 60 - 2 web
inner_wall_capacity = 840 * 1700 * wall_surface * inner_wall_depth
outer_wall_sigma = 0.76  # objemová hmotnost 1000kg/m3
# outer_wall_sigma = 2  # objemová hmotnost 1000kg/m3
# outer_wall_capacity = 1300
# outer_wall_capacity = 1300
inner_wall_heat_transfer_const = inner_wall_sigma * wall_surface / inner_wall_depth
outer_wall_heat_transfer_const = outer_wall_sigma * wall_surface / outer_wall_depth
radiator_heat_transfer_const = 229 * 0.5  # Nějaký hliníkový radiátor
# radiator_heat_transfer_const = 1000  # Nějaký hliníkový radiátor

# air_sigma = 0.0262
# objemová hmotnost 1.205 kg/m3 při 20 stupních, měrná tepelná kapacita 1005 J/kg*K při 20 stupních, 4 web
room_capacity = 1005 * 1.205 * room_size

# walls
# inner_wall_temp = (device["RoomOneTemperature"].presentValue + device["RoomTwoTemperature"].presentValue) / 2
# outer_wall_r1_temp = (device["RoomOneTemperature"].presentValue + outside_temperature) / 2
# outer_wall_r2_temp = (device["RoomTwoTemperature"].presentValue + outside_temperature) / 2

eps = 0.3
r1_radiator_state = False
r2_radiator_state = False

# Main loop
while True:
    r1_temperature = device["RoomOneTemperature"].presentValue
    r2_temperature = device["RoomTwoTemperature"].presentValue
    r1_set_point = device["RoomOneSetPoint"].presentValue
    r2_set_point = device["RoomTwoSetPoint"].presentValue
    r1_heating = True if device["RoomOneHeating"].presentValue == "active" else False
    r2_heating = True if device["RoomTwoHeating"].presentValue == "active" else False
    print("Room one: ", r1_temperature)
    print("Room two: ", r2_temperature)

    r1_temp_diff = r1_set_point - r1_temperature
    r2_temp_diff = r2_set_point - r2_temperature

    if r1_heating:
        if r1_radiator_state and r1_temp_diff < -eps:
            r1_radiator_state = False
        elif r1_temp_diff > eps:
            r1_radiator_state = True
    else:
        r1_radiator_state = False

    if r2_heating:
        if r2_radiator_state and r2_temp_diff < -eps:
            r2_radiator_state = False
        elif r2_temp_diff > eps:
            r2_radiator_state = True
    else:
        r2_radiator_state = False

    # if r1_heating and r1_temp_diff > eps:
    #     r1_radiator_state = True
    # else:
    #     r1_radiator_state = False
    # if r2_heating and r2_temp_diff > eps:
    #     r2_radiator_state = True
    # else:
    #     r2_radiator_state = False

    print("Room 1 radiator: ", r1_radiator_state)
    print("Room 2 radiator: ", r2_radiator_state)

    inner_wall_heat_flow = abs(inner_wall_heat_transfer_const * (r1_temperature - r2_temperature))
    room_wall_temp_diff = 1 / room_capacity * inner_wall_heat_flow
    r1_outer_wall_heat_flow = outer_wall_heat_transfer_const * (r1_temperature - outside_temperature)
    r1_outer_wall_temp_diff = 1 / room_capacity * r1_outer_wall_heat_flow
    r2_outer_wall_heat_flow = outer_wall_heat_transfer_const * (r2_temperature - outside_temperature)
    r2_outer_wall_temp_diff = 1 / room_capacity * r1_outer_wall_heat_flow
    r1_radiator_heat_flow = radiator_heat_transfer_const * (Real(50) - r1_temperature) * r1_radiator_state
    r1_radiator_temp_diff = 1 / room_capacity * r1_radiator_heat_flow
    r2_radiator_heat_flow = radiator_heat_transfer_const * (Real(50) - r2_temperature) * r2_radiator_state
    r2_radiator_temp_diff = 1 / room_capacity * r2_radiator_heat_flow

    if r1_temperature > r2_temperature:
        new_r1_temp = r1_temperature - room_wall_temp_diff - r1_outer_wall_temp_diff
        new_r2_temp = r2_temperature + room_wall_temp_diff - r2_outer_wall_temp_diff
    else:
        new_r1_temp = r1_temperature + room_wall_temp_diff - r1_outer_wall_temp_diff
        new_r2_temp = r2_temperature - room_wall_temp_diff - r2_outer_wall_temp_diff

    if r1_radiator_heat_flow > 0:
        new_r1_temp += r1_radiator_temp_diff
    if r2_radiator_heat_flow > 0:
        new_r2_temp += r2_radiator_temp_diff

    # inner_wall_temp = (new_r1_temp + new_r2_temp) / 2
    # outer_wall_r1_temp = (new_r1_temp + outside_temperature) / 2
    # outer_wall_r2_temp = (new_r2_temp + outside_temperature) / 2

    device["RoomOneTemperature"].presentValue = new_r1_temp
    device["RoomTwoTemperature"].presentValue = new_r2_temp

    time.sleep(0.1)

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
#
# i = 0
# previousTemperature = actualTemperature = device["RT"].presentValue
# counter = 0
# randCounter = random.randint(45, 90)
# prop = ('analogOutput', 0, 'priorityArray')
#
# while True:
#     actualTemperature = device["RT"].presentValue
#     wantedTemperature = device["WT"].presentValue
#     devState = device["BO"].presentValue
#
#     print("Actual: ", actualTemperature)
#     print("Wanted: ", wantedTemperature)
#
#     if devState != "inactive":
#         temp = previousTemperature + 0.05 * (wantedTemperature - actualTemperature)
#     else:
#         temp = actualTemperature - 0.2
#
#     if counter < randCounter:
#         counter += 1
#         rand = random.randint(0, 3) * 0.1
#     elif counter == randCounter:
#         counter += 1
#         rand = random.randint(0, 3) * 0.22
#     elif counter > randCounter and (counter < randCounter + 3):
#         counter += 1
#         rand = random.randint(0, 3) * 0.1
#     else:
#         counter = 0
#         randCounter = random.randint(45, 90)
#         rand = 0
#
#     if randCounter > 70:
#         rand = - rand
#
#     device["RT"].presentValue = temp - rand
#     # device.points
#     # device["WT"].write_property(, value=25, priority=14)
#     # print(device.read(prop))
#
#     previousTemperature = temp
#     time.sleep(1)
#
#
#
#
#


input("prompt: ")
