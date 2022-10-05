from dash import Dash, dcc, html, Input, Output
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
GPIO.setmode(GPIO.BCM)
led=17
GPIO.setup(led, GPIO.OUT)

app = Dash(__name__)

img = html.Img(src=app.get_asset_url('lightOffp'), id="photo", width="300", height="300")

app.layout = html.Div([
    html.H6("Turn The LED on and off!"),
    html.Div([
        html.Button(img, id='submit-val', n_clicks=0),
    ]),
    html.Br(),
    html.Div(id='my-output')

])


@app.callback(
    Output(component_id='submit-val', component_property='children'),
    Input(component_id='submit-val', component_property='n_clicks')
)
def update_output_div(n_clicks):
    if n_clicks % 2 == 0:
        GPIO.output(led, GPIO.LOW)
        img = html.Img(src=app.get_asset_url('lightOffp'), id="photo", width="300", height="300")
        return img
    else:
        GPIO.output(led, GPIO.HIGH)
        img = html.Img(src=app.get_asset_url('lightOnp'), id="photo", width="300", height="300")
        return img


if __name__ == '__main__':
    app.run_server(debug=True)