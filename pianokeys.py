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

SAMPLE_RATE = 44100
VOLUME = 0.4
BASE_DECAY = 1.0
SUSTAIN_DECAY = 2.5
DECAY_SCALING = 2000.0

active_notes = {}
sustain_active = False
current_octave = 4
lock = threading.Lock()

def synth_callback(outdata, frames, time_info, status):
    t = np.arange(frames) / SAMPLE_RATE
    chunk = np.zeros(frames, dtype=np.float32)
    now = time.perf_counter()
    finished = []

    with lock:
        for freq, note in list(active_notes.items()):
            age = now - note["start_time"]

            base_decay = BASE_DECAY * (DECAY_SCALING / (freq + DECAY_SCALING))
            decay = SUSTAIN_DECAY if sustain_active else base_decay

            # Envelope (Attack + Decay)
            attack = 0.008
            if age < attack:
                envelope = age / attack
            else:
                envelope = np.exp(-(age - attack) / decay)

            # Phase
            phase = note["phase"] + 2 * np.pi * freq * t

            # Warmer Harmonic Structure
            wave = (
                    np.sin(phase)
                    + 0.25 * np.sin(2 * phase)
                    + 0.1 * np.sin(3 * phase)
                    + 0.03 * np.sin(4 * phase)
                )

            wave *= envelope

            chunk += wave
            note["phase"] = float(phase[-1] % (2 * np.pi))

            if envelope < 0.0008 and not sustain_active:
                finished.append(freq)

        for f in finished:
            active_notes.pop(f, None)

    if active_notes:
        chunk *= VOLUME / np.sqrt(len(active_notes))

    outdata[:] = chunk.reshape(-1, 1)


# Note Layout
key_to_note = {
    'z': 'C',  's': 'C#',
    'x': 'D',  'd': 'D#',
    'c': 'E',
    'v': 'F',  'g': 'F#',
    'b': 'G',  'h': 'G#',
    'n': 'A',  'j': 'A#',
    'm': 'B'
}


def on_press(key):
    global sustain_active, current_octave

    try:
        if key.char in key_to_note:
            note_name = key_to_note[key.char]
            full_note = note_name + str(current_octave)

            if full_note in piano_freqs:
                freq = piano_freqs[full_note]
                with lock:
                    active_notes[freq] = {
                        "phase": 0.0,
                        "start_time": time.perf_counter()
                    }

        elif key.char in ['1','2','3','4','5','6']:
            current_octave = int(key.char)
            print(f"Octave = {current_octave}")

        elif key.char == ']':
            current_octave = min(6, current_octave + 1)
            print(f"Octave = {current_octave}")

        elif key.char == '[':
            current_octave = max(1, current_octave - 1)
            print(f"Octave = {current_octave}")

        elif key == keyboard.Key.space:
            sustain_active = True

    except AttributeError:
        if key == keyboard.Key.esc:
            return False


def on_release(key):
    global sustain_active
    if key == keyboard.Key.space:
        sustain_active = False


print("Piano | 1–6 = octave | [ ] = shift | SPACE = sustain | ESC = quit")

stream = sd.OutputStream(
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype='float32',
    callback=synth_callback,
    blocksize=2048,
    latency='low'
)

stream.start()

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

stream.stop()
stream.close()