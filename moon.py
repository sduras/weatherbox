import math
import time

from timekeeping import get_ntp_time_utc, get_rtc_time
from wi_fi import connect_wifi


def moon_info():
    ntp_timestamp = None
    if connect_wifi():
        print("[Main] Wi-Fi connected, attempting to fetch NTP time...")
        ntp_timestamp = get_ntp_time_utc()

    if ntp_timestamp:
        current_timestamp = ntp_timestamp
        print("[Main] Using NTP time.")
    else:
        print("[Main] NTP unavailable, falling back to RTC.")
        year, month, day, hour, minute, second, _ = get_rtc_time()
        current_timestamp = time.mktime(
            (year, month, day, hour, minute, second, 0, 0, -1)
        )

    epoch_timestamp = time.mktime((2000, 1, 6, 18, 14, 0, 0, 0, -1))
    moon_cycle = 29.53058867
    days = (current_timestamp - epoch_timestamp) / 86400

    moon_day = math.fmod(days, moon_cycle)
    if moon_day < 0:
        moon_day += moon_cycle
    phase = moon_day / moon_cycle
    moon_day_number = round(moon_day)

    if 0 <= phase < 0.125:
        phase_name = "new"
    elif phase < 0.25:
        phase_name = "waxing-crescent"
    elif phase < 0.375:
        phase_name = "first-quarter"
    elif phase < 0.5:
        phase_name = "waxing-gibbous"
    elif phase < 0.625:
        phase_name = "full"
    elif phase < 0.75:
        phase_name = "waning-gibbous"
    elif phase < 0.875:
        phase_name = "last-quarter"
    else:
        phase_name = "waning-crescent"

    return phase_name, moon_day_number


if __name__ == "__main__":
    moon_info()
