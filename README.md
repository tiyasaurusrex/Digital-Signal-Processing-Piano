#  Digital Signal Processing Piano
### Real-Time Digital Piano Synthesizer Built from First Principles (DSP Project)

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![NumPy](https://img.shields.io/badge/NumPy-Signal%20Processing-orange)
![Audio](https://img.shields.io/badge/Audio-Real--Time-green)
![DSP](https://img.shields.io/badge/Focus-Digital%20Signal%20Processing-purple)
![Status](https://img.shields.io/badge/Project-Active-brightgreen)

readme to be updated shortly!!

This is a real-time digital piano synthesizer built entirely using mathematical waveform generation — **no prerecorded samples, no sound engines, no MIDI libraries**.

Every note is synthesized in real time using additive harmonic modeling and exponential decay envelopes, demonstrating practical applications of **Digital Signal Processing (DSP)** concepts.



# Features

## Real-Time Audio Synthesis
- Pure sine-wave-based generation
- Additive harmonic synthesis
- 44.1 kHz sample rate
- Low-latency streaming via callback

##  True Polyphony
- Multiple simultaneous notes
- Independent phase tracking per note
- Automatic normalization
- Natural overlapping decay

##  Harmonic Tone Modeling
- Fundamental frequency
- 2nd harmonic (brightness)
- 3rd harmonic (depth)
- Subtle phase offsets for realism

## Sustain Pedal Simulation
- Spacebar acts as sustain pedal
- Extended decay time
- Natural resonance behavior

## Frequency-Dependent Decay
- Higher notes decay faster
- Lower notes sustain longer
- Simulates real acoustic piano physics

## Thread-Safe Real-Time Processing
- Audio callback thread
- Keyboard listener thread
- Thread locking prevents race conditions

---

# DSP Concepts Implemented

---

## 1. Digital Sampling Theory

Audio is generated digitally at:

- **Sample Rate:** 44,100 Hz  
- Meaning 44,100 samples per second  

Time vector per buffer:

```python
t = np.arange(frames) / SAMPLE_RATE
```

This converts discrete sample indices into continuous time.

---

## 2. Sine Wave Synthesis

Each note is generated as:

x(t) = sin(2π f t)

Where:
- f = frequency (Hz)
- t = time (seconds)

This produces a pure tone.

---

## 3. Additive Harmonic Synthesis (Timbre Modeling)

Real pianos are not pure sine waves.

We model richer timbre as:

sin(φ)  
+ 0.6 sin(2φ + 0.02)  
+ 0.3 sin(3φ + 0.03)

This adds:
- Fundamental → pitch perception
- 2nd harmonic → brightness
- 3rd harmonic → warmth

This technique is called **Additive Synthesis**.

---

## 4. Exponential Amplitude Envelope

Real piano strings decay exponentially.

Mathematically:

A(t) = e^(-t / τ)

Implemented as:

```python
envelope = np.exp(-age / decay)
```

This creates smooth, natural fade-out.

---

## 5. Frequency-Dependent Decay (Physical Modeling)

High notes decay faster in acoustic pianos.

Modeled as:

τ = BASE_DECAY × (SCALING / (f + SCALING))

Effect:
- Low frequency → long sustain
- High frequency → short sustain

This dramatically improves realism.

---

## 7. Phase Continuity

Each note stores its phase:

```python
note["phase"]
```

Why this matters:
- Prevents audio clicks
- Ensures waveform continuity
- Avoids buffer boundary artifacts

Without this, the sound would glitch.

---

## 7. Polyphonic Mixing & Loudness Normalization

All active notes are summed:

output = Σ wave_i

To prevent clipping:

```python
chunk *= VOLUME / np.sqrt(len(active_notes))
```

This keeps perceived loudness stable even when many notes are played.

---

# System Architecture

```
Keyboard Input Thread
        ↓
Active Notes Dictionary
        ↓
Audio Callback Thread
        ↓
Waveform Generation
        ↓
Harmonic Addition
        ↓
Envelope Application
        ↓
Mixing & Normalization
        ↓
Sound Device Output
```

---

#  Tech Stack

## Core Technologies
- Python 3
- NumPy (Numerical Processing)
- sounddevice (Low-Latency Audio Streaming)
- pynput (Keyboard Event Listener)
- threading (Concurrency Control)

## Audio Configuration
- Sample Rate: 44100 Hz
- Channels: Mono
- Block Size: 4086
- Latency Mode: High (stability prioritized)

---

#  Keyboard Layout

## Lower Octave (C3 – E4)

z s x d c v g b h n j m , l . ; /

## Upper Octave (F4 – E5)

q 2 w 3 e 4 r t 6 y 7 u

## Controls

- SPACE → Sustain Pedal  
- ESC → Quit Program  

---

# 📦 Installation

## Requirements
- Python 3.9+
- pip

## Install Dependencies

```bash
pip install numpy sounddevice pynput
```

## Run the Program

```bash
python piano.py
```

---

#  Internal Execution Flow

1. User presses a key
2. Frequency is added to `active_notes`
3. Audio callback continuously runs
4. For each buffer:
   - Generate sine waves
   - Add harmonics
   - Apply exponential envelope
   - Sum active notes
   - Normalize volume
5. Buffer is streamed to output device

All operations occur in real time.

---

# 🔬Why This Project Is Significant

This project demonstrates:

- Real-time signal synthesis
- Applied digital signal processing
- Thread-safe concurrent architecture
- Audio engineering fundamentals
- Mathematical modeling of acoustic instruments

It bridges theory and implementation — turning equations into playable sound.

---

#  Possible Extensions

- ADSR Envelope (Attack–Decay–Sustain–Release)
- Velocity sensitivity
- Reverb & filtering
- Stereo spatialization
- FM synthesis
- MIDI input support
- Waveform visualization module

---

#  Future Research Directions

- Physical modeling synthesis
- Karplus–Strong string simulation
- Real-time FFT visualization
- Spectral shaping filters
- Audio latency optimization experiments

---

# License

This project is for educational and research purposes.

---

#  Author

Built as a personal Digital Signal Processing project to explore real-time sound synthesis and applied mathematical modeling.

-- Tiyasa Paul

---

# Closing Note

This proves that music does not require samples —  
only mathematics, timing, and careful signal design.

**From pure sine waves to playable piano.**
