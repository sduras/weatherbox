# display.py

import gc
import time

import framebuf
import sh1106
import writer
from machine import PWM, Pin, SoftI2C

from config import (
    BLUE_LED_PIN,
    COMFORT_PRESSURE,
    GREEN_LED_PIN,
    I2C_SH1106_PINS,
    PRESSURE_TOLERANCE,
    RED_LED_PIN,
    SH1106_CONTRAST,
    SH1106_FLIP,
    SH1106_HEIGHT,
    SH1106_WIDTH,
)
from fonts import agave, smallfont
from local_sensors import get_latest_observation

try:
    i2c = SoftI2C(scl=Pin(I2C_SH1106_PINS[1]), sda=Pin(I2C_SH1106_PINS[0]))
    oled = sh1106.SH1106_I2C(SH1106_WIDTH, SH1106_HEIGHT, i2c, addr=0x3C)
    oled.contrast(SH1106_CONTRAST)
    oled.flip(SH1106_FLIP)
    font_writer = writer.Writer(oled, agave)
    small_font_writer = writer.Writer(oled, smallfont)
except Exception as e:
    print(f"Error initializing display: {e}")
    oled = None
    font_writer = None
    small_font_writer = None

try:
    red_led = PWM(Pin(RED_LED_PIN))
    green_led = PWM(Pin(GREEN_LED_PIN))
    blue_led = PWM(Pin(BLUE_LED_PIN))
    red_led.freq(1000)
    green_led.freq(1000)
    blue_led.freq(1000)

    def set_led_color(r, g, b):
        red_duty = int(r * 65535)
        green_duty = int(g * 2000)
        blue_duty = int(b * 65535)
        red_led.duty_u16(red_duty)
        green_led.duty_u16(green_duty)
        blue_led.duty_u16(blue_duty)

    set_led_color(0, 0.2, 0)
except Exception as e:
    print(f"Error initializing LEDs: {e}")
    red_led = None
    green_led = None
    blue_led = None

    def set_led_color(r, g, b):
        pass


def load_bitmap(filename):
    try:
        with open(f"/images/{filename}.pbm", "rb") as f:
            for _ in range(3):
                f.readline()
            return bytearray(f.read())
    except Exception as e:
        print(f"Error loading bitmap '{filename}': {e}")
        return None


temp_out_icon = load_bitmap("temp_out")
temp_in_icon = load_bitmap("temp_in")
hum_icon = load_bitmap("hum")
press_icon = load_bitmap("pres")


def display_reading(icon, label, value):
    if oled is None or font_writer is None:
        print("Display not initialized, skipping display_reading.")
        return
    try:
        oled.fill(0)
        oled.flip(SH1106_FLIP)
        oled.contrast(SH1106_CONTRAST)

        if icon:
            fbuf = framebuf.FrameBuffer(icon, 25, 25, framebuf.MONO_HLSB)
            start_x = (SH1106_WIDTH - 25) // 2
            start_y = 0
            oled.blit(fbuf, start_x, start_y)

        font_writer.set_textpos(35, 30)
        font_writer.printstring(f"{value}")

        oled.show()
        gc.collect()
        time.sleep(5)

    except Exception as e:
        print(f"Error displaying {label}: {e}")


def display_change(weather_change_info, icon):
    if oled is None or small_font_writer is None:
        print("Display not initialized, skipping display_change.")
        return
    try:
        oled.fill(0)

        if icon:
            fbuf = framebuf.FrameBuffer(icon, 25, 25, framebuf.MONO_HLSB)
            start_x = (SH1106_WIDTH - 25) // 2
            start_y = 0
            oled.blit(fbuf, start_x, start_y)

        small_font_writer.set_textpos(5, 50)
        small_font_writer.printstring(weather_change_info)

        oled.show()
    except Exception as e:
        print(f"Error displaying weather change: {e}")




def display_main_loop():
    if oled is None:
        print("Display not initialized, skipping display_main_loop.")
        return
    try:
        weather = get_latest_observation()
        if not weather:
            print("No observation data to display.")
            return

        outside_temp = weather.get("outside_temp_C", "N/A")
        inside_temp = weather.get("inside_temp_C", "N/A")
        humidity = weather.get("humidity_%", "N/A")
        pressure = weather.get("pressure_mmHg", "N/A")

        display_reading(temp_out_icon, "Out", f"{outside_temp}")
        display_reading(temp_in_icon, "In", f"{inside_temp}")
        display_reading(hum_icon, "Humidity", f"{humidity}")

        try:
            current_pressure = (
                float(pressure.replace(" mmHg", ""))
                if " mmHg" in pressure
                else float(pressure)
            )
            if not (
                COMFORT_PRESSURE - PRESSURE_TOLERANCE
                <= current_pressure
                <= COMFORT_PRESSURE + PRESSURE_TOLERANCE
            ):
                comfort_icon = load_bitmap("pressure_comfort")
                if comfort_icon:
                    display_reading(comfort_icon, "Pressure", f"{pressure}")
                else:
                    display_reading(press_icon, "Pressure", f"{pressure}")
            else:
                display_reading(press_icon, "Pressure", f"{pressure}")

        except ValueError:
            display_reading(press_icon, "Pressure", f"{pressure}")

        except Exception as e:
            print("Failed to update display:", e)

    except Exception as e:
        print(f"Error displaying weather: {e}")


def display_clock(t):
    if oled is None or font_writer is None:
        print("Display not initialized, skipping display_clock.")
        return
    try:
        oled.fill(0)
        font_writer.set_textpos(15, 25)
        time_str = "{:02d}:{:02d}".format(t[3], t[4])
        font_writer.printstring(time_str)
        oled.show()
    except Exception as e:
        print(f"Error displaying clock: {e}")


def trigger_led_change():
    if red_led and green_led and blue_led:
        set_led_color(1, 0, 0)
        time.sleep(0.2)
        set_led_color(0, 0, 0)
        time.sleep(0.2)
        set_led_color(0, 0, 0)
        time.sleep(0.2)
        set_led_color(0, 0, 0)
