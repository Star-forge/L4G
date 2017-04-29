from datetime import datetime

from flask import Flask
from flask import render_template, request, redirect
from flask_restful import Resource, Api
import time

FLAG = ""
STATUS = None
FILE = 'C:\\Users\\Starforge\\FLAG.TXT'

app = Flask(__name__)
api = Api(app)

def checkSTATUS():
    global FLAG, STATUS

    ff = open(FILE, 'r')
    FLAG = ff.read()
    ff.close()

    if(FLAG == 'ON'):
        STATUS = True
    elif(FLAG == 'OFF'):
        STATUS = False

@app.route('/')
@app.route('/index')
def index():
    global FLAG, STATUS
    checkSTATUS()
    return render_template("index.html",
                    title='Lamp switcher')

class WriteStatus(Resource):
    def get(self):
        global FLAG, STATUS
        checkSTATUS()
        if request.method == 'GET':
            request_flag = request.args.get('switchto', '')
            if(request_flag == 'ON'):
                ff = open(FILE, 'w')
                ff.write(request_flag)
                ff.close()
                FLAG = request_flag
            elif(request_flag == 'OFF'):
                ff = open(FILE, 'w')
                ff.write(request_flag)
                ff.close()
                FLAG = request_flag
            elif (request_flag == 'soft'):
                ff = open(FILE, 'w')
                ff.write('')
                ff.close()
                FLAG = ""

            request_flag = request.args.get('resp', '')
            if(request_flag):
                if(request_flag == '1'):
                    STATUS = True
                elif (request_flag == '2'):
                    STATUS = False

        return None

class StatusUpdate(Resource):
    def _is_updated(self, status_flag, manual_flag):
        global FLAG, STATUS
        checkSTATUS()
        if((STATUS != None) & (FLAG != None)):
            if((status_flag.lower() != str(STATUS).lower()) | (manual_flag.lower() != str(FLAG).lower())):
                return True
        return False

    def get(self):
        global FLAG, STATUS
        checkSTATUS()
        status_flag = request.args.get('status', 'true')
        manual_flag = request.args.get('flag', 'OFF')
        request_time = str(datetime.now())
        while not self._is_updated(status_flag, manual_flag):
            time.sleep(0.5)

        return {'status': STATUS,
                'flag': FLAG,
                'time': request_time}

class Status(Resource):
    def get(self):
        global FLAG, STATUS
        checkSTATUS()
        request_time = str(datetime.now())
        return {'status': STATUS,
                'flag': FLAG,
                'time': request_time}

api.add_resource(WriteStatus, '/do')
api.add_resource(StatusUpdate, '/status-update')
api.add_resource(Status, '/status')

if __name__ == '__main__':
    app.run(debug = False, threaded=True, host="192.168.1.100", port=9999)