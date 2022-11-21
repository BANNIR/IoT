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
import random
from datetime import datetime
import pytz
import sqlite3
from sqlite3 import Error


broker = '10.0.0.242'
port = 1883
topic = "IoTlab/light"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'

message ="0"

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
currentLightIntensity = "NaN"
global lightIntensity

app = Dash(__name__)
img = html.Img(src=app.get_asset_url('lightOffp'),width='40%', height='40%')
humidityValue = 0
temperatureValue = 0
tempUnit = 'Celsius'
emailSent = False
emailReceived = 0


theme_change = ThemeChangerAIO(aio_id="theme");

offcanvas = html.Div(
    [
        dbc.Button(
              "Profile", id="open-offcanvas-backdrop",style={'padding': 10, 'border': 'none', 'background': 'none'}
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
                    dbc.Col(html.Div(dbc.Input(placeholder="username", size="md", className="mb-3", readonly=True))),
                ]),
                dbc.Row(
                [
                    dbc.Col(html.Div("Ideal Temperature: ")),
                    dbc.Col(html.Div(dbc.Input(placeholder="ideal_temp", size="md", className="mb-3", readonly=True))),
                ]),
                dbc.Row(
                [
                    dbc.Col(html.Div("Ideal Humidity: ")),
                    dbc.Col(html.Div(dbc.Input(placeholder="ideal_humidity", size="md", className="mb-3", readonly=True))),
                ]),
                dbc.Row(
                [
                    dbc.Col(html.Div("Ideal light intensity: ")),
                    dbc.Col(html.Div(dbc.Input(placeholder="ideal_light_intensity", size="md", className="mb-3", readonly=True))),
                ]),
                dbc.Row(
                [   
                    dbc.Col(html.Div(theme_change, style={'padding': 0, 'border': 'none', 'background': 'none'})),
                ])
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
        html.H2("LED", className="card-title, text-center")
    ]),
    dbc.CardBody([
        html.Button(img, id='led-image', n_clicks = 0, className = "btn btn-primary-outline"),
        html.P(children='Click the image to turn on the LED'),
        dcc.Interval(id='mqtt', interval=1*1500, n_intervals=0),
    ]), 
], color="dark", outline=True);

cardLighIntensity = dbc.Card([
    dbc.CardHeader([
        html.H2("Light Intensity", className="card-title, text-center")
    ]),
    dbc.CardBody([
        html.H5("Current Light Intensity", className="card-title"),
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
                )
    ]), 
],color="dark", outline=True);

cardHumidTemp = dbc.Card([
    dbc.CardHeader([
        html.H2("Humidity and Temperature", className="card-title, text-center")
    ]),
    dbc.CardBody([
           #dbc.Row([
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
                        size=40,
                        id='temp-toggle',
                        value=False,
                        label=['Celsius', 'Fahrenheit'],
                        labelPosition='bottom',
                        color = '#0C6E87',
                        style={
                            "margin": "5%"
                        }
                        )
                    ]))       
            #   ])
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
                size=100,
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
            html.H1(children='DashBoard', style={'text-align': 'center', 'margin': '2%'}),
            dbc.Container([
                dbc.Row([
                    dbc.Col(html.Div([
                            dbc.Row([
                                dbc.Col(cardLedBox, width=6, align="start", style={"height": "100%"}),
                                dbc.Col(cardFanControlTab, width=6 ,align="start", style={"height": "100%"})
                                ]),
                            dbc.Row([
                                dbc.Col(cardLighIntensity, width=12 ,align="start", style={"height": "100%"})
                                ])
                            ])
                        ),
                    dbc.Col(cardHumidTemp, width=5,align="start", style={"height": "100%"})           
                ])
            ])     
        ], className="content");

app.layout = html.Div(id="theme-switch-div", children=[navbar, content]);


@app.callback(Output('led-image', 'children'),
              Input('mqtt', 'n_intervals')
                )
def update_output(n):
    sensorValue = float(message)

    if sensorValue <= 400.0:
        GPIO.output(_ledPin, GPIO.HIGH)
        img = html.Img(src=app.get_asset_url('lightOnp'), width='100px', height='100px')
        return img
    else:
        GPIO.output(_ledPin, GPIO.LOW)
        img = html.Img(src=app.get_asset_url('lightOffp'),width='100px', height='100px')
        return img
    
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

    # for toggle switch: C to F
    if tValue:
        tempUnit = 'Fahrenheit'
        temperatureValue = temperatureValue * (9/5) + 32
    elif not tValue:
        tempUnit = 'Celsius'

    return humidityValue, temperatureValue, tempUnit

#Phase 3 code
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
   # client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global message 
        message = msg.payload.decode()
        #print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    client.subscribe(topic)
    client.on_message = on_message


@app.callback(Output('light-intensity-value', 'value'),
              Input('interval-component', 'n_intervals'))
def update_light_intensity(n):
    return 'The current light intensity is:' + str(current_light_intensity)

def run():
    print("attempting to connect")
   # client = connect_mqtt()
    print("attempting to subscribe")
    subscribe(client)
    client.loop_start()


if __name__ == "__main__":
   # run()
    app.run_server(debug=True, host='localhost', port=8070)
    

