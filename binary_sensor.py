import logging
import threading
import cv2
import time
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import STATE_ON, STATE_OFF

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the motion detector binary sensor platform."""
    camera_id = config.get("camera_id")
    min_area = config.get("min_area", 5000)
    skip_frames = config.get("skip_frames", 3)
    width = config.get("width", 640)
    height = config.get("height", 360)
    blur = config.get("blur", False)

    if not camera_id:
        _LOGGER.error("No camera_id configured for motion_detector.")
        return

    camera_source = f"rtsp://localhost:8554/{camera_id}"

    sensor = MotionDetectorBinarySensor(
        name=f"Motion {camera_id}",
        camera_source=camera_source,
        min_area=min_area,
        skip_frames=skip_frames,
        width=width,
        height=height,
        blur=blur,
    )
    add_entities([sensor], True)


class MotionDetectorBinarySensor(BinarySensorEntity):
    """A binary sensor that detects motion using MOG2 + contours in a background thread."""

    def __init__(
        self, 
        name, 
        camera_source, 
        min_area, 
        skip_frames, 
        width, 
        height, 
        blur
    ):
        self._name = name
        self._state = False  # False = no motion
        self._camera_source = camera_source
        self._min_area = min_area
        self._skip_frames = skip_frames
        self._width = width
        self._height = height
        self._blur = blur
        self._stop_thread = False

        self._thread = threading.Thread(target=self._run_detection, daemon=True)
        self._thread.start()

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        """Return True if motion is detected, otherwise False."""
        return self._state

    def _run_detection(self):
        """Continuously capture frames and update motion state."""
        _LOGGER.debug("Starting _run_detection thread for camera: %s", self._camera_source)

        max_retries = 5
        retry_delay = 2  # seconds
        retry_count = 0
        cool_down = 3
        cap = None

        while retry_count < max_retries:
            cap = cv2.VideoCapture(self._camera_source)
            
            if cap.isOpened():
                _LOGGER.debug("Successfully opened video source on retry %d", retry_count)
                break
            
            retry_count += 1
            _LOGGER.error("Failed to open video source: %s (retry %d/%d), waiting %d sec",
                          self._camera_source, retry_count, max_retries, retry_delay)
            time.sleep(retry_delay)

        if not cap or not cap.isOpened():
            _LOGGER.error("Giving up on opening video source: %s", self._camera_source)
            return

        # Create MOG2 background subtractor
        fgbg = cv2.createBackgroundSubtractorMOG2()
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        frame_count = 0

        _LOGGER.debug("VideoCapture opened successfully for %s", self._camera_source)

        while not self._stop_thread:
            ret, frame = cap.read()
            if not ret:
                _LOGGER.debug("Failed to read frame (frame_count=%d). Waiting 1s...", frame_count)
                time.sleep(1)
                continue

            frame_count += 1

            # Debug: Show every frame or skip
            _LOGGER.debug("Captured frame #%d; skip_frames=%d", frame_count, self._skip_frames)

            if frame_count % self._skip_frames != 0:
                _LOGGER.debug("Skipping frame #%d; not processing this frame.", frame_count)
                continue

            # Resize & grayscale
            frame = cv2.resize(frame, (self._width, self._height))
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _LOGGER.debug("Frame #%d resized to %dx%d and converted to grayscale.", 
                          frame_count, self._width, self._height)

            if self._blur:
                gray = cv2.GaussianBlur(gray, (21, 21), 0)
                _LOGGER.debug("Applied GaussianBlur to frame #%d.", frame_count)

            # Background subtraction
            fgmask = fgbg.apply(gray)

            # Morphology to reduce noise
            fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
            fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_DILATE, kernel)

            # Find contours & filter by area
            contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            has_motion = any(cv2.contourArea(c) >= self._min_area for c in contours)

            _LOGGER.debug(
                "Frame #%d: Found %d contours; has_motion=%s (min_area=%d)",
                frame_count,
                len(contours),
                has_motion,
                self._min_area
            )

            # Update internal state if changed
            if has_motion != self._state:
                self._state = has_motion
                _LOGGER.debug("Motion state changed to %s on frame #%d", self._state, frame_count)
                self.schedule_update_ha_state()
                time.sleep(cool_down)

        _LOGGER.debug("Exiting _run_detection thread for camera: %s", self._camera_source)
        cap.release()

    def stop_motion_detection(self):
        """Signal the thread to stop gracefully."""
        self._stop_thread = True

    def on_remove(self):
        """Cleanup when entity is removed."""
        self.stop_motion_detection()
        self._thread.join()

    async def async_will_remove_from_hass(self):
        """Called when entity is about to be removed."""
        self.stop_motion_detection()
        # Wait in a background thread so we don’t block event loop
        await self.hass.async_add_executor_job(self._thread.join)


