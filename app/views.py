from flask import render_template, request, redirect

from app import app

FLAG = ""
STATUS = None
FILE = 'C:\\Users\\Starforge\\FLAG.TXT'

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
                    title='Lamp switcher',
                    flag=FLAG,
                    status=STATUS)

@app.route('/do', methods = ['GET'])
def do():
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

    return redirect("/", code=302)