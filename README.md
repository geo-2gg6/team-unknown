# Privacy Scanner - Cloud + Local Agent

A privacy monitoring system that runs a cloud dashboard on Render and local agents on devices to monitor network traffic in real-time.

## Architecture

- **Cloud Backend** (Render): Receives and displays data from multiple devices
- **Local Agent** (Device): Monitors network activity and sends to cloud

## Setup

### 1. Deploy to Render

1. Push this code to GitHub
2. Connect to Render
3. Deploy as a Web Service
4. Note your Render URL (e.g., `https://your-app.onrender.com`)

### 2. Run Local Agent

On each device you want to monitor:

```bash
# Install dependencies
pip install psutil requests

# Run the agent
python local_agent.py
```

When prompted, enter your Render URL.

## Features

- **Real-time monitoring**: Live network activity from your devices
- **Multi-device support**: Monitor multiple devices from one dashboard
- **Smart classification**: Safe/Risk/Caution based on destinations
- **Process tracking**: See which apps are making connections
- **Cloud dashboard**: Access from anywhere

## How It Works

1. Local agent runs on your device using `psutil` to monitor TCP connections
2. Agent classifies connections as Safe/Risk/Caution based on destination patterns
3. Agent sends data to your cloud backend every 5 seconds
4. Cloud dashboard displays real-time activity from all connected devices

## Classification Rules

- **Safe**: Trusted domains (google.com, microsoft.com, etc.) + web ports (80, 443)
- **Risk**: Known risky patterns (trackers, ads) + dangerous ports (21, 23, 25, etc.)
- **Caution**: Everything else

## Security

- Each device gets a unique ID based on hostname + MAC
- No sensitive data is stored permanently
- All communication is over HTTPS

## Troubleshooting

- **No data showing**: Make sure local agent is running and connected
- **Permission errors**: Run local agent as administrator on Windows
- **Connection issues**: Check your Render URL and internet connection
