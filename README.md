# L4G
Intelligent lighting system for plant growth
    
Based on arduino + radio module with REST-api backend and simple web-page for contol LEDs  
System contains 4 subsystem:   
* **LED and Sensor Controller (LSC)** - get data from light sensor and control power on LED via power-switch. All data can be sent via radio module.
* **USB-Stick - COM-Radio bridge**
* **PC-based Controller (monitor)** - read and write data into COM-port and analysis data for backend
* **Backend** - Flask REST-api web-server
  
### Screenshots
![PC-based Controller (monitor)](https://github.com/Star-forge/L4G/raw/master/docs/img/monitor.png)
  
**Date** - last information update datetime  
**Light power** - raw data from sensor  
**Response** - status of lighting system on arduino in human style.
May be *Light ON* or *Light OFF*  
**Manual status** - manual swither info (from FLAG.TXT).
May be *Swithed OFF* or *Light ON/OFF*  
**Soft status** - status of soft switcher.
That check data from sensor (*Check light*) and timings (*Check time*)
and switch on/off lighting system. May be *Light ON* or *Light OFF*  
**Old command** and **New command** - values of variables,
that stores commands of intellegent system and that may sent to arduino.  
**Check time** - result check: is needed switch ON/OFF by timer.  
**Check light** - result check: is needed switch ON/OFF by sensor data.  
  
Priority:  
1. Manual switcher  
2. Soft swither  
    2.1. Time check  
    2.2. Light check  

![Site](https://github.com/Star-forge/L4G/raw/master/docs/img/site.PNG)
