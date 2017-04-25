# L4G
Intelligent lighting system for plant growth
  
Based on arduino + radio module with REST-api backend and simple web-page for contol LEDs  
System contains 4 subsystem:   
* LED and Sensor Controller (LSC) - get data from light sensor and control power on LED via power-switch. All data can be sent via radio module.
* USB-Stick - COM-Radio bridge
* PC-based Controller - read and write data into COM-port and analysis data for backend
* Backend - Flask REST-api web-server
