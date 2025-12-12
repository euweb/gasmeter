"""GPIO Handler für Raspberry Pi"""
import RPi.GPIO as GPIO


class GPIOHandler:
    def __init__(self, pin, bounce_time, callback):
        self.pin = pin
        self.bounce_time = bounce_time
        self.callback = callback
        
    def setup(self):
        """Initialisiert GPIO"""
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=self.callback, bouncetime=self.bounce_time)
        print("Gas-Zähler gestartet. Warte auf Impulse...")
    
    def cleanup(self):
        """Räumt GPIO auf"""
        GPIO.cleanup()
