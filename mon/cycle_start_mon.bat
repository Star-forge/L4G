cd ..\..\..\
call ARD_ENV\Scripts\activate.bat
cd PycharmProjects\L4G\mon
:start_mon
python l4g_mon.py
goto start_mon