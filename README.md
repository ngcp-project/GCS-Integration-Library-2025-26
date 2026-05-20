# GCS-Integration-Library-2025-26

## Getting Started
1. ```git clone --recursive https://github.com/ngcp-project/GCS-Integration-Library-2025-26.git```

At the root of the project:

2. ```git checkout dev```
3. ```cd lib```
4. ```git submodule update --init --recursive```
> [!NOTE]
> Initializes the 3 submodules: gcs-infrastructure, gcs-packet, and xbee-python. It is important all submodules (including submodules of submodules) are in the lib folder for smooth imports. DO NOT CHANGE THIS. 
5. ```cd ..```
6. create a .venv (python virtual environment) through VSCode.
7. ```pip install -r requirements.txt```

### For Python 3.11+ | Modifications for lib/gcs-packet/Telemetry/Telemetry.py

Line 2 | Add this import
```
from typing import Self
```
Line 48 | Change "Telemetry" to "Self"
```
def Decode(BinaryData) -> Self:
```

### Cheking if submodules have been installed correctly: 
1. open Testing/GCSTest.py in your IDE (like VSCode)
  - This file showcases how to use all of infrastructure's features from the submodules
  - if imports are underlined in yellow, proceed anyway
2. click the run button
3. If you do not have an Xbee connected, this is the expected output:
```
[INFO] LOGGER CREATED By XBee.py
[INFO] port: COM4, baudrate: 115200, timeout: 0.1, config_file: None
[INFO] Attempting to open serial XBee connection.
[INFO] Error opening serial port: could not open port 'COM4': FileNotFoundError(2, 'The system cannot find the file specified.', None, 2)
Error: could not open port 'COM4': FileNotFoundError(2, 'The system cannot find the file specified.', None, 2)
[INFO] Serial port is already closed.
[INFO] Serial port is already closed.
Command Queued
Command Queued
Command Queued
```
As long as there are no errors when running GCSTest.py, then the submodule imports are working. 

4. End the program with Ctrl+C

## Update submodules to the latest commit tracked by the repository

```
git pull --recurse-submodules
```

## Bring the latest update from external repositories

```
git submodule update --remote --merge --recursive
```

## Submodule Repos:

### gcs-infrastructure 
  
  https://github.com/ngcp-project/gcs-infrastructure

### xbee-python

  https://github.com/ngcp-project/xbee-python

### gcs-packet 
  
  https://github.com/ngcp-project/gcs-packet

## Run script (xbee_tag_gcs.py)

On the root directory

```
python3 -m Testing.xbee_tag_gcs
```

For now to solve this problem:
<img width="1874" height="224" alt="image" src="https://github.com/user-attachments/assets/7d758705-f28f-4bad-ace1-ec5a5bacf576" />

Add this:
<img width="1716" height="124" alt="image" src="https://github.com/user-attachments/assets/ef465957-0ac1-405d-8a61-68ca8e67b51b" />

## Set up Xbee Emulator

https://github.com/ngcp-project/xbee-python/blob/main/docs/xbee_emulator.md

## Modifications XbeeEmulator.py

Line 61:

```
self.client = MqttClient(str(pan_id), self.mac_address, on_rf=self._on_mqtt, use_tls=False)
```

Modify this:

<img width="594" height="110" alt="image" src="https://github.com/user-attachments/assets/54e7dd24-a757-469d-b465-a71652b5c086" />

## Modifications x81.py

Line 3

```
 def __init__(self, frame_type, source_address, rssi, options: int, data):
```

## Set up MQTT broker:

Complete steps to setup MQTT broker:

```
brew install mosquitto
```

create file -> vim local.conf
add this info inside:

```
listener 1883
allow_anonymous true
```

Saved it usinf esc + wq

Then tell mosquito to use it

```
/opt/homebrew/sbin/mosquitto -c local.conf -v
```

-c will tell the use that file
-v to see the logs

You are gonna see this:
<img width="2722" height="800" alt="image" src="https://github.com/user-attachments/assets/21c20f79-edb2-4549-9aeb-25d001bcee8f" />

Run these files:

```
python3 -m Testing.xbee_tag_gcs
```

```
python3 -m Testing.xbee_tag_vehicle
```
