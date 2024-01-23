
# Synchronize-NBA-Calendar

[![Python](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-orange.svg)](https://flask.palletsprojects.com/en/2.0.x/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

## Description

SoMyCal is a Python Flask application that allow users to sync their calendar with NBA teams' schedules. The app is designed to work on any device supporting the iCalendar format (ICS), providing a web interface and oauth integration with Google.

This project serves a dual purpose - it not only acts as a useful NBA calendar synchronization tool but also was initiated to assist a friend in understanding Python and supporting their own programming endeavors.

## Features

- **Calendar Sync:** Easily synchronize NBA team schedules with your preferred calendar application that supports the ICS format (like, every calendar app)

- **Cross-Device Compatibility:** Access the application on any device with ICS support, ensuring flexibility and convenience.

- **Web Interface:** The user-friendly web interface makes navigation and synchronization a breeze.

- **Google OAuth :** Seamlessly connect with your Google account for a simple and fast experience

## Getting Started

Follow these steps to get started with the project:

1. Clone the repository:

    ```bash
    git clone https://github.com/itsmrval/somycal.git
    ```

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Copy then edit the env files:

    ```bash
    cp example.env .env
    ```

4. Run the Flask application:

    ```bash
    python app.py
    ```

4. Access the application through your web browser at [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Screenshots


![Screenshot 2](https://i.ibb.co/DLLbTv3/Screenshot-6.png)
*Quick dashboard screenshot*

## Live Demo 
Check out the live demo of the application currently running at [https://somycal.com](https://somycal.com).

## Contribution

Contributions are welcome! If you'd like to contribute to the project send a PR

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
