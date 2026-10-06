"""Entry point for the simple voice-controlled Windows assistant."""

from __future__ import annotations

import gc
import time

import speech_recognition as sr

import config
from commands import ActionExecutor, CommandProcessor


class VoiceOutput:
    """Speak short responses, with console output as a fallback."""

    def __init__(self) -> None:
        self.engine = None
        try:
            import pyttsx3

            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", config.SPEECH_RATE)
        except Exception as error:
            print(f"Voice output is unavailable: {error}")

    def say(self, message: str) -> None:
        print(f"Agent: {message}")
        if self.engine is None:
            return
        try:
            self.engine.say(message)
            self.engine.runAndWait()
        except Exception as error:
            print(f"Could not speak the response: {error}")

    def close(self) -> None:
        """Release SAPI's COM event connection before Python shuts down."""
        engine, self.engine = self.engine, None
        if engine is None:
            return

        try:
            engine.stop()
        except Exception as error:
            print(f"Could not stop voice output cleanly: {error}")

        driver = getattr(getattr(engine, "proxy", None), "_driver", None)
        connection = getattr(driver, "_advise", None)
        if connection is not None:
            try:
                connection.disconnect()
            except Exception as error:
                print(f"Could not disconnect the speech event handler: {error}")

        del connection, driver, engine
        gc.collect()


class VoiceAssistant:
    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()
        self.processor = CommandProcessor()
        self.executor = ActionExecutor()
        self.voice = VoiceOutput()

    def run(self) -> None:
        """Listen continuously, retrying if the microphone is unavailable."""
        microphone_error_reported = False
        try:
            self.voice.say("Voice assistant ready.")
            while True:
                try:
                    with sr.Microphone() as microphone:
                        microphone_error_reported = False
                        self.recognizer.adjust_for_ambient_noise(
                            microphone, duration=config.CALIBRATION_SECONDS
                        )
                        while True:
                            print("Listening...")
                            try:
                                audio = self.recognizer.listen(
                                    microphone,
                                    timeout=config.LISTEN_TIMEOUT_SECONDS,
                                    phrase_time_limit=config.PHRASE_TIME_LIMIT_SECONDS,
                                )
                            except sr.WaitTimeoutError:
                                continue

                            if not self._handle_audio(audio):
                                return
                except KeyboardInterrupt:
                    self.voice.say("Goodbye.")
                    return
                except (OSError, AttributeError, ImportError) as error:
                    print(f"Microphone is unavailable: {error}")
                    if not microphone_error_reported:
                        self.voice.say(
                            "Microphone unavailable. Connect or enable a microphone; I will keep trying."
                        )
                        microphone_error_reported = True
                    time.sleep(config.MICROPHONE_RETRY_SECONDS)
        finally:
            self.voice.close()

    def _handle_audio(self, audio: sr.AudioData) -> bool:
        """Recognize and execute one phrase. Return False when asked to exit."""
        try:
            text = self.recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            self.voice.say("I don't understand that command.")
            return True
        except sr.RequestError as error:
            print(f"Speech recognition is unavailable: {error}")
            self.voice.say("Speech recognition is unavailable. Check your internet connection.")
            return True

        print(f"You: {text}")
        command = self.processor.parse(text)
        result = self.executor.execute(command)
        self.voice.say(result.message)
        return not result.should_exit


if __name__ == "__main__":
    VoiceAssistant().run()
