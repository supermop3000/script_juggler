# Python Script Scheduler

The Python Script Scheduler is a PyQt5-based GUI application that allows users to schedule and run Python scripts at specified intervals. It supports features like customizable scheduling, saving and loading configurations, and error handling with email notifications.

---

## Features

- **User-Friendly GUI**: Built with PyQt5, the application provides a simple interface for scheduling Python scripts.
- **Custom Scheduling**:
  - Specify frequency values and units (e.g., seconds, minutes, hours, daily, weekly, monthly).
  - Select start times for each script.
- **Save and Load Settings**: Save script configurations to a JSON file and reload them on startup.
- **Error Notifications**: Automatically sends error reports via email if a script encounters an issue during execution.
- **Virtual Environment Support**: Executes scripts using their respective virtual environments.
- **Start/Stop Controls**: Start or stop individual scripts as needed.
- **Last Run and Next Run Info**: Displays information about the last and next execution times.

---

## Requirements

- Python 3.6+
- PyQt5
- Shotgun API (`shotgun_api3`)
- Other standard Python libraries: `smtplib`, `email`, `subprocess`, `json`, `datetime`, `sched`, and `threading`

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd python-script-scheduler
   ```

2. **Install Dependencies**:
   ```bash
   pip install PyQt5 shotgun-api3
   ```

3. **Set Up Email Configuration**:
   Update the `EMAIL` and `PASSWORD` variables in the code with your email credentials to enable error notifications.

4. **Create a Style File**:
   - Add a `style.css` file to the same directory for custom styling.

5. **Run the Application**:
   ```bash
   python script_scheduler.py
   ```

---

## How to Use

### 1. Add a Script
- Click the `Add Script` button.
- Enter the script path and configure the frequency (value and unit).
- Set the start time using the date and time selectors.

### 2. Start a Script
- Click the `Start` button to schedule the script.
- The script's fields will be disabled while it is running.
- The application will display the last and next run times.

### 3. Stop a Script
- Click the `Stop` button to halt the script execution.
- The fields will be re-enabled for editing.

### 4. Delete a Script
- Click the `Delete` button to remove the script from the scheduler.

### 5. Save Settings
- Click the `Save Settings` button to save all script configurations to `scripts.json`.

### 6. Load Settings
- The application automatically loads saved settings from `scripts.json` when launched.

---

## Configuration

### JSON Structure
The `scripts.json` file stores script configurations in the following format:
```json
[
  {
    "path": "path/to/your/script.py",
    "frequency_value": "10",
    "frequency_unit": "Minutes",
    "start_time": "2025-01-24 12:00:00",
    "last_run": "N/A",
    "next_run": "N/A"
  }
]
```

---

## Error Reporting

If a script fails to execute, an email will be sent to `chad@mrwolf.com` with the error details. Ensure the `EMAIL` and `PASSWORD` variables are configured correctly to enable this feature.

---

## Project Structure
```
python-script-scheduler/
|-- script_scheduler.py    # Main application file
|-- scripts.json           # JSON file for saving and loading configurations
|-- style.css              # CSS file for custom styling (optional)
```

---

## Future Enhancements
- Add more advanced scheduling options (e.g., cron-like scheduling).
- Enable logging for better debugging and tracking of script execution.
- Support for pausing and resuming scripts.
- Add user authentication for enhanced security.

---

## License
This project is open-source and available under the [MIT License](LICENSE).

---

## Acknowledgments
Special thanks to the team at Mr. Wolf for their contributions and support in developing this tool.

---

## Contact
For questions or support, please reach out to:
- **Email**: chad@mrwolf.com
- **GitHub**: [Your Repository Link]

