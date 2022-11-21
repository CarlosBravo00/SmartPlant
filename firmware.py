from grove_rgb_lcd import *
import time
import grovepi
from grovepi import *
import math
import Adafruit_DHT
import requests
import json

import random

temp_sensor = 0
light_sensor = 1
led = 3
water_sensor = 2

threshold = 10

URL = "https://cvvajx5zq0.execute-api.us-west-2.amazonaws.com/logs"

MAX_LIGHT = 750
MIN_LIGHT = 0

MAX_WATER = 300
MIN_WATER = 1023

LOG_INTERVAL = 10  # SEGUNDOS


def getPercentage(minValue, maxValue, value):
    res = (minValue - value) / (minValue - maxValue)
    return str(round(res * 100)) + '%'


def LEDControl(value):
    resistance = (float)(1023 - value) * 10 / value
    if resistance > threshold:
        grovepi.digitalWrite(led, 1)
    else:
        grovepi.digitalWrite(led, 0)


counter = 0
temp_acum = 0
light_acum = 0
water_acum = 0

while True:
    try:

        setRGB(0, 255, 0)
        temp_value = grovepi.temp(temp_sensor, '1.1')
        light_value = grovepi.analogRead(light_sensor)
        water_value = grovepi.analogRead(water_sensor)

        setText("T: " + str(round(temp_value, 2)) + "C\nL: " +
                getPercentage(MIN_LIGHT, MAX_LIGHT, light_value) + "  W: "
                + getPercentage(MIN_WATER, MAX_WATER, water_value))

        LEDControl(light_value)
        time.sleep(1)
        counter = counter + 1

        temp_acum += temp_value
        light_acum += light_value
        water_acum += water_value

        if counter == LOG_INTERVAL:
            temp_acum /= counter
            light_acum /= counter
            water_acum /= counter
            data = {'light': round(light_acum, 2),
                    'water': round(water_acum, 2),
                    'temperature': round(temp_acum, 2)}
            Headers = {'Content-Type': 'application/json'}
            r = requests.post(url=URL, data=json.dumps(data), headers=Headers)
            print(r, r.json())
            counter = 0
            temp_acum = 0
            light_acum = 0
            water_acum = 0
    except KeyboardInterrupt:
        setText("KeyboardInterrupt")
        setRGB(255, 0, 0)
        break
    except IOError:
        setText("IOError")
        setRGB(255, 0, 0)
        break

time.sleep(1)
setText("All done")
setRGB(0, 255, 0)
