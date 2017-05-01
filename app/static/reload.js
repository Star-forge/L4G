var STATUS = true;
var FLAG = "";

function updateElems(data){
    timeupdate = ''
    flagupdate = ''
    statusupdate = ''
    STATUS = data.status;
    FLAG = data.flag;
    if(FLAG == 'ON')
    {
        $('#autobutton').css('display','block');
        $('#manualon').css('display','block');
        $('#manualoff').css('display','none');
    }
    else if(FLAG == 'OFF'){
        $('#autobutton').css('display','block');
        $('#manualon').css('display','none');
        $('#manualoff').css('display','block');
    }
    else
    {
        $('#autobutton').css('display','none');
        $('#manualon').css('display','none');
        $('#manualoff').css('display','none');
    }

    if(STATUS == true){
        $('#status').text("Свет включен.");
        $('#ibutton').attr('src', "\\static\\switch-on-button.png");
        $('#abutton').attr('href', "javascript:switchto('OFF');");
    }
    else
    {
        if(STATUS == false){
            $('#status').text("Свет выключен.");
            $('#ibutton').attr('src', "\\static\\switch-off-button.png");
            $('#abutton').attr('href', "javascript:switchto('ON');");
        }
        else
        {
            $('#status').text("Статус не известен."+STATUS);
            $('#ibutton').attr('src', "\\static\\switch-off-button.png");
            $('#abutton').attr('href', "javascript:switchto('ON');");
        }
    }
    $('#timeupdate').text("["+data.time+"]");
    $('#flagupdate').text("["+FLAG+"]");
    $('#statusupdate').text("["+STATUS+"]");
}

function switchto(status) {
    $.ajax({
        url: '/do?switchto='+status,
        success:  function(data) {
            updateElems(data);
            $('#error').text("")
        },
        error: function(xhr, status, error) {
            $('#error').text("Зафиксирована ошибка:."+error);
        }
    });
}

function chkErrMsg() {
    $.ajax({
        url: '/status-update?status='+STATUS+"&flag="+FLAG+"&now=yes",
        success: function(data) {
            updateElems(data);
            $('#error').text("")
        },
        timeout: 5000,//If timeout is reached run again
        error: function(jqXHR, exception)
        {
            if (jqXHR.status === 0) {
                 $('#error').text('НЕ подключен к интернету!');
            } else if (jqXHR.status == 404) {
                $('#error').text('НЕ найдена страница запроса [404])');
            } else if (jqXHR.status == 500) {
                 $('#error').text('НЕ найден домен в запросе [500].');
            } else if (exception === 'parsererror') {
                $('#error').text("Ошибка в коде: \n"+jqXHR.responseText);
            } else if (exception === 'timeout') {
                $('#error').text('Не ответил на запрос.');
            } else if (exception === 'abort') {
                 $('#error').text('Прерван запрос Ajax.');
            } else {
                 $('#error').text('Неизвестная ошибка:\n' + jqXHR.responseText);
            }
            chkErrMsg();
        }
    });
}

/**
 * Request an update to the server and once it has answered, then update
 * the content and request again.
 * The server is supposed to response when a change has been made on data.
 */
function update() {
    $.ajax({
        url: '/status-update?status='+STATUS+"&flag="+FLAG,
        success: function(data) {
            updateElems(data);
            $('#error').text("")
        },
        timeout: 600000,//If timeout is reached run again
        error: function(jqXHR, exception)
        {
            if (jqXHR.status === 0) {
                 $('#error').text('НЕ подключен к интернету!');
            } else if (jqXHR.status == 404) {
                $('#error').text('НЕ найдена страница запроса [404])');
            } else if (jqXHR.status == 500) {
                 $('#error').text('НЕ найден домен в запросе [500].');
            } else if (exception === 'parsererror') {
                $('#error').text("Ошибка в коде: \n"+jqXHR.responseText);
            } else if (exception === 'timeout') {
                $('#error').text('Не ответил на запрос.');
            } else if (exception === 'abort') {
                 $('#error').text('Прерван запрос Ajax.');
            } else {
                 $('#error').text('Неизвестная ошибка:\n' + jqXHR.responseText);
            }
            chkErrMsg();
        },
        complete: function(data) {
            update();
        }
    });
}

/**
 * Perform first data request. After taking this data, just query the
 * server and refresh when answered (via update call).
 */
function load() {
    $.ajax({
        url: '/status',
        success: function(data) {
            update();
            updateElems(data);
        }
    });
}

$(document).ready(function() {
    load();
});