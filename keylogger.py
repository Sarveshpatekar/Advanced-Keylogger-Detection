import keyboard
import psutil
import numpy as np
import time
import threading
from collections import deque
import logging
import tkinter as tk
from tkinter import ttk, scrolledtext
import sys
import platform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('advanced_keylog_detection.csv'),
        logging.StreamHandler(sys.stdout)
    ]
)

class KeyloggerDetector:
    def __init__(self, max_buffer=200, z_score_threshold=3.0, rapid_press_threshold=0.05, suspicious_process_names=None):
        self.key_buffer = deque(maxlen=max_buffer)  # Store recent key presses
        self.last_press_time = time.time()
        self.rapid_press_threshold = rapid_press_threshold
        self.z_score_threshold = z_score_threshold
        self.suspicious_process_names = suspicious_process_names or ['keylogger', 'spy', 'monitor']
        self.running = False
        self.suspicious_activity_detected = False
        self.key_press_intervals = deque(maxlen=max_buffer)  # Store intervals for statistical analysis
        self.root = None
        self.alert_label = None
        self.key_rate_label = None
        self.process_text = None

    def log_key(self, event):
        if event.event_type != keyboard.KEY_DOWN:
            return
        
        current_time = time.time()
        key_name = event.name
        time_diff = current_time - self.last_press_time

        self.key_buffer.append((key_name, current_time))
        self.key_press_intervals.append(time_diff)
        logging.info(f"Key pressed: {key_name}, Interval: {time_diff:.3f}s")

        if time_diff < self.rapid_press_threshold:
            logging.warning(f"Rapid key press detected: {key_name}, Interval: {time_diff:.3f}s")
            self.analyze_anomalies()

        self.last_press_time = current_time
        if self.root:
            self.update_gui()

    def analyze_anomalies(self):
        if len(self.key_press_intervals) < 10:
            return

        intervals = np.array(list(self.key_press_intervals))
        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals)

        if std_interval == 0:
            return

        latest_interval = self.key_press_intervals[-1]
        z_score = (latest_interval - mean_interval) / std_interval

        if abs(z_score) > self.z_score_threshold:
            logging.error(f"Anomaly detected: z-score={z_score:.2f}, Interval={latest_interval:.3f}s")
            self.suspicious_activity_detected = True
            self.alert()

    def monitor_processes(self):
        while self.running:
            try:
                for proc in psutil.process_iter(['name']):
                    proc_name = proc.info['name'].lower()
                    if any(sus_name in proc_name for sus_name in self.suspicious_process_names):
                        logging.warning(f"Suspicious process detected: {proc_name}")
                        self.suspicious_activity_detected = True
                        self.alert()
                        if self.process_text:
                            self.process_text.insert(tk.END, f"Suspicious process: {proc_name}\n")
                            self.process_text.see(tk.END)
                time.sleep(5)
            except Exception as e:
                logging.error(f"Error in process monitoring: {e}")
                time.sleep(5)

    def alert(self):
        logging.critical("Potential keylogger detected. Initiating alert.")
        if self.alert_label:
            self.alert_label.config(text="⚠️ ALERT: Potential keylogger detected!", fg="red")

    def start_monitoring(self):
        self.running = True
        logging.info("Starting advanced keylogger detection system...")
        try:
            keyboard.hook(self.log_key)
            process_thread = threading.Thread(target=self.monitor_processes)
            process_thread.daemon = True
            process_thread.start()
            keyboard.wait()
        except KeyboardInterrupt:
            self.stop_monitoring()
        except Exception as e:
            logging.error(f"Error in monitoring: {e}")
            self.stop_monitoring()

    def stop_monitoring(self):
        self.running = False
        keyboard.unhook_all()
        logging.info("Advanced keylogger detection system stopped.")
        if self.root:
            self.root.quit()

    def update_gui(self):
        key_rate = len(self.key_buffer) / (time.time() - self.key_buffer[0][1]) if self.key_buffer else 0
        self.key_rate_label.config(text=f"Key Press Rate: {key_rate:.2f} keys/s")
        if not self.suspicious_activity_detected:
            self.alert_label.config(text="✅ Status: Normal", fg="green")

    def create_gui(self):
        self.root = tk.Tk()
        self.root.title("🛡️ Advanced Keylogger Detection")
        self.root.geometry("700x500")
        self.root.configure(bg="#f2f2f2")  # Light background

        # Alert label
        self.alert_label = tk.Label(
            self.root, text="Status: Normal", fg="green",
            font=("Helvetica", 16, "bold"), bg="#f2f2f2"
        )
        self.alert_label.pack(pady=15)

        # Key press rate label
        self.key_rate_label = tk.Label(
            self.root, text="Key Press Rate: 0.00 keys/s",
            font=("Helvetica", 14), bg="#f2f2f2"
        )
        self.key_rate_label.pack(pady=10)

        # Section label
        section_label = tk.Label(
            self.root, text="Suspicious Processes:", font=("Helvetica", 14, "bold"),
            bg="#f2f2f2"
        )
        section_label.pack(pady=(10, 5))

        # Text box for process output
        self.process_text = scrolledtext.ScrolledText(
            self.root, height=12, width=80, font=("Courier", 11),
            bg="#ffffff", fg="#000000", borderwidth=2, relief="groove"
        )
        self.process_text.pack(pady=5)

        # Stop button
        stop_button = ttk.Button(
            self.root, text="🛑 Stop Monitoring", command=self.stop_monitoring
        )
        stop_button.pack(pady=15)

        self.root.protocol("WM_DELETE_WINDOW", self.stop_monitoring)

    def run(self):
        self.create_gui()
        monitor_thread = threading.Thread(target=self.start_monitoring)
        monitor_thread.daemon = True
        monitor_thread.start()
        self.root.mainloop()

def main():
    detector = KeyloggerDetector()
    detector.run()

if __name__ == "__main__":
    main()
