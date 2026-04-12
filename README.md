# GCS-Integration-Library-2025-26

  ## First time cloning the repository
  ```
  git clone --recursive https://github.com/ngcp-project/GCS-Integration-Library-2025-26.git
  ```
  ## Already cloned the repository, but did not initialized the submodules
  ```
  git submodule update --init --recursive
  ```
  ## Update submodules to the latest commit tracked by the repository
  ```
  git pull --recurse-submodules
  ```
  ## Bring the latest update from external repositories
  ```
  git submodule update --remote --merge --recursive
  ```

  ## Important external repository information:
  ### Xbee-python 

  https://github.com/ngcp-project/xbee-python
  
  #### Install dependencies
  ```
  pip3 install -e Submodules/xbee_python 
  ```
  ### GCS-Infrastructure 
  
  https://github.com/ngcp-project/gcs-infrastructure

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
Saved it usinf  esc + wq

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


      
