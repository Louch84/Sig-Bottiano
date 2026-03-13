#!/usr/bin/env python3
"""Better Voice - Using edge-tts"""
import asyncio
import edge_tts
import os

async def speak(text, voice="en-US-AriaNeural"):
    """Speak with edge-tts"""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save("temp_voice.mp3")
    os.system("afplay temp_voice.mp3")
    os.remove("temp_voice.mp3")

async def list_voices():
    """List available voices"""
    voices = await edge_tts.list_voices()
    for v in voices[:10]:
        print(f"{v['ShortName']}: {v['Name']}")

# Test
if __name__ == "__main__":
    print("Testing voice...")
    asyncio.run(speak("Hey, this is Sig Botti. Running."))
