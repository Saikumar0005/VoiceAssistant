import pyttsx3
import wikipedia
import speech_recognition as sr
import datetime
import pywhatkit
import webbrowser
import requests
import os
import subprocess
import pyautogui
import spacy
import google.generativeai as genai

engine = pyttsx3.init()
recognizer = sr.Recognizer()
nlp = spacy.load("en_core_web_sm")

# Configure Gemini API
genai.configure(api_key="GEMINI_API_KEY")

# Voice setup
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # 1->Female voice, 2-> Male voice
engine.setProperty('rate', 170)  


def speak(text):
    print(f"BROO: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("\nListening... 🎤")
        try:
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=8)
            text = recognizer.recognize_google(audio, language='en-US')
            print(f"You said: {text}")
            return text.lower()
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that. Please repeat.")
            return ""
        except sr.RequestError:
            speak("Speech recognition service is unavailable.")
            return ""

# NLP Commands

def get_intent(command):
    command = command.lower()
    doc = nlp(command)

    if any(word.lemma_ in ["play", "music", "song"] for word in doc):
        return "play_music"
    elif any(word.lemma_ in ["time", "clock"] for word in doc):
        return "time"
    elif any(word.lemma_ in ["search", "find", "google"] for word in doc):
        return "search"
    elif any(word.lemma_ in ["open", "launch", "start"] for word in doc):
        return "open_app"
    elif any(word.lemma_ in ["shutdown", "restart", "screenshot", "volume"] for word in doc):
        return "system_control"
    elif any(word.lemma_ in ["weather", "temperature"] for word in doc):
        return "weather"
    elif any(word.lemma_ in ["who", "what", "tell", "explain"] for word in doc):
        return "ask_ai"
    elif any(word.lemma_ in ["exit", "quit", "stop", "goodbye"] for word in doc):
        return "exit"
    else:
        return "unknown"

def ask_gemini(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error using Gemini API: {e}"


def system_control(command):
    if "notepad" in command:
        os.system("notepad")
        speak("Opening Notepad.")
    elif "browser" in command or "chrome" in command:
        os.system("start chrome")
        speak("Opening browser.")
    elif "screenshot" in command:
        pyautogui.screenshot("screenshot.png")
        speak("Screenshot saved.")
    elif "shutdown" in command:
        speak("Shutting down the system in 5 seconds.")
        os.system("shutdown /s /t 5")
    elif "restart" in command:
        speak("Restarting the system.")
        os.system("shutdown /r /t 5")
    elif "volume up" in command:
        for _ in range(5):
            pyautogui.press("volumeup")
        speak("Volume increased.")
    elif "volume down" in command:
        for _ in range(5):
            pyautogui.press("volumedown")
        speak("Volume decreased.")
    else:
        speak("I couldn't perform that system command.")

# Weather Information
def get_weather():
    speak("Please tell me the city name.")
    cityname = listen()
    if not cityname:
        speak("City name not detected.")
        return

    apiKey = "7040ea904442a45d6950ba584410ce59"  # Replace with your OpenWeather key
    baseURL = "http://api.openweathermap.org/data/2.5/weather?q="
    completeURL = baseURL + cityname + "&appid=" + apiKey
    response = requests.get(completeURL)
    data = response.json()

    if data["cod"] != "404":
        main = data["main"]
        temperature_celsius = round(main["temp"] - 273.15, 2)
        humidity = main["humidity"]
        weather_desc = data["weather"][0]["description"]
        weather_report = (
            f"The temperature in {cityname} is {temperature_celsius}°C, "
            f"humidity is {humidity}%, and the weather is {weather_desc}."
        )
        speak(weather_report)
    else:
        speak("City not found.")


# Normal Commands

def process_command(command):
    intent = get_intent(command)

    if intent == "play_music":
        song = command.replace("play", "").strip()
        speak(f"Playing {song} on YouTube.")
        pywhatkit.playonyt(song)

    elif intent == "time":
        time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {time}.")

    elif intent == "search":
        query = command.replace("search", "").strip()
        webbrowser.open(f"https://www.google.com/search?q={query}")
        speak(f"Here are the search results for {query}.")

    elif intent == "open_app" or intent == "system_control":
        system_control(command)

    elif intent == "weather":
        get_weather()

    elif intent == "ask_ai":
        response = ask_gemini(command)
        speak(response)

    elif intent == "exit":
        speak("Goodbye! Have a nice day.")
        return True

    else:
        speak("I'm not sure how to help with that.")
    return False


if __name__ == "__main__":
    speak("Hello! I am Jarvis 2.0, your intelligent voice assistant. How can I help you today?")
    while True:
        command = listen()
        if command:
            if process_command(command):
                break
