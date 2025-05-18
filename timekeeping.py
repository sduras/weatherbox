import socket
import struct
import time

import urtc
from machine import Pin, SoftI2C

I2C_RTC = SoftI2C(scl=Pin(19), sda=Pin(18))
NTP_SERVER = "pool.ntp.org"
LVIV_TIMEZONE_OFFSET_SECONDS_STANDARD = 2 * 3600
LVIV_TIMEZONE_OFFSET_SECONDS_DST = 3 * 3600

rtc = urtc.DS3231(I2C_RTC)
_rtc_updated_this_session = False


def is_lviv_dst(utc_timestamp):
    year = time.localtime(utc_timestamp)[0]
    first_of_march = time.mktime((year, 3, 1, 0, 0, 0, 0, 0, -1))
    weekday_first_march = time.localtime(first_of_march)[6]
    days_to_last_sunday_march = (6 - weekday_first_march + 7) % 7
    dst_start_day = 31 - days_to_last_sunday_march
    dst_start_timestamp_utc = time.mktime((year, 3, dst_start_day, 3, 0, 0, 0, 0, 0))

    first_of_october = time.mktime((year, 10, 1, 0, 0, 0, 0, 0, -1))
    weekday_first_october = time.localtime(first_of_october)[6]
    days_to_last_sunday_october = (6 - weekday_first_october + 7) % 7
    dst_end_day = 31 - days_to_last_sunday_october
    dst_end_timestamp_utc = time.mktime((year, 10, dst_end_day, 4, 0, 0, 0, 0, 0))

    return dst_start_timestamp_utc <= utc_timestamp < dst_end_timestamp_utc


def get_ntp_time_utc():
    addr = socket.getaddrinfo(NTP_SERVER, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(2)
    ntp_utc_timestamp = None
    try:
        s.connect(addr)
        s.send(b"\x1b" + 47 * b"\x00")
        data = s.recv(48)
        if data:
            ntp_time = struct.unpack("!12I", data)[10]
            ntp_utc_timestamp = ntp_time - 2208988800
            print(
                f"[Timekeeping] Received NTP time (UTC timestamp): {ntp_utc_timestamp}"
            )
            return ntp_utc_timestamp
    except OSError as e:
        print(f"[Timekeeping] Error getting NTP time: {e}")
    finally:
        s.close()
    return None


def sync_rtc_from_ntp(timezone_str):
    global _rtc_updated_this_session
    print("[Timekeeping] Attempting to sync RTC from NTP...")
    try:
        utc_timestamp = get_ntp_time_utc()
        if utc_timestamp is not None:
            if is_lviv_dst(utc_timestamp):
                timezone_offset_seconds = LVIV_TIMEZONE_OFFSET_SECONDS_DST
                dst_active = True
            else:
                timezone_offset_seconds = LVIV_TIMEZONE_OFFSET_SECONDS_STANDARD
                dst_active = False

            local_time = time.localtime(utc_timestamp + timezone_offset_seconds)
            rtc_time_tuple = (
                local_time[0],
                local_time[1],
                local_time[2],
                (
                    local_time[6] + 1 if local_time[6] < 6 else 0
                ),  # weekday (Mon=0, Sun=6) -> urtc (Mon=1, Sun=7)
                local_time[3],
                local_time[4],
                local_time[5],
                0,
            )
            rtc.datetime(rtc_time_tuple)
            _rtc_updated_this_session = True
            print(f"[Timekeeping] NTP sync successful. RTC set to: {rtc.datetime()}")
            print(f"[Timekeeping] DST active in Lviv: {dst_active}")
            return True
        else:
            print("[Timekeeping] NTP sync failed.")
            print(f"[Timekeeping] Current RTC time: {rtc.datetime()}")
            return False
    except Exception as e:
        print(f"[Timekeeping] Error during NTP sync and RTC update: {e}")
        print(f"[Timekeeping] Current RTC time: {rtc.datetime()}")
        return False


def get_rtc_time():
    rtc_time = rtc.datetime()
    year, month, day, weekday, hour, minute, second, _ = rtc_time
    return (
        year,
        month,
        day,
        hour,
        minute,
        second,
        weekday - 1,
    )


def set_rtc_time(year, month, day, hour, minute, second, weekday):
    rtc.datetime((year, month, day, weekday + 1, hour, minute, second, 0))


# if __name__ == "__main__":
#     i2c = SoftI2C(scl=Pin(19), sda=Pin(18))
#     rtc_test = urtc.DS3231(i2c)
#
#     print("[Timekeeping - Test] Current RTC time:", rtc_test.datetime())
#     print("[Timekeeping - Test] Attempting NTP sync...")
#     if sync_rtc_from_ntp("Europe/Lviv"):
#         print("[Timekeeping - Test] RTC time after sync:", rtc_test.datetime())
#     else:
#         print("[Timekeeping - Test] NTP sync failed, RTC time unchanged.")
#
#     utc_now = time.time()
#     print(f"[Timekeeping - Test] UTC Timestamp: {utc_now}")
#     print(f"[Timekeeping - Test] Is DST in Lviv now? {is_lviv_dst(utc_now)}")
