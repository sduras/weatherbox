from datetime import datetime
import math

# Emoji map
moon_emojis = {
    "New Moon": "🌑",
    "Waxing Crescent": "🌒",
    "First Quarter": "🌓",
    "Waxing Gibbous": "🌔",
    "Full Moon": "🌕",
    "Waning Gibbous": "🌖",
    "Last Quarter": "🌗",
    "Waning Crescent": "🌘"
}

def moon_info(date=None):
    if date is None:
        now = datetime.utcnow()
    else:
        now = date

    epoch = datetime(2000, 1, 6, 18, 14)
    moon_cycle = 29.53058867
    delta = now - epoch
    days = delta.days + delta.seconds / 86400
    moon_day = math.fmod(days, moon_cycle)
    phase = moon_day / moon_cycle

    if 0 <= phase < 0.125:
        phase_name = "New Moon"
    elif phase < 0.25:
        phase_name = "Waxing Crescent"
    elif phase < 0.375:
        phase_name = "First Quarter"
    elif phase < 0.5:
        phase_name = "Waxing Gibbous"
    elif phase < 0.625:
        phase_name = "Full Moon"
    elif phase < 0.75:
        phase_name = "Waning Gibbous"
    elif phase < 0.875:
        phase_name = "Last Quarter"
    else:
        phase_name = "Waning Crescent"

    return phase_name, moon_day

# Usage
phase, moon_day = moon_info()
moon_day_number = round(moon_day)
emoji = moon_emojis.get(phase, "🌚")

print("Current Moon Phase:", phase, emoji)
print("Moon Day (in cycle):", moon_day_number)
