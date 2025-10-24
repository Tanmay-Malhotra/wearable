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

    # Calculate average temperature for environmental adaptation
    weekly_avg = sum(weekly_temps) / len(weekly_temps)
    return weekly_avg

def autonomic_plane(current_temp, weekly_avg):
    # If deviation > ±10, impute with weekly average
    if abs(current_temp - weekly_avg) > 10:
        print(f"Temperature deviation detected. Imputing {current_temp} with weekly average {weekly_avg}.")
        current_temp = weekly_avg
    return current_temp

def get_weather_prediction(weather):
    weather_mapping = {
        "Clear": 1,        # Sunny
        "Clouds": 0,       # Cloudy
        "Rain": -1,        # Rainy
        "Drizzle": -1,
        "Thunderstorm": -1,
        "Snow": -1,
        "Mist": 0,
        "Fog": 0
    }
    return weather_mapping.get(weather, 0)  # Default to cloudy if not matched

def manage_battery():
    hardware_enabled = input("Enable smartwatch hardware communication? (y/n): ").lower() == 'y'
    smartwatch = None

    if hardware_enabled:
        try:
            smartwatch = serial.Serial('COM6', 9600, timeout=1)
            print("Connected to Smartwatch Power Management Unit (PMU)")
            time.sleep(2)
        except Exception as e:
            print(f"Error connecting to smartwatch: {e}")
            hardware_enabled = False

    api_key = ""
    charge = int(input("Enter current smartwatch battery percentage: "))
    current_temp = float(input("Enter current ambient temperature (°C): "))

    weekly_avg = update_weekly_avg(current_temp)
    current_temp = autonomic_plane(current_temp, weekly_avg)

    choice = input("Enter 0 to use weather API or 1 to enter conditions manually: ")

    try:
        if choice == '0':
            print("Fetching next day's weather forecast...")
            weather = main.fetch_weather(api_key)
            print(f"Forecast retrieved: {weather}")
            ndw = get_weather_prediction(weather)
        elif choice == '1':
            print("Enter weather condition:")
            print("1 for Sunny, 0 for Cloudy, -1 for Rainy")
            ndw = int(input())
        else:
            print("Invalid choice. Exiting.")
            return

        if charge < 30:
            print("Battery critically low. Charging to 40% minimum for GPS/Zigbee readiness.")
            charge = 40
            if hardware_enabled:
                smartwatch.write(b'1\n')
                print("Sent charging signal to PMU.")
            else:
                print("[Simulated] Charging signal sent to PMU.")

        elif 30 <= charge < 100:
            print("Processing adaptive charging strategy based on weather prediction...")

            if ndw == 1:
                print("Clear weather predicted — solar charging expected.")
                print("Limiting night charging to 30%. Using solar energy during daylight.")
                charge = 30
                if hardware_enabled:
                    smartwatch.write(b'0\n')
                    print("Sent low-charge mode command to PMU.")
                else:
                    print("[Simulated] Low-charge mode activated.")

            elif ndw == 0:
                print("Cloudy conditions predicted — partial solar availability.")
                print("Charging battery up to 70% for safe GPS operation.")
                charge = 70
                if hardware_enabled:
                    smartwatch.write(b'1\n')
                    print("Sent moderate-charge command to PMU.")
                else:
                    print("[Simulated] Moderate-charge mode activated.")

            elif ndw == -1:
                print("Rainy conditions predicted — low solar input expected.")
                print("Charging battery up to 80% using stored power sources (e.g., power bank).")
                charge = 80
                if hardware_enabled:
                    smartwatch.write(b'1\n')
                    print("Sent full-charge command to PMU.")
                else:
                    print("[Simulated] Full-charge mode activated.")

        if hardware_enabled:
            time.sleep(1)
            while smartwatch.in_waiting:
                pmu_response = smartwatch.readline().decode('utf-8').strip()
                print(f"PMU Response: {pmu_response}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        time.sleep(2)
        if smartwatch:
            smartwatch.close()
            print("Smartwatch PMU connection closed.")

if __name__ == "__main__":
    manage_battery()
