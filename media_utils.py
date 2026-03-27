import cv2
import numpy as np
import base64
import pyaudio
import asyncio

# --- VIDEO AS ASCII ---
ASCII_CHARS = ["@", "%", "#", "*", "+", "=", "-", ":", ".", " "]

def frame_to_ascii(frame, width=80):
    # Resize frame
    height, original_width = frame.shape[:2]
    aspect_ratio = height / original_width
    new_height = int(width * aspect_ratio * 0.5)
    resized_frame = cv2.resize(frame, (width, new_height))
    
    # Grayscale
    gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
    
    # Map pixels to characters
    pixels = gray_frame.flatten()
    ascii_str = "".join([ASCII_CHARS[pixel // 26] for pixel in pixels])
    
    # Split into lines
    ascii_frame = "\n".join([ascii_str[i : i + width] for i in range(0, len(ascii_str), width)])
    return ascii_frame

# --- AUDIO CAPTURE ---
class AudioManager:
    def __init__(self):
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.p = pyaudio.PyAudio()
        self.stream = None

    def start_recording(self):
        self.stream = self.p.open(format=self.format,
                                  channels=self.channels,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.chunk)

    def get_chunk(self):
        if self.stream:
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            return base64.b64encode(data).decode()
        return None

    def play_chunk(self, b64_data):
        if not self.stream:
            self.stream = self.p.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.rate,
                                      output=True,
                                      frames_per_buffer=self.chunk)
        data = base64.b64decode(b64_data)
        self.stream.write(data)
