# pi-rfid-reader

The `pi-rfid-reader` project is a simple and lightweight Python application designed to run on Raspberry Pi. It utilizes the MFRC522 RFID reader to scan RFID tags and provides a single REST endpoint to retrieve scanned tag data. This project is ideal for hobbyists and professionals looking to integrate RFID capabilities into their Raspberry Pi projects.

## Features

- **Simple REST API**: Offers a single endpoint to scan RFID tags.
- **Asynchronous Handling**: Utilizes `aiohttp` for asynchronous request handling.
- **Command-Line Configuration**: Configure log file location and server port via command-line arguments.

## Prerequisites

Before you install and run the `pi-rfid-reader`, ensure you have the following:

- Raspberry Pi (Any model that supports GPIO pins and Python 3)
- Python 3.6 or higher installed on your Raspberry Pi
- MFRC522 RFID reader module properly connected to your Raspberry Pi

## Connect the reader to the pi

![PiZero_FRID-RC522_Steckplatine](https://github.com/nf-gmbh/pi-rfid-reader/assets/308471/e37e41e5-5b9f-4ad3-8e32-744f5c13c7d7)
Image source: https://devdrik.de/pi-mit-rfid-rc522/

## Installation

Follow these steps to get `pi-rfid-reader` up and running on your Raspberry Pi:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/schub/pi-rfid-reader.git
   cd pi-rfid-reader

2. **Setup Python Virtual Environment (Optional but recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate

3. **Install Required Packages:**
   ```bash
   pip install -r requirements.txt

## Configuration

The application requires you to specify the log file location, the server port and the timeout for the reader. These can be set via command-line arguments when starting the server.

## Usage

To start the pi-rfid-reader, use the following command:

   ```bash
   python app.py --log path/to/your/logfile.log --port 8080 --timeout 5

Replace `path/to/your/logfile.log` with the path where you want the logs to be saved and `8080` with your preferred port number. Timeout is optional and defaults to 5sec.

## Testing the API

Once the server is running, you can test the RFID scanning functionality by accessing:

`http://<raspberry-pi-ip-address>:8080/scan`

This endpoint will attempt to scan an RFID tag and return its ID and text data in JSON format.

## misc

To start in kiosk mode, edit `~/.config/wayfire.ini` and add the following lines:

```
[autostart]
panel = wfrespawn wf-panel-pi
background = wfrespawn pcmanfm --desktop --profile LXDE-pi
xdg-autostart = lxsession-xdg-autostart
chromium = chromium-browser https://example.com --kiosk --noerrdialogs --disable-infobars --no-first-run --ozone-platform=wayland --enable-features=OverlayScrollbar
```

