
from dotenv import load_dotenv
load_dotenv()
import os
import sys
import json
import time
import subprocess
import threading
import platform
import webbrowser
from datetime import datetime
from typing import Optional

import anthropic


try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False

try:
    import pyautogui
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False




def open_application(app_name: str) -> str:
    """Open an application by name."""
    system = platform.system()
    app_name_lower = app_name.lower().strip()

    known_apps = {
        "browser": {"Darwin": "open -a Safari", "Windows": "start chrome", "Linux": "xdg-open https://google.com"},
        "chrome":  {"Darwin": "open -a 'Google Chrome'", "Windows": "start chrome", "Linux": "google-chrome"},
        "vscode":  {"Darwin": "open -a 'Visual Studio Code'", "Windows": "code", "Linux": "code"},
        "terminal":{"Darwin": "open -a Terminal", "Windows": "start cmd", "Linux": "x-terminal-emulator"},
        "spotify": {"Darwin": "open -a Spotify", "Windows": "start spotify", "Linux": "spotify"},
        "notes":   {"Darwin": "open -a Notes", "Windows": "start notepad", "Linux": "gedit"},
        "calculator":{"Darwin":"open -a Calculator","Windows":"start calc","Linux":"gnome-calculator"},
        "finder":  {"Darwin": "open ~", "Windows": "start explorer", "Linux": "nautilus ~"},
    }

    cmd = None
    for key, cmds in known_apps.items():
        if key in app_name_lower:
            cmd = cmds.get(system)
            break

    if not cmd:
        if system == "Darwin":
            cmd = f"open -a '{app_name}'"
        elif system == "Windows":
            cmd = f"start {app_name}"
        else:
            cmd = app_name

    try:
        subprocess.Popen(cmd, shell=True)
        return f"Opened: {app_name}"
    except Exception as e:
        return f"Could not open {app_name}: {e}"


def control_media(action: str) -> str:
    """Control media playback (play/pause/next/previous/volume)."""
    system = platform.system()
    action = action.lower()

    if not GUI_AVAILABLE:
        return f"pyautogui not installed — cannot send media keys (simulated: {action})"

    key_map = {
        "play": "playpause", "pause": "playpause", "toggle": "playpause",
        "next": "nexttrack",  "skip": "nexttrack",
        "previous": "prevtrack", "back": "prevtrack",
        "mute": "volumemute",
        "volume up": "volumeup",   "louder": "volumeup",
        "volume down": "volumedown", "quieter": "volumedown",
    }

    for keyword, key in key_map.items():
        if keyword in action:
            try:
                pyautogui.press(key)
                return f"Media: {action}"
            except Exception as e:
                return f"Media key error: {e}"

    return f"Unknown media action: {action}"


def scroll_page(direction: str, amount: int = 3) -> str:
    """Scroll the current page up or down."""
    if not GUI_AVAILABLE:
        return f"pyautogui not installed — cannot scroll (simulated: {direction})"
    try:
        clicks = amount if "down" in direction.lower() else -amount
        pyautogui.scroll(clicks)
        return f"Scrolled {direction} by {amount}"
    except Exception as e:
        return f"Scroll error: {e}"


def search_web(query: str) -> str:
    """Open a web search for a query."""
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Searching for: {query}"


def type_text(text: str) -> str:
    """Type text at the current cursor position."""
    if not GUI_AVAILABLE:
        return f"pyautogui not installed — cannot type (simulated: {text})"
    try:
        pyautogui.typewrite(text, interval=0.05)
        return f"Typed: {text}"
    except Exception as e:
        return f"ype error: {e}"


def take_screenshot() -> str:
    """Take a screenshot and save it to the desktop."""
    if not GUI_AVAILABLE:
        return "pyautogui not installed — cannot take screenshot"
    try:
        desktop = os.path.expanduser("~/Desktop")
        filename = os.path.join(desktop, f"screenshot_{datetime.now().strftime('%H%M%S')}.png")
        pyautogui.screenshot(filename)
        return f"Screenshot saved: {filename}"
    except Exception as e:
        return f"Screenshot error: {e}"



TOOLS = [
    {
        "name": "open_application",
        "description": "Open a desktop application by name (e.g. browser, Spotify, VS Code, terminal, calculator).",
        "input_schema": {
            "type": "object",
            "properties": {
                "app_name": {"type": "string", "description": "Name of the application to open."}
            },
            "required": ["app_name"],
        },
    },
    {
        "name": "control_media",
        "description": "Control media playback: play, pause, next track, previous track, volume up/down, mute.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "Media action: play, pause, next, previous, volume up, volume down, mute."}
            },
            "required": ["action"],
        },
    },
    {
        "name": "scroll_page",
        "description": "Scroll the currently focused window up or down.",
        "input_schema": {
            "type": "object",
            "properties": {
                "direction": {"type": "string", "enum": ["up", "down"]},
                "amount":    {"type": "integer", "description": "Number of scroll steps (1-10).", "default": 3},
            },
            "required": ["direction"],
        },
    },
    {
        "name": "search_web",
        "description": "Open a Google search in the default browser.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query."}
            },
            "required": ["query"],
        },
    },
    {
        "name": "type_text",
        "description": "Type text at the current cursor position.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to type."}
            },
            "required": ["text"],
        },
    },
    {
        "name": "take_screenshot",
        "description": "Take a screenshot and save it to the Desktop.",
        "input_schema": {"type": "object", "properties": {}},
    },
]

TOOL_FUNCTIONS = {
    "open_application": lambda inp: open_application(inp["app_name"]),
    "control_media":    lambda inp: control_media(inp["action"]),
    "scroll_page":      lambda inp: scroll_page(inp["direction"], inp.get("amount", 3)),
    "search_web":       lambda inp: search_web(inp["query"]),
    "type_text":        lambda inp: type_text(inp["text"]),
    "take_screenshot":  lambda inp: take_screenshot(),
}



SYSTEM_PROMPT = """You are an AI desktop control agent. You receive voice or text commands from the user
and execute the appropriate system action using your tools.

Rules:
- Always use a tool never just describe what you would do.
- Choose the most specific matching tool.
- For ambiguous commands, pick the most likely intent.
- After executing, confirm what you did in one short sentence."""

client = anthropic.Anthropic()


def run_agent(user_input: str) -> str:
    """Send input to Claude with tool-use and execute the chosen action."""
    messages = [{"role": "user", "content": user_input}]

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=messages,
    )


    while response.stop_reason == "tool_use":
        tool_uses = [b for b in response.content if b.type == "tool_use"]
        tool_results = []

        for tool_use in tool_uses:
            fn = TOOL_FUNCTIONS.get(tool_use.name)
            if fn:
                result = fn(tool_use.input)
            else:
                result = f"Unknown tool: {tool_use.name}"

            print(f" Tool: {tool_use.name}({json.dumps(tool_use.input)}) → {result}")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": result,
            })


        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=256,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )


    text_blocks = [b for b in response.content if hasattr(b, "text")]
    return text_blocks[0].text if text_blocks else "(no response)"



def listen_once(timeout: int = 5) -> Optional[str]:
    """Listen for one voice command and return the transcript."""
    if not SPEECH_AVAILABLE:
        print("speech_recognition not installed. Run: pip install SpeechRecognition pyaudio")
        return None

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening…")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=8)
            text = recognizer.recognize_google(audio)
            print(f"   Heard: \"{text}\"")
            return text
        except sr.WaitTimeoutError:
            print("   (no speech detected)")
            return None
        except sr.UnknownValueError:
            print("   (could not understand audio)")
            return None
        except sr.RequestError as e:
            print(f"   (recognition error: {e})")
            return None



BANNER = r"""
╔══════════════════════════════════════════════════════╗
║                AI Sound Control Agent                ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
"""

MENU = """
Modes:
  [1] Voice continuous loop    (microphone → Claude → action)
  [2] Text input               (type command → Claude → action)
  [q] Quit
"""


def main():
    print(BANNER)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY environment variable not set.")
        print("Export it before running:  export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    print(f"Dependencies:")
    print(f"  Speech Recognition: {'✅' if SPEECH_AVAILABLE else '❌ (pip install SpeechRecognition pyaudio)'}")
    print(f"  GUI Control:        {'✅' if GUI_AVAILABLE else '❌ (pip install pyautogui)'}")
    print()

    while True:
        print(MENU)
        choice = input("Select mode: ").strip().lower()

        if choice == "1":
            if not SPEECH_AVAILABLE:
                print("Install speech_recognition to use voice mode.")
                continue
            print("\nVoice mode — say a command (Ctrl-C to stop)\n")
            try:
                while True:
                    text = listen_once(timeout=6)
                    if text:
                        print(f"\nCommand: {text}")
                        reply = run_agent(text)
                        print(f"Agent:   {reply}\n")
            except KeyboardInterrupt:
                print("\nStopped voice mode.")

        elif choice == "2":
            print("\n  Text mode — type your command (empty line to go back)\n")
            while True:
                cmd = input("Command> ").strip()
                if not cmd:
                    break
                reply = run_agent(cmd)
                print(f" Agent: {reply}\n")

        elif choice == "q":
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
