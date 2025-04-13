# forecast.py

import gc
import json

import framebuf
import urequests
import writer

from config import SH1106_HEIGHT, SH1106_WIDTH
from display import display_reading, oled
from fonts import smallfont

weather_codes_to_icons = {
    0: "sun",
    1: "sun",
    2: "clouds",
    3: "overcast",
    45: "fog",
    48: "fog",
    51: "drizzle",
    53: "drizzle",
    55: "drizzle",
    56: "snow",
    57: "snow",
    61: "drizzle",
    63: "drizzle",
    65: "rain",
    66: "rain",
    67: "rain",
    71: "snow",
    73: "snow",
    75: "snow",
    77: "drizzle",
    80: "drizzle",
    81: "drizzle",
    82: "showers-violent",
    85: "snow",
    86: "snow",
    95: "showers-violent",
    96: "showers-violent",
    99: "showers-violent",
}

weather_codes_to_description = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Slight or moderate thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def get_tomorrow_weather_code():
    latitude = 49.8383
    longitude = 24.0232
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=weather_code&forecast_days=2&timezone=Europe%2FKyiv"

    try:
        response = urequests.get(url)
        if response.status_code == 200:
            weather_data = response.json()
            response.close()
            if (
                "daily" in weather_data
                and "weather_code" in weather_data["daily"]
                and len(weather_data["daily"]["weather_code"]) > 1
            ):
                tomorrow_weather_code = weather_data["daily"]["weather_code"][
                    1
                ]
                return tomorrow_weather_code
            else:
                print("Error: Could not find tomorrow's weather code in the response.")
                return None
        else:
            print(
                f"Error: Open-Meteo API request failed with status code: {response.status_code}"
            )
            return None
    except urequests.exceptions.OSError as e:
        print(f"Error making HTTP request (check network): {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def get_weather_icon(weather_code):
    return weather_codes_to_icons.get(weather_code, "unknown")


def get_weather_description(weather_code):
    return weather_codes_to_description.get(weather_code, "Unknown")


def load_forecast_bitmap(filename):
    try:
        with open(f"/images/{filename}.pbm", "rb") as f:
            f.readline()
            f.readline()
            f.readline()
            return bytearray(f.read())
    except Exception as e:
        print(f"Error loading bitmap '{filename}': {e}")
        return None


def display_forecast(bitmap_data):
    if bitmap_data is None:
        print("Error: No bitmap data to display.")
        return

    if not isinstance(bitmap_data, (bytes, bytearray)):
        print("Error: Invalid bitmap data type.")
        return

    try:
        fbuf = framebuf.FrameBuffer(bitmap_data, 55, 55, framebuf.MONO_HLSB)
    except Exception as e:
        print(f"Error creating FrameBuffer: {e}")
        return

    oled.fill(0)
    font_writer = writer.Writer(oled, smallfont)
    font_writer.set_textpos(35, 1)
    font_writer.printstring("3ABTPA")
    start_x = (128 - 55) // 2
    start_y = (64 - 39) // 2
    oled.blit(fbuf, start_x, start_y)
    oled.show()
    gc.collect()