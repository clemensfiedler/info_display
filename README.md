# Infodisplay

This project contains the code used to create an infoterminal based on raspbberry pi and a 7.5 inch waveshare, 2 colour e-paper display.

## Installation

1. Operating system: (Raspbian)[https://www.raspberrypi.org/downloads/raspbian/]
2. Raspbian comes preinstalled with Python and Pip. Otherwise both need to be installed
3. The display requires the pythonpackges: libjpeg-dev(```sudo apt-get install libjpeg-dev```), pillow (```pip install Pillow```), spidev(```pip install spidev```)
4. See `requirements.txt` for necessary packages
4. By default RSI is deactivated. It can be activated in the advanced settings.
5. Get credentials for open weather
6. Setup Google API for calendar (guide)[https://developers.google.com/calendar/quickstart/python]
7. generate  `settings.json` and `credentials.json`

## Run

- run `test.py` to verify. This generates a bmp file. 
- run `run.py [-r 10] [-t 24] ` to start the screen. 
  - `-r`: refrehsrate in minutes
  - `-t`: duration n hours.
