## Pump Monitoring App
An application for energy efficiency and performance monitoring of a pump system, made with Dash. As part of a Industrial Internet of Things system, this app serves as the application layer. Using MQTT messaging protocol, the app receives sensor and instrument data installed on a pump system and display the processed data in a web- based application.
The app should be running together along with already-scripted gateway connected with the pump system or the bottom layer. 


This app is still on the development stage and should not deployed publicly as I have not implemented the security yet.

## Quick Start
Install required modules in requirements.txt
```
pip3 install -r requirements.txt
```
Launch the app (depending on the system but it has to run with Python 3) 
```
python3 run.py
```
or
```
python run.py
```
