#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import threading

import urllib3
from terminaltables import AsciiTable
import serial
from datetime import datetime, date, time

port = "COM2"
baud = 9600
COMMAND = ""
SERIAL_PORT = None

TIME_ON = [6, 0, 22, 0, True]
TIME_OFF = [0, 0, 23, 59, False]
FLAGTXT = "C:\\Users\\Starforge\\FLAG.TXT"
LIGHT_POWER_LEVELTXT = "C:\\Users\\Starforge\\LIGHT_POWER_LEVEL.TXT"

LIGHT_PERIODS = []
LIGHT_PERIODS.append(TIME_ON)
LIGHT_PERIODS.append(TIME_OFF)
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
    ff = open(LIGHT_POWER_LEVELTXT, 'r')
    Light_power_levels = ff.read()
    ff.close()
    return int(Light_power_levels.split("-")[0]), int(Light_power_levels.split("-")[1])

# Проверка уровня освещения
def checkLightPower():
    global SoftFLAG, LIGHT_POWER_LEVEL_MIN, LIGHT_POWER_AVG, LIGHT_POWER_LEVEL_MAX

    # Чтение конфига с уровнями освещения
    LIGHT_POWER_LEVEL_MIN, LIGHT_POWER_LEVEL_MAX = readLPConf()

    # Проверка показаний датчика
    # Если входит в диапазон когда надо подсвечивать
    if (LIGHT_POWER_LEVEL_MAX > LIGHT_POWER_AVG > LIGHT_POWER_LEVEL_MIN):
        return True
    # Если НЕ входит в диапазон, 2 сделано для отсечки частых переключений
    elif ((LIGHT_POWER_AVG > LIGHT_POWER_LEVEL_MAX + 2) | (LIGHT_POWER_AVG < LIGHT_POWER_LEVEL_MIN - 2)):
        return False
    # print(LIGHT_POWER_LEVEL_MIN, LIGHT_POWER_AVG, LIGHT_POWER_LEVEL_MAX)
    return None

def checkFLAG():
    global SoftFLAG, FLAG, COMMAND, LIGHT_POWER, LIGHT_POWER_LEVEL_MIN, LIGHT_POWER_AVG, LIGHT_POWER_LEVEL_MAX
    ff = open(FLAGTXT, 'r')
    FLAG = ff.read()
    ff.close()

def fetch(SERVER_ADDR, LIGHT_POWER, resp):
    http = urllib3.PoolManager()
    URL = SERVER_ADDR + "/do?lp=" + str(LIGHT_POWER) + "&resp=" + str(resp)
    return http.request('GET', URL, )

def print2console(today, lp, resp, flag, sflag, old_com, new_com, ct, clp):
    flag = "Light " + flag if (flag == "ON") | (flag == "OFF") else "Switched OFF"
    sflag = "Light ON" if sflag == "True" else "Light OFF"
    old_com = "ON" if old_com == "1" else "OFF"
    new_com = "ON" if new_com == "1" else "OFF"
    resp = "Light ON" if resp == "1" else "Light OFF"

    date_info =                 "Date = "+ today
    lp_info =                   "Light power = "+ lp.zfill(3)
    resp_info =                 "Response = "+ resp
    manual_status =             "Manual status = "+ flag
    soft_status =               "Soft status   = " + sflag
    old_command_info =          "Old command = " + old_com
    new_command_info =          "New command = " + new_com
    check_time_info =           "Check time  = " + ct
    check_light_power_info =    "Check light = " + clp

    table_data = [
        [date_info, lp_info, resp_info],
        [manual_status, old_command_info, check_time_info],
        [soft_status, new_command_info, check_light_power_info],
    ]
    table = AsciiTable(table_data)

    os.system('cls' if os.name == 'nt' else 'clear')
    print (table.table)

if __name__ == "__main__":
    _str = ""
    COMMAND = "2"
    SoftFLAG = False
    lp, resp = 0, 0
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
            # print(line)
            today = datetime.now()
            _str = str(line.decode("utf-8")).strip()
            if((len(_str) > 0) & (_str.startswith("data"))):
                lp, resp = _str.split()
                LIGHT_POWER = int(lp[4:])
                getAVG_LIGHT_POWER()
                _str = str(today) + "," + str(LIGHT_POWER) + "," + str(resp)

                # print(today, " lp =", LIGHT_POWER, " resp =", resp) change to print2console

                # Отправка данных на веб сервер
                threading.Thread(target=fetch, args=[SERVER_ADDR, LIGHT_POWER, resp]).start()

                now = datetime.time(datetime.now())
                if((now.hour >= 0) & (now.minute >= 0)):
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
                        SFLAG = clp & SFLAG

                    if(SFLAG):
                        COMMAND = "1"
                    elif(SFLAG == False):
                        COMMAND = "2"

                print2console(str(today), str(LIGHT_POWER), str(resp), str(FLAG), str(SFLAG), str(com), str(COMMAND), str(ct), str(clp))

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



