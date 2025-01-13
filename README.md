# Motion Detector

A simple Home Assistant custom integration that creates a binary sensor for detecting motion using OpenCV’s MOG2 background subtraction and contour analysis. This integration was inspired by the [PyImageSearch blog post on basic motion detection](https://pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/).

## Features

- **Motion Detection:** Uses OpenCV MOG2 for background subtraction.
- **Contour Filtering:** Triggers only when a detected contour exceeds a configurable area.
- **Cool-down Period:** Implements a delay after motion is detected to prevent rapid state toggling.
- **Optional Debug Logging:** Easily enable debugging to view detailed processing logs.

## Installation

1. Place the entire `simple_motion_detector` folder (which includes the `manifest.json`, `binary_sensor.py`, etc.) into your Home Assistant `custom_components` directory.
2. Ensure your Home Assistant Python environment includes the required library:  
   **opencv-python-headless** (version 4.x).

## Configuration

Configure the binary sensor in Home Assistant’s configuration file by providing parameters such as:
- **camera_id:** The identifier for your camera stream.
- **min_area:** The minimum contour area (in pixels) needed to trigger a motion event.
- **skip_frames:** How many frames to skip between processing (to lower CPU usage).
- **width** and **height:** The dimensions to which the incoming video is resized.
- **blur:** Option to enable or disable Gaussian blur for noise reduction.

*Note:* This integration constructs the RTSP stream URL in the following format:  
`rtsp://<host_IP>:8554/<camera_id>`  
Adjust the code if your setup is different.

## Usage

- When a contour larger than the specified **min_area** is detected, the binary sensor’s state changes to **ON**.
- A cool-down period (default is 3 seconds) is enforced after detecting motion before monitoring resumes.
- To enable additional debug logging for troubleshooting, adjust your Home Assistant logger settings as needed.

## Inspiration

This integration was inspired by the [PyImageSearch blog post on basic motion detection](https://pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/).

## Author

Created by [@graus](https://github.com/graus/simple_motion_detector).

