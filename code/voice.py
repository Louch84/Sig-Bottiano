#!/usr/bin/env python3
"""Voice - Text to Speech"""
import os

def speak(text):
    """Speak text using Mac TTS"""
    # Clean text for command line
    text = text.replace('"', '\\"')
    os.system(f'say -v Samantha "{text}"')

def speak_async(text):
    """Speak in background"""
    text = text.replace('"', '\\"')
    os.system(f'say -v Samantha "{text}" &')

if __name__ == "__main__":
    speak("Hey, this is Sig Botti. Running.")
