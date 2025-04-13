
import time

import forecast
import timekeeping
import wi_fi
from config import (
    BLINK_INTERVAL_MS,
    CLOCK_DISPLAY_DURATION_SECONDS,
    DISPLAY_UPDATE_INTERVAL,
    FORECAST_DISPLAY_DURATION_SECONDS,
    NTP_SYNC_INTERVAL_SECONDS,
    WEATHER_CHECK_INTERVAL,
    WIFI_RETRY_ATTEMPTS,
    WIFI_RETRY_DELAY,
)
from display import (
    display_clock,
    display_main_loop,
    display_reading,
    load_bitmap,
    set_led_color,
)
from weather_change import check_weather_change


def main_loop():
    last_weather_check = 0
    last_display_update = time.ticks_ms() - (DISPLAY_UPDATE_INTERVAL * 1000)
    last_ntp_sync = 0
    weather_change_info_cache = []
    significant_change_level = 0
    last_blink_time = 0
    led_on = False
    wifi_connected = False
    clock_display_active = False
    clock_display_start_time = 0
    last_forecast_display = time.ticks_ms() - (FORECAST_DISPLAY_DURATION_SECONDS * 1000)

    print("Attempting to connect to Wi-Fi for time sync and forecast...")
    for attempt in range(WIFI_RETRY_ATTEMPTS):
        try:
            if wi_fi.connect_wifi():
                print("Wi-Fi connected successfully!")
                wifi_connected = True
                break
            else:
                print(
                    f"Wi-Fi connection failed (attempt {attempt + 1}). Retrying in {WIFI_RETRY_DELAY} seconds..."
                )
                time.sleep(WIFI_RETRY_DELAY)
        except Exception as e:
            print(
                f"An error occurred during Wi-Fi connection (attempt {attempt + 1}): {e}"
            )
            time.sleep(WIFI_RETRY_DELAY)

    if wifi_connected:
        print("Attempting initial time synchronization from NTP...")
        try:
            if timekeeping.sync_rtc_from_ntp("Europe/Lviv"):
                print("RTC synchronized from NTP successfully.")
                last_ntp_sync = time.time()
            else:
                print("Initial NTP synchronization failed. Using RTC time.")
        except Exception as e:
            print(f"Error during initial NTP sync: {e}")
            print("Using RTC time.")
    else:
        print("Wi-Fi not connected. Using RTC time.")

    while True:
        try:
            current_time_ms = time.ticks_ms()
            current_time_seconds = time.time()

            if (
                wifi_connected
                and current_time_seconds - last_ntp_sync >= NTP_SYNC_INTERVAL_SECONDS
            ):
                print("Attempting weekly time synchronization from NTP...")
                try:
                    if timekeeping.sync_rtc_from_ntp("Europe/Lviv"):
                        print("RTC synchronized from NTP successfully.")
                        last_ntp_sync = current_time_seconds
                    else:
                        print("Weekly NTP synchronization failed.")
                except Exception as e:
                    print(f"Error during weekly NTP sync: {e}")

            if (
                time.ticks_diff(current_time_ms, last_weather_check)
                >= WEATHER_CHECK_INTERVAL * 1000
            ):
                try:
                    weather_changes, significance = check_weather_change()
                    last_weather_check = current_time_ms

                    if weather_changes:
                        print(f"Weather Changes Detected: {weather_changes}")
                        weather_change_info_cache = weather_changes
                        significant_change_level = significance
                    else:
                        weather_change_info_cache = []
                        significant_change_level = 0

                except Exception as e:
                    print(f"Error checking weather change: {e}")
                    weather_change_info_cache = []
                    significant_change_level = 0

            if significant_change_level == 2:
                if (
                    time.ticks_diff(current_time_ms, last_blink_time)
                    >= BLINK_INTERVAL_MS
                ):
                    led_on = not led_on
                    set_led_color(1 if led_on else 0, 0, 0)
                    last_blink_time = current_time_ms
            elif significant_change_level == 1:
                set_led_color(0, 0, 0.2)
            else:
                set_led_color(0, 0.2, 0)

            try:
                display_main_loop()

                if (
                    wifi_connected
                    and time.ticks_diff(current_time_ms, last_forecast_display)
                    >= FORECAST_DISPLAY_DURATION_SECONDS * 1000
                ):
                    tomorrow_forecast_code = forecast.get_tomorrow_weather_code()
                    if tomorrow_forecast_code is not None:
                        icon_filename = forecast.get_weather_icon(
                            tomorrow_forecast_code
                        )
                        bitmap_data = forecast.load_forecast_bitmap(icon_filename)
                        forecast.display_forecast(bitmap_data)
                        time.sleep(7)
                        last_forecast_display = current_time_ms

                if weather_change_info_cache:
                    for change, icon in weather_change_info_cache:
                        display_reading(load_bitmap(icon), "", change)

                current_rtc_time = timekeeping.get_rtc_time()
                display_clock(current_rtc_time)
                time.sleep(CLOCK_DISPLAY_DURATION_SECONDS)

            except Exception as e:
                print(f"Error updating display: {e}")

            time.sleep(1)

        except Exception as e:
            print(f"EXCEPTION IN MAIN LOOP: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main_loop()
