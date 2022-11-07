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


app = Dash(__name__)
img = html.Img(src=app.get_asset_url('lightOffp'),width='100px', height='100px')
humidityValue = 0
temperatureValue = 0

theme_change = ThemeChangerAIO(aio_id="theme")

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
            ]),
            id="offcanvas-backdrop",
            title="User Options",
            is_open=False,
        ),
    ]
)



navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(theme_change, style={'padding': 10, 'border': 'none', 'background': 'none'}),
        # dbc.NavItem(dbc.NavLink("Settings", href="#")),
        dbc.NavItem(dbc.NavLink(offcanvas))

    ],
    brand="HOME",
    brand_href="#",
    color="dark",
    dark=True,
    sticky='top'
    
    
)
ledBoxTab = html.Div(id='led-box', className='ledBox',children=[
                html.H1(children='LED'),
                html.Button(img, id='led-image', n_clicks = 0),
        ])

humidTempTab = html.Div(className='grid-container', children=[
                dbc.Row([
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
                        min=0,
                        max=100
                        )
                    ]))        
                ])
            ])

fanControlTab =  html.Div(className='grid-container',children=[
                html.Div(style={'text-align': 'center'},children=[
                    html.Img(src=app.get_asset_url('fan.png'), width='15%', height='15%')
                ]),
                daq.ToggleSwitch(
                size=100,
                id='fan-toggle',
                value=False,
                label='Fan Status',
                labelPosition='bottom',
                color = '#0C6E87', 
                style={
                    'margin-top': '3%'
                }
                ),
            ])

tabs = dcc.Tabs([
        dcc.Tab(className='custom-tab', id='LED', label='LED Control', children=[
            ledBoxTab
        ]),
        dcc.Tab(className='custom-tab', id='HT', label='Humidity & Temperature', children=[
            humidTempTab
        ]),
        dcc.Tab(className='custom-tab',id='FC', label='Fan Control', children=[
            fanControlTab
        ]),
    ], colors={
        "border": "#097966",
        "primary": "#097966",
        "background": "#3cdfff"
    })



app.layout = html.Div(id="theme-switch-div", children=[
    navbar,
    html.H1(children='DASHBOARD', style={'text-align': 'center', 'margin-top': '3%'}),

    html.Div(className='grid-container', style={'margin': '5% 7% 5% 7%'}, children=[
        tabs
    ]),
    dcc.Interval(id='interval-component', interval=1*1500, n_intervals=0)
])


@app.callback(Output('led-image', 'children'),
              Input('led-image', 'n_clicks')
                )
def update_output(n_clicks):
    if n_clicks % 2 == 1:
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
              Input('interval-component', 'n_intervals'))

def update_sensor(n):
    global EMAIL_SEND
    dht.readDHT11()
    temperatureValue = dht.temperature
    humidityValue = dht.humidity
    #checking for the temp and sending an email / turning on a motor
    if temperatureValue > 20 and EMAIL_SEND == False:
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
            
    return humidityValue, temperatureValue
 

#Phase 3 code
@app.callback(
    Output("offcanvas-backdrop", "is_open"),
    Input("open-offcanvas-backdrop", "n_clicks"),
    State("offcanvas-backdrop", "is_open"))
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open





def main():
    app.run_server(debug=True, host='localhost', port=8060)
   
main()
