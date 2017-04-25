#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib3

import serial
from datetime import datetime, date, time

port = "COM2"
baud = 9600
COMMAND = ""
SERIAL_PORT = None

UTRO = [6, 0, 7, 0, True]
VECHER = [20, 0, 22, 0, True]
NOCH1 = [22, 0, 23, 59, False]
NOCH2 = [0, 0, 6, 0, False]
LIGHT_PERIODS = []
LIGHT_PERIODS.append(UTRO)
LIGHT_PERIODS.append(VECHER)
LIGHT_PERIODS.append(NOCH1)
LIGHT_PERIODS.append(NOCH2)
SERVER_ADDR = "217.71.231.9:9999"

FLAG = ""
SoftFLAG = ""
LIGHT_POWER_LEVEL_MIN = 70
LIGHT_POWER_LEVEL_MAX = 103
LIGHT_POWER = 0
# Average LIGHT_POWER - of last 5 datas
LIGHT_POWER_AVG = 0
LIGHT_POWER_AVG_LIST = []

# Подсчет среднего значения показаний датчика
def getAVG_LIGHT_POWER():
    global LIGHT_POWER_AVG, LIGHT_POWER_AVG_LIST, LIGHT_POWER
    # Если значений меньше 5, то список заполняется дублями
    while (len(LIGHT_POWER_AVG_LIST) < 6):
        LIGHT_POWER_AVG_LIST.append(LIGHT_POWER)
    LIGHT_POWER_AVG_LIST.pop(0)

    lp_avg = 0
    for lp in LIGHT_POWER_AVG_LIST:
        lp_avg += lp
    LIGHT_POWER_AVG = int(lp_avg / 5)
    # print("LIGHT_POWER_AVG =",LIGHT_POWER_AVG)

def time_in_range(start, end, x):
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

# Проверка времени
def checkTimes():
    global LIGHT_PERIODS
    for min_hour, min_minute, max_hour, max_minute, command in LIGHT_PERIODS:
        # Если входит в диапазон
        start = time(min_hour, min_minute, 0)
        end = time(max_hour, max_minute, 0)
        now = datetime.time(datetime.now())
        if(time_in_range(start, end, now)):
            return command
    # print(start, end, now)
    return None

def readLPConf():
    # Чтение конфига с уровнями освещения
    ff = open("LIGHT_POWER_LEVEL.TXT", 'r')
    Light_power_levels = ff.read()
    ff.close()
    return int(Light_power_levels.split("-")[0]), int(Light_power_levels.split("-")[1])

# Проверка уровня освещения
def checkLightPower():
    global SoftFLAG, LIGHT_POWER_LEVEL_MIN, LIGHT_POWER_AVG, LIGHT_POWER_LEVEL_MAX

    # Чтение конфига с уровнями освещения
    LIGHT_POWER_LEVEL_MIN, LIGHT_POWER_LEVEL_MAX = readLPConf()

    # Проверка показаний датчика
    # Если входит в диапазон
    if (LIGHT_POWER_LEVEL_MAX > LIGHT_POWER_AVG > LIGHT_POWER_LEVEL_MIN):
        return False
    # Если НЕ входит в диапазон, 2 сделано для отсечки частых переключений
    elif ((LIGHT_POWER_AVG > LIGHT_POWER_LEVEL_MAX + 2) | (LIGHT_POWER_AVG < LIGHT_POWER_LEVEL_MIN - 2)):
        return True
    # print(LIGHT_POWER_LEVEL_MIN, LIGHT_POWER_AVG, LIGHT_POWER_LEVEL_MAX)
    return None

def checkFLAG():
    global SoftFLAG, FLAG, COMMAND, LIGHT_POWER, LIGHT_POWER_LEVEL_MIN, LIGHT_POWER_AVG, LIGHT_POWER_LEVEL_MAX
    ff = open("FLAG.TXT", 'r')
    FLAG = ff.read()
    ff.close()

def checkFlag():
    global SoftFLAG, FLAG, COMMAND, LIGHT_POWER, LIGHT_POWER_LEVEL_MIN, LIGHT_POWER_AVG, LIGHT_POWER_LEVEL_MAX
    ff = open("FLAG.TXT", 'r')
    FLAG = ff.read()
    ff.close()
    ret_code = 1

    ff = open("LIGHT_POWER_LEVEL.TXT", 'r')
    Light_power_levels = ff.read()
    Light_power_level_min, Light_power_level_max = Light_power_levels.split("-")
    LIGHT_POWER_LEVEL_MIN = int(Light_power_level_min)
    LIGHT_POWER_LEVEL_MAX = int(Light_power_level_max)
    ff.close()

    # Проверка показаний датчика
    if (LIGHT_POWER_LEVEL_MAX > LIGHT_POWER_AVG > LIGHT_POWER_LEVEL_MIN):
        SoftFLAG = "ON"
    elif ((LIGHT_POWER_AVG > LIGHT_POWER_LEVEL_MAX + 2) | (LIGHT_POWER_AVG < LIGHT_POWER_LEVEL_MIN - 2)):
        SoftFLAG = "OFF"

    if (((FLAG == "ON") | (SoftFLAG == "ON")) & (COMMAND != "1") & (FLAG != "OFF")):
        print('Set COMMAND = 1, FLAG =', FLAG, 'SoftFLAG =', SoftFLAG, 'COMMAND =', COMMAND)
        COMMAND = "1"
        SERIAL_PORT.write(COMMAND.encode('ascii'))
        return ret_code
    elif ((FLAG == "OFF") & (COMMAND != "2")):
        print('-Set COMMAND = 2, FLAG =', FLAG, 'SoftFLAG =', SoftFLAG, 'COMMAND =', COMMAND)
        COMMAND = "2"
        SERIAL_PORT.write(COMMAND.encode('ascii'))
        return ret_code
    elif ((FLAG != "OFF") & (FLAG != "ON") & (COMMAND != "2") & (SoftFLAG == "OFF")):
        print('Set COMMAND = 2, FLAG =', FLAG, 'SoftFLAG =', SoftFLAG, 'COMMAND =', COMMAND)
        COMMAND = "2"
        SERIAL_PORT.write(COMMAND.encode('ascii'))
        return ret_code
    elif ((FLAG == "ON") | (FLAG == "OFF")):
        # print('No doing', FLAG, SoftFLAG, COMMAND)
        return ret_code
    else:
        return 0

def checkTime():
    global COMMAND, SERIAL_PORT, LIGHT_PERIODS, LIGHT_POWER, LIGHT_POWER_LEVEL
    com = COMMAND
    for _hour, _minute, _command in LIGHT_PERIODS:
        if ((int(datetime.today().hour) >= int(_hour)) & (int(datetime.today().minute) >= int(_minute)) & (
            _command != com)):
            com = _command
    if (com != COMMAND):
        print('Set COMMAND =', com, 'OLD COMMAND =', COMMAND)
        COMMAND = com;
        SERIAL_PORT.write(COMMAND.encode('ascii'))


if __name__ == "__main__":
    _str = ""
    COMMAND = "2"
    SoftFLAG = False
    try:
        SERIAL_PORT = serial.Serial(port, baud, timeout=1)
    except serial.serialutil.SerialException as se:
        print("Permission Error. Port in use. Exit.")
        exit()
    # open the serial port
    if SERIAL_PORT.isOpen():
        filename = 'svet' + str(date.today()) + ".log"

        print(SERIAL_PORT.name + ' is open...')
        SERIAL_PORT.write(COMMAND.encode('ascii'))
    while True:
        try:
            line = SERIAL_PORT.readline()
            today = datetime.now()
            _str = str(line.decode("utf-8")).strip()
            if((len(_str) > 0) & (_str.startswith("data"))):
                lp, resp = _str.split()
                LIGHT_POWER = int(lp[4:])
                getAVG_LIGHT_POWER()
                _str = str(today) + "," + str(LIGHT_POWER) + "," + str(resp)
                print(today, " lp =", LIGHT_POWER, " resp =", resp)
                http = urllib3.PoolManager()
                URL = SERVER_ADDR + "/do?lp=" + str(LIGHT_POWER) + "&resp=" + str(resp)
                response = http.request('GET', URL)
                if datetime.hour == datetime.minute == datetime.second == 0:
                    filename = 'svet' + str(date.today()) + ".log"
                f = open(filename, 'a')
                if (f):
                    f.write("\n" + _str)
                    f.flush()
                    f.close()
                else:
                    print("File Error")
            elif (len(_str) > 0):
                print(today, _str)

            try:
                checkFLAG()
                SFLAG = SoftFLAG
                com = COMMAND
                ct = None
                clp = None
                if(FLAG == 'ON'):
                    COMMAND = "1"
                elif (FLAG == 'OFF'):
                    COMMAND = "2"
                else:
                    ct = checkTimes()
                    if(ct != None):
                        SFLAG = ct

                    clp = checkLightPower()
                    if (clp != None):
                        SFLAG = clp | SFLAG

                    if(SFLAG):
                        COMMAND = "1"
                    elif(SFLAG == False):
                        COMMAND = "2"
                # print('COMMAND =', COMMAND, 'FLAG =', FLAG, 'SoftFLAG =', SFLAG, 'OLD COMMAND =', com, ct, clp)
                SoftFLAG = SFLAG
                if (com != COMMAND):
                    SERIAL_PORT.write(COMMAND.encode('ascii'))

            except IOError as e:
                print(e)
                pass
            #
            # if (checkFlag() == 0):
            #     checkTime()
            #     # elif(checkFlag() == -1):
            #     #     checkTime()


        except OSError:
            print('cannot open')



