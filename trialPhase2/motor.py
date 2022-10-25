import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
Motor1 = 27 # Input Pin
Motor2 = 17 # Input Pin
Motor3 = 22 # Enable Pin

GPIO.setup(Motor1,GPIO.OUT)
GPIO.setup(Motor2,GPIO.OUT)
GPIO.setup(Motor3,GPIO.OUT)

def start():
    while (True):
        GPIO.output(Motor1,GPIO.HIGH)
        GPIO.output(Motor2,GPIO.LOW)
        GPIO.output(Motor3,GPIO.HIGH)
        sleep(10)
        GPIO.cleanup()
        
def stop():
    GPIO.output(Motor1,GPIO.LOW)
    GPIO.output(Motor2,GPIO.LOW)
    GPIO.output(Motor3,GPIO.LOW)
    GPIO.cleanup()


#GPIO.output(Motor1,GPIO.HIGH)
#GPIO.output(Motor2,GPIO.LOW)
#GPIO.output(Motor3,GPIO.HIGH)
#sleep(5)

#GPIO.output(Motor1,GPIO.LOW)
#GPIO.output(Motor2,GPIO.HIGH)
#GPIO.output(Motor3,GPIO.HIGH)

#sleep(5)
#GPIO.output(Motor3,GPIO.LOW)
#GPIO.cleanup() 