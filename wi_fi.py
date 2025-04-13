# wi_fi.py

import time

import network


def read_credentials():
    try:
        with open("credentials.txt", "r") as f:
            lines = f.readlines()

            if len(lines) < 2:
                print("Error [Wi-Fi]: File does not contain both SSID and PASSWORD.")
                return None, None

            ssid_line = next((line for line in lines if "SSID=" in line), None)
            password_line = next((line for line in lines if "PASSWORD=" in line), None)

            if ssid_line and password_line:
                ssid = ssid_line.strip().split("=")[1].strip()
                password = password_line.strip().split("=")[1].strip()
                if ssid and password:
                    return ssid, password
                else:
                    print("Error [Wi-Fi]: Invalid SSID or password format.")
                    return None, None
            else:
                print("Error [Wi-Fi]: SSID or PASSWORD not found in credentials.txt.")
                return None, None
    except Exception as e:
        print(f"Error [Wi-Fi] reading credentials: {e}")
        return None, None


def connect_wifi():
    ssid, password = read_credentials()

    if ssid is None or password is None:
        print("Error [Wi-Fi]: Cannot retrieve credentials, proceeding without Wi-Fi.")
        return False

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"Attempting to connect to Wi-Fi: SSID='{ssid}'")
        wlan.connect(ssid, password)

        attempt = 0
        while not wlan.isconnected():
            print(f"[Wi-Fi] Attempt {attempt}: Connection status: {wlan.status()}")
            if attempt >= 10:  # Increased retry within this function
                print(
                    "[Wi-Fi] Failed to connect after multiple attempts within connect_wifi."
                )
                return False
            attempt += 1
            time.sleep(2)
            if attempt > 0 and attempt % 5 == 0:
                if wlan.status() == network.STAT_IDLE:
                    print("[Wi-Fi] Re-attempting connection.")
                    wlan.connect(ssid, password)

        ip = wlan.ifconfig()[0]
        print(f"[Wi-Fi] Connected on {ip}")
        return True
    else:
        print("[Wi-Fi] Already connected.")
        print(f"[Wi-Fi] IP address: {wlan.ifconfig()[0]}")
        return True


if __name__ == "__main__":
    if connect_wifi():
        print("[Wi-Fi] Wi-Fi connection test successful.")
    else:
        print("[Wi-Fi] Wi-Fi connection test failed.")
