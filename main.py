'''
tomte main application code
'''
import gc
import machine
import socket
import time

features = [machine.Pin(16, machine.Pin.OUT), machine.Pin(17, machine.Pin.OUT), machine.Pin(21, machine.Pin.OUT)]

on_string = "on"
off_string = "off"
feature_light_id = "light"
feature_heater_id = "heater"
feature_knock_id = "knock"

feature_light_state = False
feature_heater_state = False
feature_knock_state = False
feature_state_suffix = "_state"

def features_html():
    features_list = [
        (feature_light_id, feature_light_state),
        (feature_heater_id, feature_heater_state),
        (feature_knock_id, feature_knock_state)]
    features_table_html = f"""<table style="width:100%">"""

    for feature_id, feature_state in features_list:        
        features_table_html += f"""<tr>
    <td> </td>
    <td><p>State: <strong id=\"{feature_id + feature_state_suffix}\">{feature_state}</strong></p></td>
    <td>
    <p>
        <a ><button class="button" id=\"{feature_id}\" onclick="button_click(this.id)">{feature_id}</button></a>
    </p>
    </td>
    </tr>
    """    
    features_table_html += """</table>"""

    return features_table_html

def web_page():
    html = """<html>

<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css"
     integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">
    <style>
        html {
            font-family: Arial;
            display: inline-block;
            margin: 0px auto;
            text-align: center;
        }

        .button {
            background-color: #ce1b0e;
            border: none;
            color: white;
            padding: 16px 40px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
        }

        .button_off {
            background-color: #000000;
        }
    </style>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
</head>

<body>
    <h2>Tomte</h2> """ + features_html() + """
    <script>
    function button_click(id) {
        $.ajaxSetup({timeout:1000});
        $.get(id);
        {Connection.close()};
    }

    function updateFeatureStates() {
        var xmlRequest = new XMLHttpRequest();
        xmlRequest.open('GET', 'getFeatureStates', true);
        xmlRequest.onreadystatechange = function()
        {            
            if(xmlRequest.readyState == 4 && xmlRequest.status==200)
            {
                var response = xmlRequest.responseText;
                var states = response.split("|");
                
                if (states.length > 1){
                    document.getElementById("light_state").innerHTML = states[0];
                    document.getElementById("heater_state").innerHTML = states[1];
                    document.getElementById("knock_state").innerHTML = states[2];
                }
            }   
        }  
        xmlRequest.send();
    }
    
    setInterval(updateFeatureStates, 2000);

    </script>
</body>

</html>"""
    return html

def toggle_light():
    global feature_light_state
    feature_light_state = not feature_light_state
    print("*** TOGGLE LIGHT ***")

def toggle_heater():
    global feature_heater_state
    feature_heater_state = not feature_heater_state
    print("*** TOGGLE HEATER ***")

def toggle_knock():
    global feature_knock_state
    feature_knock_state = not feature_knock_state
    print("*** TOGGLE KNOCK ***")

# create and bind socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 80))
s.listen(1)

# main loop
while True:
    try:
        if gc.mem_free() < 102000:
            gc.collect()
        conn, addr = s.accept()
        conn.settimeout(3.0)
        print('Received HTTP GET connection request from %s' % str(addr))
        request = conn.recv(1024)
        conn.settimeout(None)
        request = str(request)
        response = ''
        print('GET Request Content = %s' % request)

        update = request.find('getFeatureStates')

        if (update == 7):
            response = '|'.join(['ON' if s else 'OFF' for s in [feature_light_state, feature_heater_state, feature_knock_state]])
        else:
            features_list = [
                (feature_light_id, feature_light_state, toggle_light),
                (feature_heater_id, feature_heater_state, toggle_heater),
                (feature_knock_id, feature_knock_state, toggle_knock)]

            for feature_string, feature_status, feature_func in features_list:
                feature_toggle = request.find(feature_string)

                if feature_toggle != -1:
                    feature_func()

            response = web_page()

        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()
    except OSError as e:
        conn.close()
        print('Connection closed')
