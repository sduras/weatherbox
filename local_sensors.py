import re
import time

import bme280
import ds18x20
import machine
import onewire
from machine import Pin, SoftI2C

DS18X20_PIN = 15
BME280_SCL = 5
BME280_SDA = 4

dat = machine.Pin(DS18X20_PIN)
ow = onewire.OneWire(dat)
ds = ds18x20.DS18X20(ow)

bme = bme280.BME280(i2c=SoftI2C(scl=Pin(BME280_SCL), sda=Pin(BME280_SDA)))


def extract_numeric_value(value_str):
    if isinstance(value_str, str):
        numeric_value = re.search(r"[-+]?\d*\.\d+|\d+", value_str)
        if numeric_value:
            return float(numeric_value.group(0))
    elif isinstance(value_str, (int, float)):
        return float(value_str)
    return None


def read_ds_sensor(ds_sensor):
    try:
        roms = ds_sensor.scan()
        if not roms:
            print("No DS18x20 sensors found!")
            return "DS18x20 Error"

        ds_sensor.convert_temp()
        time.sleep_ms(750)

        for rom in roms:
            try:
                tempC = ds_sensor.read_temp(rom)
                rounded = round(tempC)
                return rounded
            except Exception as e:
                print(f"Error reading DS18x20 sensor: {e}")
                return "DS18x20 Read Error"

    except Exception as e:
        print(f"Sensor scan failed: {e}")
        return "DS18x20 Scan Error"


def read_bme280_values():
    try:
        return bme.values
    except Exception as e:
        print(f"Error reading BME280 values: {e}")
        return None


def read_bme280_temperature():
    values = read_bme280_values()
    if values:
        temp, _, _ = values
        temp_value = float(temp[:-1]) if isinstance(temp, str) else temp
        return round(temp_value)
    return "Temp Error"


def read_bme280_humidity():
    values = read_bme280_values()
    if values:
        _, _, hum = values
        hum_value = float(hum[:-1]) if isinstance(hum, str) else hum
        return round(hum_value)
    return "Humidity Error"


def read_bme280_pressure():
    values = read_bme280_values()
    if values:
        _, pressure_hPa, _ = values
        pressure_value = (
            float(pressure_hPa[:-3]) if isinstance(pressure_hPa, str) else pressure_hPa
        )
        conversion_factor = 0.7500616827
        pressure_mmHg = round(pressure_value * conversion_factor) + 33
        return round(pressure_mmHg)
    return "Pressure Error"


def observations():
    try:
        print("Initializing sensors...")

        ds_available = ds.scan()
        bme_available = read_bme280_values() is not None

        if not ds_available:
            print("DS18x20 sensor not found. Skipping.")
        if not bme_available:
            print("BME280 sensor not responding. Skipping.")

        if not ds_available and not bme_available:
            print("No sensors available.")
            return {}

        print("Starting observation loop. Reading every 5 minutes...\n")

        while True:
            try:
                observations = {}

                if ds_available:
                    temp_out = read_ds_sensor(ds)
                    print(f"Temperature outside: {temp_out}C")
                    observations["outside_temp_C"] = temp_out

                if bme_available:
                    temp_in = read_bme280_temperature()
                    humidity = read_bme280_humidity()
                    pressure = read_bme280_pressure()

                    print(f"Temperature inside: {temp_in}C")
                    print(f"Humidity inside: {humidity}%")
                    print(f"Pressure inside: {pressure} mmHg")
                    print("-" * 40)
                    print()

                    observations["inside_temp_C"] = temp_in
                    observations["humidity_%"] = humidity
                    observations["pressure_mmHg"] = pressure

                print("Observations:", observations)
                print("-" * 40)

            except Exception as loop_error:
                print("Error during observation cycle:", loop_error)

            time.sleep(100)

    except Exception as setup_error:
        print("Failed to initialize or run observation loop:", setup_error)

    return observations


def get_latest_observation():
    try:
        observation = {}

        ds_available = ds.scan()
        bme_available = read_bme280_values() is not None

        if ds_available:
            temp_out = read_ds_sensor(ds)
            print(f"Temperature outside: {temp_out}C")
            observation["outside_temp_C"] = f"{temp_out}C"

        if bme_available:
            temp_in = read_bme280_temperature()
            humidity = read_bme280_humidity()
            pressure = read_bme280_pressure()

            print(f"Temperature inside: {temp_in}C")
            print(f"Humidity inside: {humidity}%")
            print(f"Pressure inside: {pressure} mmHg")

            observation["inside_temp_C"] = f"{temp_in}C"
            observation["humidity_%"] = f"{humidity}%"
            observation["pressure_mmHg"] = f"{pressure}"

        return observation

    except Exception as e:
        print("Error getting observation:", e)
        return {}
