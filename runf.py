import wt as main
import serial
import time,math

from autonomic import update_weekly_avg, autonomic_plane

def bell_curve_efficiency(temp_c):
    """
    Bell curve model centered at 25°C.
    Efficiency reduces as temperature deviates from 25°C.
    """
    optimal_temp = 25
    sigma = 10   # spread of the curve
    efficiency = math.exp(-((temp_c - optimal_temp) ** 2) / (2 * sigma ** 2))
    return efficiency  # between 0 and 1


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

    api_key = "59fa7bff31936dcd5ba90343da033b98"
    
    charge = int(input("Enter current smartwatch battery percentage: "))


    if charge < 30:
        print("Battery critically low. Charging to 40% minimum for GPS/Zigbee readiness.")
        charge = 40
        if hardware_enabled:
            smartwatch.write(b'1\n')
            print("Sent charging signal to PMU.")
        else:
            print("[Simulated] Charging signal sent to PMU.")

    choice = input("Enter 0 to use weather API or 1 to enter conditions manually: ")

    try:
        if choice == '0':
            print("Fetching next day's weather forecast...")
            weather, forecast_temp, efficiency = main.fetch_weather(api_key)
            print(f"Forecast retrieved: {weather}, Temperature: {forecast_temp}°C, Efficiency: {efficiency:.2f}")
            
            # Use forecast temperature for weekly average and autonomic plane
            weekly_avg = update_weekly_avg(forecast_temp)
            forecast_temp = autonomic_plane(forecast_temp, weekly_avg)
            
            ndw = get_weather_prediction(weather)
            solar_forecast = efficiency * (1.0 if ndw == 1 else 0.6 if ndw == 0 else 0.3)

            print(f"Combined Solar Forecast Score: {solar_forecast:.2f}")

        elif choice == '1':
            print("Enter weather condition:")
            print("1 for Sunny, 0 for Cloudy, -1 for Rainy")
            ndw = int(input())
            
            # Ask user for forecast temperature
            forecast_temp = float(input("Enter forecast temperature (°C): "))
            
            # Use forecast temperature for weekly average and autonomic plane
            weekly_avg = update_weekly_avg(forecast_temp)
            forecast_temp = autonomic_plane(forecast_temp, weekly_avg)
            
            efficiency = bell_curve_efficiency(forecast_temp)
            solar_forecast = efficiency * (1.0 if ndw == 1 else 0.6 if ndw == 0 else 0.3)
            print(f"Manual Solar Forecast Score: {solar_forecast:.2f}")
        else:
            print("Invalid choice. Exiting.")
            return

        # -------------------- Adaptive Charging Strategy --------------------
        if charge < 30:
            print("Battery critically low. Charging to 40% minimum for GPS/Zigbee readiness.")
            charge = 40
            if hardware_enabled:
                smartwatch.write(b'1\n')
                print("Sent charging signal to PMU.")
            else:
                print("[Simulated] Charging signal sent to PMU.")

        elif 30 <= charge < 100:
            print("Processing adaptive charging strategy based on solar forecast...")

            if solar_forecast > 0.75:
                print("High solar potential — limit night charging to 30%. Use solar energy during daylight.")
                charge = 30
                if hardware_enabled:
                    smartwatch.write(b'0\n')
                    print("Sent low-charge mode command to PMU.")
                else:
                    print("[Simulated] Low-charge mode activated.")

            elif 0.4 < solar_forecast <= 0.75:
                print("Moderate solar potential — charge up to 60% for safe GPS operation.")
                charge = 60
                if hardware_enabled:
                    smartwatch.write(b'1\n')
                    print("Sent moderate-charge command to PMU.")
                else:
                    print("[Simulated] Moderate-charge mode activated.")

            else:
                print("Low solar potential , Fully charging the smartwatch")
                charge = 100
                if hardware_enabled:
                    smartwatch.write(b'1\n')
                    print("Sent full-charge command to PMU.")
                else:
                    print("[Simulated] Full-charge mode activated.")

        # -------------------- PMU RESPONSE HANDLING --------------------
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