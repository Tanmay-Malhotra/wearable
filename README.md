# Solar-Powered Smartwatch Battery Management System

An intelligent battery management system for solar-powered smartwatches that optimizes charging strategies based on weather forecasts and environmental conditions.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Hardware Requirements](#hardware-requirements)
- [Usage](#usage)
- [System Architecture](#system-architecture)
- [Configuration](#configuration)
- [Weather Prediction Logic](#weather-prediction-logic)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

This system implements an adaptive battery management strategy for solar-powered smartwatches. By analyzing weather forecasts and temperature patterns, it optimizes charging to maximize solar energy utilization while ensuring the device maintains sufficient power for critical operations like GPS and Zigbee connectivity.

## Features

### Adaptive Charging Strategy
- Weather-Based Optimization: Adjusts charging levels based on next-day weather predictions
- Solar Priority: Maximizes use of solar energy when sunny weather is forecasted
- Smart Fallback: Increases grid charging when poor weather is expected

### Environmental Monitoring
- Temperature Tracking: Maintains 7-day rolling temperature history
- Anomaly Detection: Automatically detects and corrects temperature outliers (±10°C deviation)
- Environmental Adaptation: Uses weekly averages for baseline calibration

### Battery Protection
- Critical Level Protection: Automatically charges to 40% when battery drops below 30%
- GPS/Zigbee Readiness: Ensures minimum power for essential connectivity features
- Graceful Degradation: Simulation mode available when hardware is unavailable

### Hardware Integration
- Serial Communication: Direct PMU control via COM port
- Real-time Monitoring: Receives and displays PMU responses
- Error Handling: Robust connection management with automatic fallback

## Installation

### Prerequisites

- Python 3.6 or higher
- pip package manager

### Dependencies

Install required Python packages:
```bash
pip install pyserial
```

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/solar-smartwatch-battery-manager.git
cd solar-smartwatch-battery-manager
```

2. Ensure the required modules are present:
   - `mainnew.py` - Must include `fetch_weather(api_key)` function

3. Configure your weather API key (see Configuration section)

## Hardware Requirements

### Optional Hardware Setup

- Smartwatch with PMU: Compatible smartwatch with Power Management Unit
- Serial Connection: USB-to-Serial adapter or built-in serial port
- Default Port: COM6 (configurable)
- Baud Rate: 9600

Note: The system can run in simulation mode without hardware for testing and development.

## Usage

### Running the Program
```bash
python battery_manager.py
```

### Interactive Prompts

The system will guide you through the following inputs:

1. Hardware Connection
```
   Enable smartwatch hardware communication? (y/n):
```
   - Enter `y` to connect to physical hardware
   - Enter `n` for simulation mode

2. Battery Status
```
   Enter current smartwatch battery percentage:
```
   - Input current battery level (0-100)

3. Temperature Input
```
   Enter current ambient temperature (°C):
```
   - Input current temperature in Celsius

4. Weather Data Source
```
   Enter 0 to use weather API or 1 to enter conditions manually:
```
   - `0` - Fetch forecast from weather API
   - `1` - Manually input weather condition

5. Manual Weather Input (if option 1 selected)
```
   Enter weather condition:
   1 for Sunny, 0 for Cloudy, -1 for Rainy
```

## System Architecture

### Core Functions

#### update_weekly_avg(current_temp)

Maintains a rolling 7-day temperature history and calculates the weekly average.

Parameters:
- `current_temp` (float): Current ambient temperature in Celsius

Returns:
- `weekly_avg` (float): Average temperature over available days

Behavior:
- Stores up to 7 daily temperature readings
- Implements FIFO queue when limit is reached
- Calculates mean temperature for baseline reference

#### autonomic_plane(current_temp, weekly_avg)

Detects temperature anomalies and performs automatic correction.

Parameters:
- `current_temp` (float): Current temperature reading
- `weekly_avg` (float): Weekly average temperature

Returns:
- `current_temp` (float): Validated or corrected temperature

Logic:
- If absolute difference between current_temp and weekly_avg is greater than 10°C, imputes with weekly average
- Prevents sensor errors from affecting charging decisions

#### get_weather_prediction(weather)

Maps weather condition strings to numeric prediction values.

Parameters:
- `weather` (str): Weather condition name

Returns:
- `int`: Prediction value (1, 0, or -1)

Mapping:

| Weather Condition | Value | Solar Potential |
|------------------|-------|-----------------|
| Clear | 1 | High (Sunny) |
| Clouds | 0 | Medium (Cloudy) |
| Mist, Fog | 0 | Medium (Cloudy) |
| Rain, Drizzle | -1 | Low (Rainy) |
| Thunderstorm | -1 | Low (Rainy) |
| Snow | -1 | Low (Rainy) |

#### manage_battery()

Main orchestration function that manages the entire battery optimization workflow.

Workflow:
1. Initialize hardware connection (if enabled)
2. Collect battery and temperature data
3. Process temperature through autonomic plane
4. Fetch or input weather prediction
5. Execute adaptive charging strategy
6. Send commands to PMU
7. Monitor PMU responses
8. Clean up and close connections

## Configuration

### Weather API Setup

Replace the API key in the code with your own:
```python
api_key = "your_openweathermap_api_key_here"
```

Get a free API key from OpenWeatherMap at https://openweathermap.org/api

### Serial Port Configuration

Modify the serial port settings if needed:
```python
smartwatch = serial.Serial('COM6', 9600, timeout=1)
```

Common Port Names:
- Windows: `COM1`, `COM3`, `COM6`, etc.
- Linux/Mac: `/dev/ttyUSB0`, `/dev/ttyACM0`, etc.

### Temperature Threshold

Adjust the anomaly detection threshold (default: ±10°C):
```python
if abs(current_temp - weekly_avg) > 10:
```

## Weather Prediction Logic

### Charging Strategies

#### Clear Weather (Prediction: 1)
```
Target Charge: 30%
Strategy: Solar-First
```

- Limits night charging to conserve grid power
- Relies on daytime solar charging
- Optimal for maximizing renewable energy use
- PMU Command: `b'0\n'` (Low-charge mode)

#### Cloudy Weather (Prediction: 0)
```
Target Charge: 70%
Strategy: Balanced
```

- Moderate charging for partial solar availability
- Ensures safe GPS operation
- Balance between solar reliance and power security
- PMU Command: `b'1\n'` (Moderate-charge mode)

#### Rainy Weather (Prediction: -1)
```
Target Charge: 80%
Strategy: Grid-Priority
```

- Higher charging due to low solar input
- Uses stored power sources (power bank)
- Ensures full functionality in adverse conditions
- PMU Command: `b'1\n'` (Full-charge mode)

### Critical Battery Protection

When battery level falls below 30%, the system immediately charges to 40% minimum to ensure:
- GPS functionality
- Zigbee connectivity
- System stability

This protection is triggered regardless of weather prediction.

## Examples

### Example 1: Sunny Day with Good Battery
```
Enable smartwatch hardware communication? (y/n): n
Enter current smartwatch battery percentage: 65
Enter current ambient temperature (°C): 28
Enter 0 to use weather API or 1 to enter conditions manually: 0
Fetching next day's weather forecast...
Forecast retrieved: Clear
Processing adaptive charging strategy based on weather prediction...
Clear weather predicted — solar charging expected.
Limiting night charging to 30%. Using solar energy during daylight.
[Simulated] Low-charge mode activated.
```

### Example 2: Rainy Day with Low Battery
```
Enable smartwatch hardware communication? (y/n): y
Connected to Smartwatch Power Management Unit (PMU)
Enter current smartwatch battery percentage: 25
Enter current ambient temperature (°C): 18
Enter 0 to use weather API or 1 to enter conditions manually: 1
Enter weather condition:
1 for Sunny, 0 for Cloudy, -1 for Rainy
-1
Battery critically low. Charging to 40% minimum for GPS/Zigbee readiness.
Sent charging signal to PMU.
PMU Response: Charging initiated at 1.2A
```

### Example 3: Temperature Anomaly Detection
```
Enable smartwatch hardware communication? (y/n): n
Enter current smartwatch battery percentage: 50
Enter current ambient temperature (°C): 45
Temperature deviation detected. Imputing 45.0 with weekly average 26.5.
Enter 0 to use weather API or 1 to enter conditions manually: 0
Fetching next day's weather forecast...
Forecast retrieved: Clouds
Processing adaptive charging strategy based on weather prediction...
Cloudy conditions predicted — partial solar availability.
Charging battery up to 70% for safe GPS operation.
[Simulated] Moderate-charge mode activated.
```

## Troubleshooting

### Common Issues

#### Serial Port Connection Failed
```
Error connecting to smartwatch: [Errno 2] could not open port 'COM6'
```

Solutions:
- Verify the correct COM port in Device Manager (Windows) or `ls /dev/tty*` (Linux/Mac)
- Check USB cable connection
- Ensure no other application is using the port
- Try a different USB port
- Run the program in simulation mode

#### Weather API Error
```
Error: HTTP Error 401: Unauthorized
```

Solutions:
- Verify your API key is correct
- Check API key activation (may take a few minutes)
- Ensure internet connectivity
- Check API rate limits

#### Import Error for mainnew
```
ModuleNotFoundError: No module named 'mainnew'
```

Solutions:
- Ensure `mainnew.py` is in the same directory
- Verify `mainnew.py` contains `fetch_weather()` function
- Check file permissions

### Hardware Communication Tips

- Timeout Issues: Increase timeout value if PMU is slow to respond
- Garbage Data: Add delay after opening serial connection
- Connection Drops: Implement retry logic or use simulation mode

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

### Development Priorities

- Machine learning-based weather prediction
- Historical charging pattern analysis
- Multi-day forecast integration
- Battery health monitoring and degradation tracking
- Solar panel efficiency metrics
- Mobile app interface
- Cloud data synchronization
- Multiple device support

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenWeatherMap for weather API services
- PySerial community for serial communication tools
- Contributors and testers

## Contact

For questions, suggestions, or support:
- GitHub Issues: Create an issue at https://github.com/yourusername/solar-smartwatch-battery-manager/issues
- Email: your.email@example.com

---

Disclaimer: This system is designed for educational and experimental purposes. Thoroughly test the system before deploying in production environments. The authors are not responsible for any damage to hardware or data loss resulting from the use of this software.

Version: 1.0.0
Last Updated: 2025
