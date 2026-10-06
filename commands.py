"""Allowlisted voice commands and their Windows actions."""

from __future__ import annotations

import ctypes
import os
import re
import shutil
import subprocess
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

import config


@dataclass(frozen=True)
class Command:
    action: str
    target: str = ""


@dataclass(frozen=True)
class ActionResult:
    message: str
    should_exit: bool = False


class CommandProcessor:
    """Turn recognized phrases into explicit, safe actions."""

    EXIT_PHRASES = {"stop", "exit", "quit", "goodbye", "stop assistant"}
    OPEN_TARGETS = {
        "youtube": Command("website", "youtube"),
        "you tube": Command("website", "youtube"),
        "google": Command("website", "google"),
        "whatsapp": Command("app", "whatsapp"),
        "chrome": Command("app", "chrome"),
        "google chrome": Command("app", "chrome"),
        "vs code": Command("app", "vs code"),
        "visual studio code": Command("app", "vs code"),
        "calculator": Command("windows_app", "calculator"),
        "calc": Command("windows_app", "calculator"),
        "notepad": Command("windows_app", "notepad"),
        "file explorer": Command("windows_app", "file explorer"),
        "explorer": Command("windows_app", "file explorer"),
        "files": Command("windows_app", "file explorer"),
    }

    def parse(self, phrase: str) -> Command:
        original = phrase.strip()
        text = self._clean(original)
        if text in self.EXIT_PHRASES:
            return Command("exit")
        if text in {"take a screenshot", "take screenshot", "screenshot"}:
            return Command("screenshot")
        if text in {"lock my computer", "lock computer", "lock my pc", "lock pc"}:
            return Command("lock")

        search = re.match(
            r"^search google for\s+(.+?)[.!?]*\s*$", original, flags=re.IGNORECASE
        )
        if search:
            return Command("search", search.group(1).strip())

        youtube_search = re.match(
            r"^search\s+(?:youtube(?:\s+music)?|music)\s+for\s+(.+?)[.!?]*\s*$",
            original,
            flags=re.IGNORECASE,
        )
        if youtube_search:
            return Command("music", youtube_search.group(1).strip())

        play_music = re.match(
            r"^play\s+(.+?)(?:\s+on\s+youtube(?:\s+music)?)?[.!?]*\s*$",
            original,
            flags=re.IGNORECASE,
        )
        if play_music:
            query = play_music.group(1).strip()
            if self._clean(query) in {"music", "some music", "a song", "my music"}:
                return Command("music", "music")
            return Command("music", query)

        opening = re.match(r"^open\s+(.+)$", text, flags=re.IGNORECASE)
        if opening:
            target = opening.group(1).strip()
            target = re.sub(r"^(?:my\s+)", "", target)
            target = self._clean(target)
            if target in self.OPEN_TARGETS:
                return self.OPEN_TARGETS[target]
            if target in config.PROJECT_PATHS:
                return Command("project", target)
            target = re.sub(r"\s+project$", "", target)
            if target in config.PROJECT_PATHS:
                return Command("project", target)

        return Command("unknown", phrase.strip())

    @staticmethod
    def _clean(text: str) -> str:
        text = re.sub(r"[.!?,;:]+$", "", text.lower().strip())
        return re.sub(r"\s+", " ", text)


class ActionExecutor:
    """Execute only actions produced by the command allowlist."""

    WEBSITES = {
        "youtube": "https://www.youtube.com/",
        "google": "https://www.google.com/",
    }
    WEBSITE_LABELS = {"youtube": "YouTube", "google": "Google"}
    YOUTUBE_URL = "https://www.youtube.com/"
    WINDOWS_COMMANDS = {
        "calculator": "calc.exe",
        "notepad": "notepad.exe",
        "file explorer": "explorer.exe",
    }
    APP_LABELS = {"chrome": "Chrome", "vs code": "VS Code", "whatsapp": "WhatsApp"}

    def execute(self, command: Command) -> ActionResult:
        try:
            if command.action == "exit":
                return ActionResult("Goodbye.", should_exit=True)
            if command.action == "unknown":
                return ActionResult("I don't understand that command.")
            if command.action == "website":
                return self._open_website(command.target)
            if command.action == "search":
                return self._search_google(command.target)
            if command.action == "music":
                return self._play_music(command.target)
            if command.action == "app":
                return self._open_app(command.target)
            if command.action == "windows_app":
                return self._open_windows_app(command.target)
            if command.action == "project":
                return self._open_project(command.target)
            if command.action == "screenshot":
                return self._take_screenshot()
            if command.action == "lock":
                return self._lock_computer()
        except Exception as error:
            print(f"Action failed: {error}")
            return ActionResult("That action could not be completed.")
        return ActionResult("I don't understand that command.")

    def _open_website(self, name: str) -> ActionResult:
        url = self.WEBSITES.get(name)
        if not url:
            return ActionResult("I don't understand that command.")
        if webbrowser.open(url, new=2):
            return ActionResult(f"Opening {self.WEBSITE_LABELS[name]}.")
        return ActionResult("I couldn't open a web browser.")

    def _search_google(self, query: str) -> ActionResult:
        url = f"https://www.google.com/search?q={quote_plus(query)}"
        if webbrowser.open(url, new=2):
            return ActionResult("Searching Google.")
        return ActionResult("I couldn't open a web browser.")

    def _play_music(self, query: str) -> ActionResult:
        if query:
            url = f"{self.YOUTUBE_URL}results?search_query={quote_plus(query)}"
            message = f"Searching YouTube for {query}."
        else:
            url = f"{self.YOUTUBE_URL}results?search_query=music"
            message = "Searching YouTube for music."
        if webbrowser.open(url, new=2):
            return ActionResult(message)
        return ActionResult("I couldn't open YouTube.")

    def _open_app(self, name: str) -> ActionResult:
        candidates = config.APP_EXECUTABLE_CANDIDATES.get(name, ())
        executable = next((path for path in candidates if path.is_file()), None)
        if executable is None:
            path_names = {
                "chrome": ("chrome.exe", "chrome"),
                "vs code": ("code.exe", "code"),
                "whatsapp": ("WhatsApp.exe", "whatsapp"),
            }.get(name, ())
            executable_name = next((shutil.which(item) for item in path_names if shutil.which(item)), None)
            executable = Path(executable_name) if executable_name else None

        if executable is not None:
            subprocess.Popen([str(executable)], shell=False)
            return ActionResult(f"Opening {self.APP_LABELS[name]}.")

        if name == "whatsapp":
            if webbrowser.open("https://web.whatsapp.com/", new=2):
                return ActionResult("WhatsApp desktop wasn't found. Opening WhatsApp Web.")
            return ActionResult("I couldn't find WhatsApp or open a web browser.")
        label = "VS Code" if name == "vs code" else name.title()
        return ActionResult(f"{label} was not found on this computer.")

    def _open_windows_app(self, name: str) -> ActionResult:
        executable = self.WINDOWS_COMMANDS.get(name)
        if not executable:
            return ActionResult("I don't understand that command.")
        subprocess.Popen([executable], shell=False)
        labels = {"calculator": "Calculator", "notepad": "Notepad", "file explorer": "File Explorer"}
        return ActionResult(f"Opening {labels[name]}.")

    def _open_project(self, name: str) -> ActionResult:
        project_path = config.PROJECT_PATHS.get(name)
        if not project_path:
            return ActionResult(f"No folder is configured for {name.title()}.")
        path = Path(project_path).expanduser()
        if not path.is_dir():
            return ActionResult(f"The configured folder for {name.title()} does not exist.")
        subprocess.Popen(["explorer.exe", str(path)], shell=False)
        return ActionResult(f"Opening {name.title()} folder.")

    def _take_screenshot(self) -> ActionResult:
        from PIL import ImageGrab

        config.SCREENSHOT_DIRECTORY.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destination = config.SCREENSHOT_DIRECTORY / f"screenshot_{timestamp}.png"
        ImageGrab.grab(all_screens=True).save(destination)
        print(f"Screenshot saved to {destination}")
        return ActionResult("Screenshot saved.")

    @staticmethod
    def _lock_computer() -> ActionResult:
        if os.name != "nt":
            return ActionResult("Locking the computer is only supported on Windows.")
        if ctypes.windll.user32.LockWorkStation():
            return ActionResult("Locking your computer.")
        return ActionResult("I couldn't lock the computer.")
