import serial
import time
import csv
import matplotlib.pyplot as plt
from datetime import datetime
from collections import deque

# --- Configuration ---
PORT = 'COM3'  # Update to your ESP32 port
BAUD_RATE = 115200
FILE_NAME = 'dual_motor_tuning.csv'
MAX_POINTS = 150 

# Data storage
time_data = deque(maxlen=MAX_POINTS)
front_rpm_data = deque(maxlen=MAX_POINTS)
rear_rpm_data = deque(maxlen=MAX_POINTS)

# Plot Setup
plt.ion()
fig, ax = plt.subplots(figsize=(10, 6))
line_front, = ax.plot([], [], 'b-', label='Front RPM')
line_rear, = ax.plot([], [], 'r-', label='Rear RPM')
ax.set_title("Real-Time Dual RPM Monitoring")
ax.set_xlabel("Time (ms)")
ax.set_ylabel("RPM")
ax.legend(loc='upper left')
ax.grid(True)

def log_data():
    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
        time.sleep(2)

        with open(FILE_NAME, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Timestamp', 'Arduino_ms', 'Front_RPM', 'Rear_RPM'])

            print(f"Logging dual data to {FILE_NAME}. Press Ctrl+C to stop.")

            while True:
                if ser.in_waiting > 0:
                    raw_line = ser.readline().decode('utf-8').strip()
                    
                    # Look for our "DATA" prefix
                    if raw_line.startswith("DATA,"):
                        parts = raw_line.split(',')
                        # parts[1]=Time, [2]=FrontRPM, [3]=RearRPM
                        arduino_ms = int(parts[1])
                        f_rpm = float(parts[2])
                        r_rpm = float(parts[3])

                        # Save to CSV
                        writer.writerow([datetime.now(), arduino_ms, f_rpm, r_rpm])

                        # Update Graph
                        time_data.append(arduino_ms)
                        front_rpm_data.append(f_rpm)
                        rear_rpm_data.append(r_rpm)

                        line_front.set_data(list(time_data), list(front_rpm_data))
                        line_rear.set_data(list(time_data), list(rear_rpm_data))

                        ax.relim()
                        ax.autoscale_view()
                        fig.canvas.draw()
                        fig.canvas.flush_events()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Closing Serial and Saving File...")
        if 'ser' in locals(): ser.close()

if __name__ == "__main__":
    log_data()