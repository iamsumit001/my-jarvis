# My Jarvis

A small, voice-controlled Windows desktop assistant. My Jarvis turns spoken English commands into a short, allowlisted set of desktop actions.

## What it can do

- Listen through the default microphone and speak short replies.
- Open YouTube, Google, Chrome, VS Code, WhatsApp, Calculator, Notepad, and File Explorer.
- Search Google for a phrase.
- Search YouTube for a song or artist by name. This opens search results; it does not automatically play a track.
- Open a folder you configure in config.py.
- Save a screenshot in your Pictures folder or lock the Windows session.
- Stop listening when you say **“stop assistant”**, **“stop”**, **“exit”**, **“quit”**, or **“goodbye”**.

## How it works

1. The microphone captures a spoken phrase.
2. SpeechRecognition sends the audio to Google's online speech-recognition service and returns a transcript.
3. The command processor matches the transcript against known phrases.
4. The action executor runs a predefined action. Recognized text is never passed to a shell as a command.
5. pyttsx3 generates spoken replies locally when a compatible system voice is available.

This is a small first version: it does not include a wake word, an LLM, a custom-trained language model, or smart-home controls. Its command phrases are currently in English.

## Requirements

- Windows 10 or 11, 64-bit
- 64-bit Python 3.10–3.12
- A microphone and speakers or headphones
- Internet access for speech recognition and web searches

## Set up

Open PowerShell in the project folder and run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If the environment is active, you can use python instead of .\.venv\Scripts\python.exe.

## Run

### In VS Code

1. Open the project folder in VS Code.
2. Open **Run and Debug**.
3. Select **Run my Jarvis voice assistant**.
4. Press **F5**.

The assistant's messages appear in the Debug Console. Use the Stop button in the debug toolbar to end the session.

### In PowerShell

```powershell
.\.venv\Scripts\python.exe main.py
```

Say **“stop assistant”** (or another exit phrase above) to stop it. You can also press **Ctrl+C** in the terminal.

## Voice command examples

| Say | Result |
| --- | --- |
| “Open YouTube” | Opens YouTube |
| “Open Google” | Opens Google |
| “Open Chrome” | Opens Chrome if installed |
| “Open VS Code” | Opens VS Code if installed |
| “Open WhatsApp” | Opens the desktop app if found, otherwise WhatsApp Web |
| “Open Calculator” | Opens Windows Calculator |
| “Open Notepad” | Opens Notepad |
| “Open File Explorer” | Opens File Explorer |
| “Search Google for Java arrays” | Opens Google results for the phrase |
| “Search YouTube for Arijit Singh” | Opens YouTube results for the phrase |
| “Play Tum Hi Ho on YouTube” | Searches YouTube for the song |
| “Take a screenshot” | Saves a screenshot under Pictures\VoiceAgentScreenshots |
| “Lock my computer” | Locks the Windows session |
| “Stop assistant” | Exits the assistant |

## Configure your folders

Edit PROJECT_PATHS in config.py. Replace or add names and point them to folders on your computer:

```python
PROJECT_PATHS = {
    "project folder": PROJECT_ROOT,
    "my notes": Path(r"C:\Users\your-name\Documents\Notes"),
}
```

Then say **“Open my notes”**. Use a folder path that exists on your computer. The built-in app paths in config.py can also be adjusted if an application is installed in a nonstandard location.

## Privacy and safety

- Speech recognition uses Google's online service. Microphone audio is sent to that service for transcription, so this feature requires internet access.
- Voice replies are generated on your computer with pyttsx3 when available.
- Browser searches open in your default browser.
- Spoken text is matched against explicit actions; it is not executed as a shell command.
- Screenshots are saved locally in your Windows Pictures folder.

## Troubleshooting

- **Python is not found:** install 64-bit Python 3.10–3.12 and reopen PowerShell or VS Code.
- **PyAudio installation fails:** upgrade pip and confirm that your Python installation is 64-bit. If pip has no compatible wheel for your Python version, use one of the versions listed above.
- **The microphone is unavailable:** choose a default input device and check Windows microphone access for desktop apps.
- **Speech recognition is unavailable:** check your internet connection.
- **An app does not open:** install it or add its executable location to APP_EXECUTABLE_CANDIDATES in config.py.
- **Voice replies are silent:** check the Windows output device. Responses are also printed in the console.

## Project files

- main.py — microphone loop, speech recognition, and voice output
- commands.py — phrase matching and allowlisted Windows actions
- config.py — voice settings, app locations, and configurable folder aliases
- requirements.txt — Python dependencies
- .vscode/ — VS Code launch profile and workspace interpreter setting

## License

No license file is included yet. Choose and add a license before granting others permission to reuse or redistribute this project.