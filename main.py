import sys
import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QDateEdit,
                             QComboBox, QPushButton, QVBoxLayout, QScrollArea, QFormLayout,
                             QGroupBox, QHBoxLayout, QCheckBox)
from PyQt5.QtCore import QDate, QDateTime
from PyQt5.QtGui import QWheelEvent
import sched
import time as pytime
import subprocess
from threading import Thread, Event
from functools import partial
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import traceback
from shotgun_api3 import Shotgun
from collections import defaultdict
import os
import re
from datetime import datetime

EMAIL = "SAMPLE_EMAIL@EMAIL.COM"
PASSWORD = 'SAMPLE PASSWORD'

SERVER_PATH = MW_SERVER_PATH
SCRIPT_NAME = MW_SCRIPT_NAME
SCRIPT_KEY = MW_SCRIPT_KEY

sg = Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)

def send_error_email(error_message, script_name):
    date_time = datetime.now().strftime("%B %d, %Y at %I:%M%p")
    from_email = EMAIL
    to_email = "chad@mrwolf.com"
    subject = "Script Juggler Error: " + str(script_name) + " - " + date_time
    body = f"An error occurred in the script: {error_message}"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Error email sent successfully")
    except Exception as e:
        print(f"Failed to send error email: {e}")


class NoScrollComboBox(QComboBox):
    def wheelEvent(self, event: QWheelEvent):
        event.ignore()


class TimeSelector(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()

        # Date selector
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)

        # Hour selector
        self.hour_combo = QComboBox()
        self.hour_combo.addItems([str(i).zfill(2) for i in range(1, 13)])

        # Minute selector
        self.minute_combo = QComboBox()
        self.minute_combo.addItems([str(i).zfill(2) for i in range(0, 60)])

        # AM/PM selector
        self.ampm_combo = QComboBox()
        self.ampm_combo.addItems(["AM", "PM"])

        layout.addWidget(self.date_edit)
        layout.addWidget(self.hour_combo)
        layout.addWidget(self.minute_combo)
        layout.addWidget(self.ampm_combo)

        self.setLayout(layout)

    def get_datetime(self):
        date = self.date_edit.date()
        hour = int(self.hour_combo.currentText())
        minute = int(self.minute_combo.currentText())
        ampm = self.ampm_combo.currentText()

        if ampm == "PM" and hour != 12:
            hour += 12
        elif ampm == "AM" and hour == 12:
            hour = 0

        datetime_obj = datetime(date.year(), date.month(), date.day(), hour, minute)
        return datetime_obj

    def set_datetime(self, dt):
        self.date_edit.setDate(dt.date())
        hour = dt.hour
        if hour == 0:
            self.ampm_combo.setCurrentText("AM")
            self.hour_combo.setCurrentText("12")
        elif hour < 12:
            self.ampm_combo.setCurrentText("AM")
            self.hour_combo.setCurrentText(str(hour).zfill(2))
        elif hour == 12:
            self.ampm_combo.setCurrentText("PM")
            self.hour_combo.setCurrentText("12")
        else:
            self.ampm_combo.setCurrentText("PM")
            self.hour_combo.setCurrentText(str(hour - 12).zfill(2))
        self.minute_combo.setCurrentText(str(dt.minute).zfill(2))


class ScriptScheduler(QWidget):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.schedulers = {}
        self.stop_events = {}
        self.main_layout = QHBoxLayout()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.add_script_button = QPushButton('Add Script')
        self.save_button = QPushButton('Save Settings')
        self.setup_buttons()
        self.load_scripts_from_json()

    def setup_buttons(self):
        self.resize(900, 700)
        self.setWindowTitle('Python Script Scheduler')
        with open("style.css", "r") as file:
            self.setStyleSheet(file.read())
        self.add_script_button.clicked.connect(self.add_script_fields)
        self.save_button.clicked.connect(self.save_scripts_to_json)
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.add_script_button)
        button_layout.addWidget(self.save_button)
        button_layout.addStretch()
        self.main_layout.addWidget(self.scroll_area, 1)
        self.main_layout.addLayout(button_layout)
        self.setLayout(self.main_layout)
        self.show()

    def add_script_fields(self):
        script_group = QGroupBox('Script Settings')
        script_layout = QFormLayout()
        script_path_input = QLineEdit()

        # Frequency value input
        frequency_value_input = NoScrollComboBox()
        frequency_value_input.addItems([str(i) for i in range(1, 61)])  # Allow values 1 to 60

        # Frequency unit input
        frequency_unit_input = NoScrollComboBox()
        frequency_unit_input.addItems(['Seconds', 'Minutes', 'Hours', 'Daily', 'Weekly', 'Monthly'])

        start_time_input = TimeSelector()
        last_run_label = QLabel('Last Run: N/A')
        next_run_label = QLabel('Next Run: N/A')
        start_button = QPushButton('Start')
        stop_button = QPushButton('Stop')
        delete_button = QPushButton('Delete')
        delete_button.setObjectName('delete-button')
        delete_button.clicked.connect(partial(self.delete_script, script_group))
        start_button.clicked.connect(partial(self.start_script, script_group))
        stop_button.clicked.connect(partial(self.stop_script, script_group))

        button_layout = QHBoxLayout()
        button_layout.addWidget(start_button)
        button_layout.addWidget(stop_button)
        button_layout.addWidget(delete_button)

        script_layout.addRow('Script Path:', script_path_input)
        script_layout.addRow('Frequency Value:', frequency_value_input)
        script_layout.addRow('Frequency Unit:', frequency_unit_input)
        script_layout.addRow('Start Time:', start_time_input)
        script_layout.addRow(last_run_label)
        script_layout.addRow(next_run_label)
        script_layout.addRow(button_layout)

        script_group.setLayout(script_layout)
        self.scroll_layout.addWidget(script_group)
        self.scripts.append(
            (script_group, script_path_input, frequency_value_input, frequency_unit_input, start_time_input,
             last_run_label, next_run_label,
             start_button, stop_button, delete_button))

    def delete_script(self, script_group):
        self.stop_script(script_group)
        self.scroll_layout.removeWidget(script_group)
        script_group.deleteLater()
        self.scripts = [(sg, p, fv, fu, st, l, n, st_btn, sp, d) for sg, p, fv, fu, st, l, n, st_btn, sp, d in
                        self.scripts if
                        sg != script_group]

    def start_script(self, script_group):
        for sg, script_path_input, frequency_value_input, frequency_unit_input, start_time_input, last_run_label, next_run_label, start_button, stop_button, delete_button in self.scripts:
            if sg == script_group:
                script_path = script_path_input.text()
                frequency_value = int(frequency_value_input.currentText())
                frequency_unit = frequency_unit_input.currentText()
                start_time = start_time_input.get_datetime()

                if not os.path.isfile(script_path):
                    print("INVALID PATH")
                    last_run_label.setText('Invalid Script Path')
                    return

                # Disable fields
                script_path_input.setEnabled(False)
                frequency_value_input.setEnabled(False)
                frequency_unit_input.setEnabled(False)
                start_time_input.setEnabled(False)
                delete_button.setEnabled(False)

                scheduler = sched.scheduler(pytime.time, pytime.sleep)
                self.schedulers[script_group] = scheduler
                stop_event = Event()
                self.stop_events[script_group] = stop_event

                def run_script(script_path, last_run_label, stop_event):
                    if not stop_event.is_set():
                        try:
                            # Get the directory where the script is located
                            script_dir = os.path.dirname(script_path)

                            # Construct the path to the virtual environment's Python executable
                            python_executable = os.path.join(script_dir, 'venv', 'Scripts', 'python.exe')

                            # Run the script using the Python interpreter from the virtual environment
                            subprocess.run([python_executable, script_path], check=True)

                            # Update the last run time
                            last_run_datetime = QDateTime.currentDateTime()
                            formatted_last_run_time = last_run_datetime.toString('ddd MMMM dd hh:mm:ss AP')
                            last_run_label.setText(f'Last Run: {formatted_last_run_time}')
                        except Exception as e:
                            error_message = traceback.format_exc()
                            last_run_label.setText("Last Run: Error Check Email")
                            file_name = os.path.basename(script_path)
                            send_error_email(error_message, file_name)

                def schedule_next_run(frequency_value, frequency_unit, scheduler, stop_event, script_path,
                                      last_run_label):
                    unit_seconds = {'Seconds': 1, 'Minutes': 60, 'Hours': 3600, 'Daily': 86400, 'Weekly': 604800,
                                    'Monthly': 2592000}
                    interval = frequency_value * unit_seconds.get(frequency_unit,
                                                                  60)  # Default to 60 seconds if unit not found

                    if not stop_event.is_set():
                        scheduler.enter(interval, 1, schedule_next_run,
                                        (frequency_value, frequency_unit, scheduler, stop_event, script_path,
                                         last_run_label))
                        Thread(target=run_script, args=(script_path, last_run_label, stop_event)).start()

                initial_delay = (start_time - datetime.now()).total_seconds()
                if initial_delay < 0:
                    initial_delay = 0

                scheduler.enter(initial_delay, 1, schedule_next_run,
                                (frequency_value, frequency_unit, scheduler, stop_event, script_path, last_run_label))
                Thread(target=scheduler.run).start()
                start_button.setEnabled(False)
                stop_button.setEnabled(True)

    def stop_script(self, script_group):
        if script_group in self.schedulers:
            self.stop_events[script_group].set()
            del self.schedulers[script_group]
            del self.stop_events[script_group]
            for sg, script_path_input, frequency_value_input, frequency_unit_input, start_time_input, last_run_label, next_run_label, start_button, stop_button, delete_button in self.scripts:
                if sg == script_group:
                    # Re-enable fields
                    script_path_input.setEnabled(True)
                    frequency_value_input.setEnabled(True)
                    frequency_unit_input.setEnabled(True)
                    start_time_input.setEnabled(True)
                    delete_button.setEnabled(True)

                    start_button.setEnabled(True)
                    stop_button.setEnabled(False)
                    next_run_label.setText('Next Run: N/A')
                    break

    def save_scripts_to_json(self):
        script_data = []
        for script_group, script_path_input, frequency_value_input, frequency_unit_input, start_time_input, last_run_label, next_run_label, start_button, stop_button, delete_button in self.scripts:
            script_info = {
                'path': script_path_input.text(),
                'frequency_value': frequency_value_input.currentText(),
                'frequency_unit': frequency_unit_input.currentText(),
                'start_time': start_time_input.get_datetime().strftime('%Y-%m-%d %H:%M:%S'),
                'last_run': last_run_label.text().replace('Last Run: ', ''),
                'next_run': next_run_label.text().replace('Next Run: ', '')
            }
            script_data.append(script_info)

        with open('scripts.json', 'w') as file:
            json.dump(script_data, file, indent=4)

    def load_scripts_from_json(self):
        if os.path.exists('scripts.json'):
            with open('scripts.json', 'r') as file:
                script_data = json.load(file)
                for script in script_data:
                    script_path_input = QLineEdit(script.get('path', ''))

                    # Handle missing frequency_value and frequency_unit
                    frequency_value_input = NoScrollComboBox()
                    frequency_value_input.addItems([str(i) for i in range(1, 61)])  # Allow values 1 to 60
                    frequency_value_input.setCurrentText(script.get('frequency_value', '1'))  # Default to '1'

                    frequency_unit_input = NoScrollComboBox()
                    frequency_unit_input.addItems(['Seconds', 'Minutes', 'Hours', 'Daily', 'Weekly', 'Monthly'])
                    frequency_unit_input.setCurrentText(script.get('frequency_unit', 'Minutes'))  # Default to 'Minutes'

                    start_time_str = script.get('start_time',
                                                QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss'))
                    start_time_input = TimeSelector()
                    start_time_input.set_datetime(datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S'))

                    last_run_label = QLabel(f"Last Run: {script.get('last_run', 'N/A')}")
                    next_run_label = QLabel(f"Next Run: {script.get('next_run', 'N/A')}")
                    start_button = QPushButton('Start')
                    stop_button = QPushButton('Stop')
                    delete_button = QPushButton('Delete')
                    delete_button.setObjectName('delete-button')
                    script_group = QGroupBox('Script Settings')
                    script_layout = QFormLayout()
                    script_layout.addRow('Script Path:', script_path_input)
                    script_layout.addRow('Frequency Value:', frequency_value_input)
                    script_layout.addRow('Frequency Unit:', frequency_unit_input)
                    script_layout.addRow('Start Time:', start_time_input)
                    script_layout.addRow(last_run_label)
                    script_layout.addRow(next_run_label)
                    button_layout = QHBoxLayout()
                    button_layout.addWidget(start_button)
                    button_layout.addWidget(stop_button)
                    button_layout.addWidget(delete_button)
                    script_layout.addRow(button_layout)

                    script_group.setLayout(script_layout)
                    self.scroll_layout.addWidget(script_group)
                    self.scripts.append(
                        (script_group, script_path_input, frequency_value_input, frequency_unit_input, start_time_input,
                         last_run_label, next_run_label,
                         start_button, stop_button, delete_button))
                    delete_button.clicked.connect(partial(self.delete_script, script_group))
                    start_button.clicked.connect(partial(self.start_script, script_group))
                    stop_button.clicked.connect(partial(self.stop_script, script_group))
                    stop_button.setEnabled(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ScriptScheduler()
    sys.exit(app.exec_())
