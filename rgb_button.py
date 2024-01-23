import RPi.GPIO as GPIO
import time
import subprocess
from math import sin, radians

# Define GPIO pins
button_pin = 21
red_pin = 16
green_pin = 19
blue_pin = 6

# Define services to check
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

# Setup falling edge detection for the button
GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=lambda x: button_callback(), bouncetime=200)

def set_rgb_color(r, g, b):
    red_pwm.ChangeDutyCycle(r)
    green_pwm.ChangeDutyCycle(g)
    blue_pwm.ChangeDutyCycle(b)

def cycle_rgb():
    # Cycle through all possible colors
    for angle in range(0, 360, 5):
        r = int((1 + sin(radians(angle))) * 50)
        g = int((1 + sin(radians(angle + 120))) * 50)
        b = int((1 + sin(radians(angle + 240))) * 50)

        set_rgb_color(r, g, b)
        time.sleep(0.1)

def check_services():
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
    for service in services_to_check:
        subprocess.call(["sudo", "systemctl", "restart", service])
        print(f"Restarting service {service}")

def blink_blue():
    set_rgb_color(0, 0, 100)  # Set the LED to blue
    time.sleep(0.5)
    set_rgb_color(0, 0, 0)  # Turn off the LED
    time.sleep(0.5)
    set_rgb_color(0, 0, 100)  # Set the LED to blue
    time.sleep(0.5)
    set_rgb_color(0, 0, 0)  # Turn off the LED

def button_callback():
    print("Button pressed")
    blink_blue()  # Blink the LED blue twice
    restart_services()
    set_rgb_color(0, 100, 0)  # Turn the LED green after restarting services
    time.sleep(2)  # Allow time for services to start before resuming normal operation
    services_running = check_services()  # Recheck services
    if services_running:
        cycle_rgb()  # Restart RGB cycle

try:
    while True:
        # Check services every 30 minutes (twice per hour)
        for _ in range(2):
            services_running = check_services()
            if services_running:
                cycle_rgb()
            time.sleep(900)  # 15 minutes

except KeyboardInterrupt:
    pass

finally:
    # Cleanup GPIO on program exit
    GPIO.cleanup()
