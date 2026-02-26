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


      
