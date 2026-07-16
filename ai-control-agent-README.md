# AI Control Agent

Control your desktop with voice commands or hand gestures. Speech and camera input are translated into natural-language commands, sent to Anthropic's Claude with tool use, and executed as real OS actions.

**Demo:** https://youtu.be/qytfNAuzK7U

## How it works

```
Microphone / Webcam → Speech Recognition / MediaPipe → Claude (Tool Use) → OS Action
```

1. Input is captured as text (speech-to-text) or as a gesture label (hand landmark classification)
2. Claude receives the command along with a set of tool definitions and decides which action to run
3. The agent loop executes the chosen tool locally and reports back

## Features

- **Voice mode** – continuous listening loop, speak commands like "open Spotify" or "scroll down"
- **Gesture mode** – real-time hand tracking with OpenCV + MediaPipe (thumbs up, fist, open hand, peace, pointing)
- **Text mode** – type commands directly, useful for testing
- Cross-platform actions: open apps, control media playback, scroll, web search, type text, take screenshots
- Multi-step agentic loop – Claude can chain several tool calls for a single command

## Gesture mapping

| Gesture | Action |
|---|---|
| Thumbs up | Play media |
| Thumbs down | Pause media |
| Open hand | Scroll down |
| Fist | Scroll up |
| Peace | Screenshot |
| Pointing up | Open browser |

## Setup

```bash
git clone https://github.com/tomertir/ai-control-agent.git
cd ai-control-agent
pip install -r requirements.txt

cp .env.example .env   # add your ANTHROPIC_API_KEY

python agent.py
```

Voice and gesture modes require optional dependencies (`SpeechRecognition`, `pyaudio`, `opencv-python`, `mediapipe`, `pyautogui`). The program detects what's installed and enables modes accordingly.

## Tech

Python · Anthropic API (tool use) · OpenCV · MediaPipe · SpeechRecognition · PyAutoGUI

Works on macOS, Windows and Linux.
