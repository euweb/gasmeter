"""Mock GPIO Handler für Entwicklung/Test"""
import threading
import time


class GPIOMock:
    def __init__(self, pin, bounce_time, callback, pulse_interval=10):
        self.pin = pin
        self.bounce_time = bounce_time
        self.callback = callback
        self.pulse_interval = pulse_interval
        self.running = False
        self.thread = None
        
    def setup(self):
        """Startet Mock-Modus mit simulierten Impulsen"""
        print(f"🧪 TEST-MODUS: Impulse alle {self.pulse_interval}s")
        self.running = True
        self.thread = threading.Thread(target=self._pulse_simulator, daemon=True)
        self.thread.start()
    
    def cleanup(self):
        """Stoppt Mock-Modus"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
    
    def _pulse_simulator(self):
        """Simuliert GPIO-Impulse"""
        while self.running:
            time.sleep(self.pulse_interval)
            if self.running:
                self.callback(channel=None)
