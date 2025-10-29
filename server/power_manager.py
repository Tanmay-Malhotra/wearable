import mainnew as main
import serial
import time

# Array to store 7 days of temperature
weekly_temps = []
MAX_DAYS = 7

def update_weekly_avg(current_temp):
    global weekly_temps
    if len(weekly_temps) < MAX_DAYS:
        weekly_temps.append(current_temp)
    else:
        weekly_temps.pop(0)
        weekly_temps.append(current_temp)
    return sum(weekly_temps) / len(weekly_temps)

def autonomic_plane(current_temp, weekly_avg):
    if abs(current_temp - weekly_avg) > 10:
        current_temp = weekly_avg
    return current_temp

def get_weather_prediction(weather):
    mapping = {
        "Clear": 1, "Clouds": 0, "Rain": -1, "Drizzle": -1,
        "Thunderstorm": -1, "Snow": -1, "Mist": 0, "Fog": 0
    }
    return mapping.get(weather, 0)

def manage_battery_api(data):
    try:
        charge = int(data["charge"])
        current_temp = float(data["temperature"])
        mode = data.get("mode", "api")  # 'api' or 'manual'
        manual_weather = int(data.get("manual_weather", 0))
        hardware_enabled = bool(data.get("hardware_enabled", False))
        api_key = data.get("api_key", "")

        logs = []
        logs.append(f"Battery: {charge}%")
        logs.append(f"Temperature: {current_temp}°C")

        weekly_avg = update_weekly_avg(current_temp)
        current_temp = autonomic_plane(current_temp, weekly_avg)

        if mode == "api":
            weather = fetch_weather(api_key)
            ndw = get_weather_prediction(weather)
            logs.append(f"Weather fetched: {weather}")
        else:
            ndw = manual_weather
            logs.append(f"Manual weather: {ndw}")

        # Battery logic
        if charge < 30:
            logs.append("Battery critically low. Charging to 40% minimum.")
            charge = 40

        elif 30 <= charge < 100:
            if ndw == 1:
                logs.append("Clear weather — solar charging expected. Limit to 30%.")
                charge = 30
            elif ndw == 0:
                logs.append("Cloudy — charging up to 70% for safety.")
                charge = 70
            elif ndw == -1:
                logs.append("Rainy — charging up to 80% from backup.")
                charge = 80

        return {
            "success": True,
            "final_charge": charge,
            "logs": logs
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
    

if __name__ == "__main__":
    manage_battery_api()
