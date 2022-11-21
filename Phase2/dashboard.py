import dash.dependencies
import dash_daq as daq
from dash import html, Input, Output, dcc, Dash
import dash_bootstrap_components as dbc
import RPi.GPIO as GPIO
import time
import Freenove_DHT as DHT
import mail_client as email
#import motor as motor

GPIO.setmode(GPIO.BCM) # BCM
GPIO.setwarnings(False)
GPIO.setup(21, GPIO.OUT)
EMAIL_SEND = False

DHTPin = 17 
dht = DHT.DHT(DHTPin) #create a DHT class object

app = Dash(__name__)
img = html.Img(src=app.get_asset_url('lightOffp'),width='100px', height='100px')
humidityValue = 0
temperatureValue = 0

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


app.layout = html.Div(children=[
    html.H1(children='Dashboard', style={'text-align': 'center', 'margin-left': '6%', 'margin-bottom': '5%'}),
    html.Div( id='led-box', style={'margin-left': '6%', 'margin-top': '5%', 'margin-bottom': '5%'},children=[
        html.H1(children='LED Controller'),
        html.Button(img, id='led-image', n_clicks = 0),
    ]),

    html.Div(className='grid-container', id='humidity-and-temperature', style={'margin-left': '2%', 'margin-top': '5%', 'margin-bottom': '5%'}, children=[
        html.H1(children='Humidity & Temperature'),
    ]),


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
            max=100,
            style={
                'margin-top': '5%',
                'margin-bottom': '5%'
            })])),  
        dbc.Col(html.Div(id='dc-motor', children=[
            daq.ToggleSwitch(
            id='motor',
            label=['Fan On', 'Fan Off'],
            value='',
            #if temperatureValue >= 24:
            #    GPIO.output(Motor1,GPIO.HIGH)
            #    GPIO.output(Motor2,GPIO.LOW)
            #    GPIO.output(Motor3,GPIO.HIGH)
            #    value=False
            #elif temperatureValue < 24:
            #    sleep(5)
            #    GPIO.output(Motor1,GPIO.LOW)
            #    GPIO.cleanup()
            #    value=motorOn
            style={
                'margin-top': '5%',
                'margin-bottom': '5%'
            }
            
            
            )])) 
        ]),
 
    dcc.Interval(id='interval-component', interval=1*5000, n_intervals=0)
],  style={'backgroundColor':'#727174', 'padding-top': '2%'})


@app.callback(Output('led-image', 'children'),
              Input('led-image', 'n_clicks')
              )
def update_output(n_clicks):
    if n_clicks % 2 == 1:
        GPIO.output(21, GPIO.HIGH)
        img = html.Img(src=app.get_asset_url('lightOnp'), width='100px', height='100px')
        return img
    else:
        GPIO.output(21, GPIO.LOW)
        img = html.Img(src=app.get_asset_url('lightOffp'),width='100px', height='100px')
        return img
    
def main():
    app.run_server(debug=True, host='localhost', port=8050)


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
            
    #turning the motor off when the temperature is lower than 24
#    if temperatureValue < 24:
#        motor.stop()
#        email_sent = False
    

main()

