"""User-editable paths and voice settings."""

from pathlib import Path
import os


PROJECT_ROOT = Path(__file__).resolve().parent
USER_PROFILE = Path(os.environ.get("USERPROFILE", Path.home()))
LOCAL_APP_DATA = Path(os.environ.get("LOCALAPPDATA", USER_PROFILE / "AppData/Local"))
STANDARD_LOCAL_APP_DATA = USER_PROFILE / "AppData/Local"
if not (LOCAL_APP_DATA / "Programs").is_dir() and (STANDARD_LOCAL_APP_DATA / "Programs").is_dir():
    LOCAL_APP_DATA = STANDARD_LOCAL_APP_DATA
PROGRAM_FILES = Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
PROGRAM_FILES_X86 = Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))

# Add your own folders here. Use None until you have a real path to configure.
PROJECT_PATHS = {
    "project folder": PROJECT_ROOT,
    "voice agent": PROJECT_ROOT,
    "wanderlust": None,
    "college project": None,
}

# These are checked only if the executable is not already available on PATH.
APP_EXECUTABLE_CANDIDATES = {
    "chrome": (
        PROGRAM_FILES / "Google/Chrome/Application/chrome.exe",
        PROGRAM_FILES_X86 / "Google/Chrome/Application/chrome.exe",
        LOCAL_APP_DATA / "Google/Chrome/Application/chrome.exe",
    ),
    "vs code": (
        LOCAL_APP_DATA / "Programs/Microsoft VS Code/Code.exe",
        PROGRAM_FILES / "Microsoft VS Code/Code.exe",
        PROGRAM_FILES_X86 / "Microsoft VS Code/Code.exe",
    ),
    "whatsapp": (
        LOCAL_APP_DATA / "WhatsApp/WhatsApp.exe",
        PROGRAM_FILES / "WhatsApp/WhatsApp.exe",
    ),
}

SCREENSHOT_DIRECTORY = Path.home() / "Pictures" / "VoiceAgentScreenshots"
SPEECH_RATE = 175
CALIBRATION_SECONDS = 0.5
LISTEN_TIMEOUT_SECONDS = 8
PHRASE_TIME_LIMIT_SECONDS = 8
MICROPHONE_RETRY_SECONDS = 5
