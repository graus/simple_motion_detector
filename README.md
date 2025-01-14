# Motion Detector

A simple Home Assistant custom integration that creates a binary sensor for detecting motion using OpenCV’s MOG2 background subtraction and contour analysis, for cameras that do not support motion detection (e.g., some Tuya cameras). This approach is built to be lightweight and simple. 

## Features

- **Motion Detection:** Uses OpenCV MOG2 for background subtraction.
- **Contour Filtering:** Triggers only when a detected contour exceeds a configurable area.
- **Debounce / Cool-down Period:** Ensures that motion is only registered after a series of consecutive frames, preventing rapid state toggling due to noise.
- **Optional Debug Logging:** Easily enable debugging to view detailed processing logs.

## Installation

1. Place the entire simple_motion_detector folder (which includes the manifest.json, binary_sensor.py, etc.) into your Home Assistant custom_components directory.
2. Ensure your Home Assistant Python environment includes the required library:
   **opencv-python-headless** (version 4.x).

## Configuration

Configure the binary sensor in Home Assistant’s configuration file:

```yaml
binary_sensor:
  - platform: simple_motion_detector
    camera_id: "webrtc_cam_garden"
    min_area: 5000
    skip_frames: 3
    width: 640
    height: 360
    blur: true
```

Parameters such as:
- **camera_id:** The identifier for your camera stream.
- **min_area:** The minimum contour area (in pixels) needed to trigger a motion event.
- **skip_frames:** How many frames to skip between processing (to lower CPU usage).
- **width** and **height:** The dimensions to which the incoming video is resized.
- **blur:** Option to enable or disable Gaussian blur for noise reduction.

*Note:* This integration constructs the RTSP stream URL in the following format:
rtsp://<host_IP>:8554/<camera_id>
Adjust the code if your setup is different.

## Usage

- The integration continuously captures frames from the specified RTSP stream.
- It applies background subtraction using OpenCV’s MOG2 and then examines contours.
- When a contour larger than the specified **min_area** is detected, the binary sensor’s state changes to **ON**.
- Once motion ceases for a certain number of consecutive frames, the sensor’s state is updated to **OFF**.
- A cool-down period helps prevent rapid toggling of the sensor state.
- To enable additional debug logging for troubleshooting, adjust your Home Assistant logger settings:
```yaml
logger:
  default: info
  logs:
    custom_components.simple_motion_detector: debug
```

## Inspiration

This integration was inspired by the [PyImageSearch blog post on basic motion detection](https://pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/).

## Author

Created by [@graus](https://github.com/graus).
