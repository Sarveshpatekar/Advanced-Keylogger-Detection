# 🛡️ Advanced Keylogger Detection

This is an intelligent, real-time keylogger detection system built in Python. It uses keyboard timing analysis (Z-score) and suspicious process scanning to detect potential keyloggers. A modern GUI is included for monitoring system activity and triggering alerts.

---

## ⚙️ Features

- ⌨️ **Key Press Timing Detection**  
  Detects rapid key presses and statistical anomalies (via Z-score analysis).

- 🔍 **Suspicious Process Scanner**  
  Monitors running processes for suspicious keywords (e.g., `keylogger`, `spy`, `monitor`).

- 📊 **Key Press Rate Monitoring**  
  Displays real-time key press frequency.

- 🖥️ **Graphical User Interface**  
  User-friendly GUI built with `Tkinter`.

- 📁 **Logs Everything**  
  Logs events and alerts to `advanced_keylog_detection.csv`.

---

## 📦 Requirements

Install dependencies using pip:

```bash
pip install keyboard psutil numpy

