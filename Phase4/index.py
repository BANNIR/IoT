import dash.dependencies
import dash_daq as daq
from dash import html, Input, Output, dcc, Dash, State
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO
import RPi.GPIO as GPIO
import time
import Freenove_DHT as DHT
import mail_client as email
from datetime import datetime
import random
from paho.mqtt import client as mqtt_client
import paho.mqtt.publish as publish
import random
from datetime import datetime
import pytz
import sqlite3
from sqlite3 import Error
import CRUD as db

temp = 0
light = 0
humidity = 0

lastSentTime = int(time.time())
lastReadTime = email.read_mail_timestamp(email.get_mail_ids(1)[0])
isSendEligible = True

broker = '192.168.0.119'
port = 1883
topic = "IoTlab/light"
# generate client ID with pub prefix randomly
client_id = f"python-mqtt-{random.randint(0, 100)}"

message ="0"
tag_num = "CCC79463"
prevTag = ""

GPIO.setmode(GPIO.BCM) # BCM
GPIO.setwarnings(False)
_ledPin = 21
GPIO.setup(_ledPin, GPIO.OUT)
EMAIL_SEND = False

DHTPin = 17 
dht = DHT.DHT(DHTPin) #create a DHT class object
dht.readDHT11()

Motor1 = 27
Motor2 = 18
Motor3 = 22
GPIO.setup(Motor1,GPIO.OUT)
GPIO.setup(Motor2,GPIO.OUT)
GPIO.setup(Motor3,GPIO.OUT)

def startMotor():
    GPIO.output(Motor1,GPIO.HIGH)
    GPIO.output(Motor2,GPIO.LOW)
    GPIO.output(Motor3,GPIO.HIGH)
    time.sleep(10)
    GPIO.output(Motor1, GPIO.LOW)

#Phase3 pin
intensityPin = 13 #33 in GPIO.BOARD
GPIO.setup(intensityPin, GPIO.OUT)


global current_light_intensity
currentLightIntensity = 0
global lightIntensity

app = Dash(__name__)
img = html.Img(src=app.get_asset_url('lightOffp'),width='100px', height='100px')
humidityValue = 0
temperatureValue = 0
tempUnit = 'Celsius'
emailSent = False
emailReceived = 0


theme_change = ThemeChangerAIO(aio_id="theme");

offcanvas = html.Div(
    [
        dbc.Button(
              "Profile", id="open-offcanvas-backdrop",style={'padding': '10%', 'border': 'none', 'background': 'none'}
        ),
        dbc.Offcanvas(
            html.Div(
            [                       
                html.Div(style={'text-align': 'center'},children=[
                      html.Img(src=app.get_asset_url('avatar.png'), width='50%', height='50%', style={'border-radius': '50%'})
            ]),
                dbc.Row(
                [
                    dbc.Col(html.Div("Name: ")),
                    dbc.Col(html.Div(dbc.Input(placeholder="username", size="md", className="mb-3", readonly=True, id="user", value=tag_num))),
                ]),
                dbc.Row(
                [
                    dbc.Col(html.Div("Ideal Temperature: ")),
                    dbc.Col(html.Div(dbc.Input(placeholder="ideal_temp", size="md", className="mb-3", readonly=True, id="temp", value=0))),
                ]),
                dbc.Row(
                [
                    dbc.Col(html.Div("Ideal Humidity: ")),
                    dbc.Col(html.Div(dbc.Input(placeholder="ideal_humidity", size="md", className="mb-3", readonly=True, id="humid", value=0))),
                ]),
                dbc.Row(
                [
                    dbc.Col(html.Div("Ideal light intensity: ")),
                    dbc.Col(html.Div(dbc.Input(placeholder="ideal_light_intensity", size="md", className="mb-3", readonly=True, id="light", value=0))),
                ]),
                dbc.Row(
                [   
                    dbc.Col(html.Div(theme_change, style={'padding': 0, 'border': 'none', 'background': 'none'})),
                ]), dcc.Interval(id='mqtt2', interval = 1 * 1500, n_intervals=0)
            ]),
            id="offcanvas-backdrop",
            title="User Information",
            is_open=False,
        ),
    ]
)

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink(offcanvas), style={'text-align': 'end'})
    ],
    brand="SMARTHOME",
    brand_href="#",
    color="dark",
    dark=True,
    sticky='top'
)

cardLedBox = dbc.Card([
    dbc.CardHeader([
         html.H2(children="LED", className="card-title, text-center")
    ]),
    dbc.CardBody([
        html.Div(children=[
                html.H1(children='LED'),
                html.P("Light Intensity: ", id="light_intensity"),
                html.Div(img, id='led-image', n_clicks = 0),
                dbc.Toast(
                    "An email has been sent!",
                    id="notification",
                    header="LED WARNING",
                    is_open=False,
                    dismissable=True,
                    icon="danger",
                    # top: 66 positions the toast below the navbar
                    style={"position": "fixed", "top": 75, "right": 10, "width": 350},
                ),
                dcc.Interval(id='mqtt', interval = 1 * 1500, n_intervals=0),
                html.P(children='Click the image to turn on the LED'),
            ]),
    ]),
], color="dark", outline=True);

cardLightIntensity = dbc.Card([ 
    dbc.CardHeader([
       html.H2("Light Intensity", className="card-title, text-center")
    ]),
    dbc.CardBody([
        html.H5("Current Light Intensity", className="card-title"),
        dbc.Col(html.Div(children=[
                html.Img(src=app.get_asset_url('light_intensity.png'),width='30%', height='30%'),
                dbc.Input(
                    size="lg",
                    id='light-intensity-value',
                    className="mb-2",
                    value="The light intensity is " + str(currentLightIntensity), # + isItOn,
                    readonly = True,
                    style = {
                        'text-align': 'center',
                         # 'margin-top': '2%',
                        # 'margin-right': '5%',
                        # 'margin-left': '5%',
                        'width' : '100%',
                    }
                ),  dcc.Interval(id='mqtt3', interval = 1 * 1000, n_intervals=0)
            ]))
    ]),
],color="dark", outline=True);

cardHumidTemp = dbc.Card([
    dbc.CardHeader([
        html.H2("Humidity and Temperature", className="card-title, text-center")
    ]),
    dbc.CardBody([
                    dbc.Col(html.Div(id='humidity', children=[
                        daq.Gauge(
                        color={"gradient":True,"ranges":{"yellow":[0,30],"green":[30,50],"red":[50,100]}},
                        id='humidity-gauge',
                        label='Current Humidity',
                        showCurrentValue=True,
                        units="Percentage",
                        value=humidityValue,
                        max=100,
                        min=0
                        )
                    ])),
                    dbc.Col(html.Div(id='temperature', children=[
                        daq.Thermometer(
                        id='temperature-thermometer',
                        label='Current temperature',
                        value=temperatureValue,
                        showCurrentValue=True,
                        min=-20,
                        max=122
                        ),
                        daq.ToggleSwitch(
                        size = 50,
                        id='temp-toggle',
                        value=False,
                        label=['Celsius', 'Fahrenheit'],
                        labelPosition='bottom',
                        color = '#0C6E87',
                        style={
                            "margin": "0.5%"
                        }
                        )
                    ])) 
     ]) 
 ],color="dark", outline=True );

cardFanControlTab= dbc.Card([
    dbc.CardHeader([
        html.H2("Fan", className="card-title, text-center")
    ]),
    dbc.CardBody([
        html.Img(src=app.get_asset_url('fan.png'),width='35%', height='35%', 
                style={
                    "margin": "5%"
                } 
                ),
        daq.ToggleSwitch(
                size=50,
                id='fan-toggle',
                value=False,
                label='Fan Status',
                labelPosition='bottom',
                color = '#0C6E87', 
                style={
                    "margin": "2%"
                }
                )
    ]), 
    dcc.Interval(id='interval-component', interval=1*1500, n_intervals=0)
], color="dark", outline=True);

content = html.Div([
            html.H1(children='DashBoard', style={'text-align': 'center', 'margin': '0.5%'}),
            dbc.Container([
                dbc.Row([
                    dbc.Col(html.Div([
                            dbc.Row([
                                dbc.Col(cardLedBox, width=6, align="start", style={"height": "100%"}),
                                dbc.Col(cardFanControlTab, width=6 ,align="start", style={"height": "100%"})
                                ]),
                            dbc.Row([
                                dbc.Col(cardLightIntensity, width=12 ,align="start", style={"height": "100%"})
                                ])
                            ])
                        ),
                    dbc.Col(cardHumidTemp, width=5,align="start", style={"height": "100%"})           
                ])
            ])   
        ], className="content");

app.layout = html.Div(id="theme-switch-div", children=[navbar, content]);

@app.callback(Output('light', 'value'),
              Output('humid', 'value'),
              Output('temp', 'value'),
              Output('user', 'value'),
              Input('mqtt2', 'n_intervals')
                )
def update_output(n):
    global temp, light, humidity

    temp = db.getTemp(tag_num)

    # light
    light = db.getLight(tag_num)

    #global humidity
    humidity = db.getHumidity(tag_num)
    print(tag_num)
    
    prevTag = tag_num
    
    return light, humidity, temp, tag_num
    #remove the rest of the database stuff

@app.callback(Output('led-image', 'children'),
              Output('notification', 'is_open'),
              Output('light_intensity', 'children'),
              Input('mqtt3', 'n_intervals')
                )
def update_output(n):
    global lastSentTime 
    global isSendEligible

    sensorValue = float(message)

    if sensorValue <= light:
        GPIO.output(_ledPin, GPIO.HIGH)
        img = html.Img(src=app.get_asset_url('lightOnp'), width='100px', height='100px')

        date = datetime.now()
        if isSendEligible:
            subject="LED Warning!"
            body=f"The Light is ON at {date}"
            email.send_mail(subject, body)
            lastSentTime = int(time.time())
            isSendEligible = False
        show =  True
        return img, sensorValue
    else:
        GPIO.output(_ledPin, GPIO.LOW)
        img = html.Img(src=app.get_asset_url('lightOffp'),width='100px', height='100px')
        show = False
        # don't send another light email for 5 minutes
        # hardcoded for now, make an option later?
        if int(time.time()) > lastSentTime + 60*5:
            isSendEligible = True
        return img, sensorValue
        
    
@app.callback(Output('fan-toggle', 'value'),
              Input('fan-toggle', 'value')
)
def toggle_fan(value):
    if value:
        GPIO.output(Motor1, GPIO.HIGH)
        value = True
    else:
         GPIO.output(Motor1, GPIO.LOW)
         value = False
    return value


@app.callback(Output('humidity-gauge', 'value'),
              Output('temperature-thermometer', 'value'),
              Output('temperature-thermometer', 'units'),
              Input('interval-component', 'n_intervals'),
              Input('temp-toggle', 'value'))
def update_sensor(n, tValue):
    global emailSent
    global emailReceived
    # dht.readDHT11()
    # temperatureValue = dht.temperature
    temperatureValue = 20
        
   # humidityValue = dht.humidity
    humidityValue = 55
    
    if temperatureValue > temp and EMAIL_SEND == False:
        EMAIL_SEND = True
        subject = "Temperature too High"
        body = "The current temperature is " + str(temperatureValue) + ". Would you like to turn on the fan?"
        email.send_mail(subject, body)
        EMAIL_SEND = True
    else:
        email_id = email.get_mail_ids(1)
        reply = email.read_mail_body(email_id[0])
        reply = reply.lower()
        # todo: read mail timestamp to prevent re-using old "yes" replies
        # some_timestamp_record = email.read_mail_timestamp(email_id[0])
        if (reply.__contains__("yes")):
            startMotor()
            EMAIL_SEND = False

    # to consider: put a lower bound to start warning about temperature changes again
    # if temperatureValue < (temp - 5):
    #     EMAIL_SEND = False

    # for toggle switch: C to F
    if tValue:
        tempUnit = 'Fahrenheit'
        temperatureValue = temperatureValue * (9/5) + 32
    elif not tValue:
        tempUnit = 'Celsius'
    

    return humidityValue, temperatureValue, tempUnit


@app.callback(
    Output("offcanvas-backdrop", "is_open"),
    Input("open-offcanvas-backdrop", "n_clicks"),
    State("offcanvas-backdrop", "is_open"))
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open



#mqtt sub communication
def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    #client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


#needs testing but this should make listening for specific messages more elegant
def subscribe(client: mqtt_client):
    def on_light(client, userdata, msg):
        print("Got light message (value: " + str(msg.payload) + ")")
        global message 
        message = msg.payload.decode()
        print(float(msg.payload.decode()))
    
    def on_rfid(client, userdata, msg):
        print("Got RFID message (value: " + str(msg.payload) + ")")
        global tag_num
        tag_num = msg.payload.decode()
        print("" + msg.payload.decode())
        email.send_mail("User Login", "User with tag " + tag_num + " has logged in.")
    
    def on_message(client, userdata, msg):
        print("FALLBACK CALL | Received: Topic: %s Body: %s. No handler exists for this topic!", msg.topic, msg.payload)

    client.subscribe("IoTlab/light/intensity")
    client.message_callback_add("IoTlab/light/intensity", on_light)

    client.subscribe("IoTlab/rfid/id")
    client.message_callback_add("IoTlab/rfid/id", on_rfid)

    client.on_message = on_message


@app.callback(Output('light-intensity-value', 'value'),
              Output('username', 'value'),
              Output('tempThreshold', 'value'),
              Output('humidityThreshold', 'value'),
              Output('lightIntensity', 'value'),
              Input('interval-component', 'n_intervals'))
def update_light_intensity(n):
    return 'The current light intensity is:' + str(currentLightIntensity)

def hasLetter(s):
    for char in s:
        if (char.isalpha()):
            return True
    return False

def run():
    print("connecting")
    client = connect_mqtt()
    print("subscribing")
    subscribe(client)
    print("looping")
    client.loop_start()


if __name__ == "__main__":
    run()
    app.run_server(debug=True, host='localhost', port=8070)
    

