# Digital Signal Processing PERSONAL PROJECT

import numpy as np
import sounddevice as sd
from pynput import keyboard
import threading, time

# Frequencies
piano_freqs = {
    "A0": 27.50, "B0": 30.87,
    "C1": 32.70, "C#1": 34.65, "D1": 36.71, "D#1": 38.89, "E1": 41.20,
    "F1": 43.65, "F#1": 46.25, "G1": 49.00, "G#1": 51.91, "A1": 55.00, "A#1": 58.27, "B1": 61.74,
    "C2": 65.41, "C#2": 69.30, "D2": 73.42, "D#2": 77.78, "E2": 82.41,
    "F2": 87.31, "F#2": 92.50, "G2": 98.00, "G#2": 103.83, "A2": 110.00, "A#2": 116.54, "B2": 123.47,
    "C3": 130.81, "C#3": 138.59, "D3": 146.83, "D#3": 155.56, "E3": 164.81,
    "F3": 174.61, "F#3": 185.00, "G3": 196.00, "G#3": 207.65, "A3": 220.00, "A#3": 233.08, "B3": 246.94,
    "C4": 261.63, "C#4": 277.18, "D4": 293.66, "D#4": 311.13, "E4": 329.63,
    "F4": 349.23, "F#4": 370.00, "G4": 392.00, "G#4": 415.30, "A4": 440.00, "A#4": 466.16, "B4": 493.88,
    "C5": 523.25, "C#5": 554.37, "D5": 587.33, "D#5": 622.25, "E5": 659.26,
    "F5": 698.46, "F#5": 739.99, "G5": 783.99, "G#5": 830.61, "A5": 880.00, "A#5": 932.33, "B5": 987.77,
    "C6": 1046.50
}

# Settings
SAMPLE_RATE = 44100
VOLUME = 0.45
BASE_DECAY = 0.8        # natural fade
SUSTAIN_DECAY = 2.0     # longer when pedal held
DECAY_SCALING = 1800.0  # high notes fade faster

active_notes = {}
sustain_active = False
lock = threading.Lock()

# Audio callback
def synth_callback(outdata, frames, time_info, status):
    t = np.arange(frames) / SAMPLE_RATE
    chunk = np.zeros(frames, dtype=np.float32)
    now = time.perf_counter()
    finished = []

    with lock:
        # Generate all notes in one go
        for freq, note in list(active_notes.items()):
            age = now - note["start_time"]

            # Adaptive decay
            base_decay = BASE_DECAY * (DECAY_SCALING / (freq + DECAY_SCALING))
            decay = SUSTAIN_DECAY if sustain_active else base_decay
            envelope = np.exp(-age / decay)
            env_val = float(envelope if np.isscalar(envelope) else envelope[-1])

            # Harmonic-rich wave
            phase = note["phase"] + 2 * np.pi * freq * t
            wave = (np.sin(phase)
                    + 0.6 * np.sin(2 * phase + 0.02)
                    + 0.3 * np.sin(3 * phase + 0.03)) * envelope

            chunk += wave
            note["phase"] = float(phase[-1] % (2 * np.pi))

            # Drop finished notes
            if env_val < 0.001 and not sustain_active:
                finished.append(freq)

        for f in finished:
            active_notes.pop(f, None)

    # Normalize once (outside loop)
    if active_notes:
        chunk *= VOLUME / np.sqrt(len(active_notes))
    else:
        chunk *= 0.0

    outdata[:] = chunk.reshape(-1, 1)

#Key mapping
key_to_note = {
    # Lower octave (C3–E4)
    'z': 'C3', 's': 'C#3', 'x': 'D3', 'd': 'D#3', 'c': 'E3',
    'v': 'F3', 'g': 'F#3', 'b': 'G3', 'h': 'G#3', 'n': 'A3',
    'j': 'A#3', 'm': 'B3', ',': 'C4', 'l': 'C#4', '.': 'D4',
    ';': 'D#4', '/': 'E4',

    # Upper octave (F4–E5)
    'q': 'F4', '2': 'F#4', 'w': 'G4', '3': 'G#4', 'e': 'A4',
    '4': 'A#4', 'r': 'B4', 't': 'C5', '6': 'C#5', 'y': 'D5',
    '7': 'D#5', 'u': 'E5'
}


# Keyboard events
def on_press(key):
    global sustain_active
    try:
        if key.char in key_to_note:
            note = key_to_note[key.char]
            freq = piano_freqs[note]
            with lock:
                active_notes[freq] = {"phase": 0.0, "start_time": time.perf_counter()}
        elif key == keyboard.Key.space:
            sustain_active = True
            print("Sustain pedal ON")
    except AttributeError:
        if key == keyboard.Key.esc:
            print("\nPAUSE")
            return False

def on_release(key):
    global sustain_active
    if key == keyboard.Key.space:
        sustain_active = False
        print("Sustain pedal OFF")

# Run
print("Fire Piano| SPACE = sustain | ESC = quit\n")

stream = sd.OutputStream(
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype='float32',
    callback=synth_callback,
    blocksize=4086,   #stability buffer
    latency='high'
)

stream.start()
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
stream.stop()
stream.close()





