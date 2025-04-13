# weather_change.py

from local_sensors import get_latest_observation

weather_history = []
MAX_HISTORY = 36


def clean(val):
    if isinstance(val, str):
        cleaned_value = "".join(c for c in val if c.isdigit() or c == "." or c == "-")
        try:
            return float(cleaned_value)
        except ValueError:
            return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def average(values):
    clean_vals = [clean(v) for v in values if clean(v) is not None]
    return sum(clean_vals) / len(clean_vals) if clean_vals else None


def check_weather_change():
    observation = get_latest_observation()
    if not observation:
        return [], 0

    required_keys = ["pressure_mmHg", "inside_temp_C", "humidity_%"]
    if not all(
        key in observation and observation[key] is not None for key in required_keys
    ):
        print("Warning: Incomplete observation data received.")
        if weather_history:
            weather_history.append(observation)
            if len(weather_history) > MAX_HISTORY:
                weather_history.pop(0)
        return [], 0

    weather_history.append(observation)
    if len(weather_history) > MAX_HISTORY:
        weather_history.pop(0)

    if len(weather_history) < 2:
        return [], 0

    first_observation = weather_history[0]

    if any(
        first_observation.get(key) is None or clean(first_observation[key]) is None
        for key in required_keys
    ) or any(
        observation.get(key) is None or clean(observation[key]) is None
        for key in required_keys
    ):
        print("Warning: Could not clean all observation values for comparison.")
        return [], 0

    pressure_diff = clean(observation["pressure_mmHg"]) - clean(
        first_observation["pressure_mmHg"]
    )
    temp_diff = clean(observation["inside_temp_C"]) - clean(
        first_observation["inside_temp_C"]
    )
    hum_diff = clean(observation["humidity_%"]) - clean(first_observation["humidity_%"])

    print(
        f"Temp diff: {temp_diff:.1f}°C, Hum diff: {hum_diff:.1f}%, Pressure diff: {pressure_diff:.1f} mmHg"
    )

    changes = []
    significant_level = 0

    if abs(temp_diff) >= 5:
        temp_str = f"{temp_diff:+.0f}"
        changes.append((temp_str, "temp_in"))
        significant_level = max(significant_level, 2)
    elif abs(temp_diff) >= 3:
        temp_str = f"{temp_diff:+.0f}"
        changes.append((temp_str, "temp_in"))
        significant_level = max(significant_level, 1)

    if abs(hum_diff) >= 15:
        hum_str = f"{hum_diff:+.0f}"
        changes.append((hum_str, "hum"))
        significant_level = max(significant_level, 2)
    elif abs(hum_diff) >= 10:
        hum_str = f"{hum_diff:+.0f}"
        changes.append((hum_str, "hum"))
        significant_level = max(significant_level, 1)

    if abs(pressure_diff) >= 10:
        press_str = f"{pressure_diff:+.0f}"
        changes.append((press_str, "pres"))
        significant_level = max(significant_level, 2)
    elif abs(pressure_diff) >= 5:
        press_str = f"{pressure_diff:+.0f}"
        changes.append((press_str, "pres"))
        significant_level = max(significant_level, 1)

    return changes, significant_level
