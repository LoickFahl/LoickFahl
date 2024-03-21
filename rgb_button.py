import RPi.GPIO as GPIO
import time
import subprocess
from math import sin, radians

# Define GPIO pins
button_pin = 21
red_pin = 16
green_pin = 19
blue_pin = 6

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(red_pin, GPIO.OUT)
GPIO.setup(green_pin, GPIO.OUT)
GPIO.setup(blue_pin, GPIO.OUT)

# Initial state (off)
GPIO.output(red_pin, GPIO.LOW)
GPIO.output(green_pin, GPIO.LOW)
GPIO.output(blue_pin, GPIO.LOW)

# PWM setup
red_pwm = GPIO.PWM(red_pin, 1000)
green_pwm = GPIO.PWM(green_pin, 1000)
blue_pwm = GPIO.PWM(blue_pin, 1000)

red_pwm.start(0)
green_pwm.start(0)
blue_pwm.start(0)

def set_rgb_color(r, g, b):
    red_pwm.ChangeDutyCycle(r)
    green_pwm.ChangeDutyCycle(g)
    blue_pwm.ChangeDutyCycle(b)

def fade_rgb():
    # Fading through all possible colors
    for angle in range(0, 360, 5):
        r = int((1 + sin(radians(angle))) * 50)
        g = int((1 + sin(radians(angle + 120))) * 50)
        b = int((1 + sin(radians(angle + 240))) * 50)

        set_rgb_color(r, g, b)
        time.sleep(0.1)

def check_services():
    services_to_check = [
        "gpsd.socket",
        "readsb.service",
        "graphs1090.service",
        "icecast2.service",
        "chasemapper.service",
        "rtl_airband.service",
        "tar1090.service",
        "timelapse1090.service",
        "dev_auto_rx.service"
    ]
    for service in services_to_check:
        try:
            subprocess.check_output(["systemctl", "is-active", "--quiet", service])
            print(f"Service {service} is running.")
        except subprocess.CalledProcessError:
            print(f"Service {service} is not running.")
            set_rgb_color(100, 0, 0)  # Turn the LED red if any service is stopped
            return False
    return True

def restart_services():
    services_to_check = [
        "gpsd.socket",
        "readsb.service",
        "graphs1090.service",
        "icecast2.service",
        "chasemapper.service",
        "rtl_airband.service",
        "tar1090.service",
        "timelapse1090.service",
        "dev_auto_rx.service"
    ]
    for service in services_to_check:
        subprocess.call(["sudo", "systemctl", "restart", service])
        print(f"Restarting service {service}")

try:
    # Check services initially
    if check_services():
        fade_rgb()  # Start RGB fading if services are running
    else:
        set_rgb_color(100, 0, 0)  # Set LED to solid red if any service is stopped

    while True:
        # Continuous check for button press
        while GPIO.input(button_pin) == GPIO.HIGH:
            time.sleep(0.1)  # Small delay to avoid high CPU usage

        print("Button pressed")

        # Restart services if any are stopped
        if not check_services():
            restart_services()
            time.sleep(2)  # Wait for services to start before resuming

        # Resume RGB fading
        fade_rgb()

except KeyboardInterrupt:
    pass

finally:
    # Cleanup GPIO on program exit
    GPIO.cleanup()
