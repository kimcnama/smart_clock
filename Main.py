import RPi.GPIO as GPIO
import time
from threading import Thread
import os
from Display import Display

def sensor_module():
	screen_off = False
	INPUT_PIN = 4
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(INPUT_PIN, GPIO.IN)
	thread_sleep_time_secs = 21
	wait_before_off_screen = 10
	screen_off_command = "sleep {} && xset dpms force off".format(wait_before_off_screen)
	screen_on_command = "xset dpms force on"
	
	while True:
		# 0 for light, 1 for darkness
		darkness = GPIO.input(INPUT_PIN)
		
		#turn screen on
		if not darkness and screen_off:
			os.system(screen_on_command)
			screen_off = False
		#turn screen off
		elif darkness and not screen_off:
			os.system(screen_off_command)
			screen_off = True
		
		time.sleep(thread_sleep_time_secs)
		
if __name__ == '__main__':
	Thread(target=sensor_module).start()
	gui = Display()

