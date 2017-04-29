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
    update();
}

function switchto(status) {
    $.ajax({
        url: '/do?switchto='+status,
        success:  function(data) {
            updateElems(data);
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
        success:  function(data) {
            updateElems(data);
        },
        timeout: 500000 //If timeout is reached run again
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
            updateElems(data);
        }
    });
}

$(document).ready(function() {
    load();
});