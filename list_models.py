import os
from dotenv import load_dotenv
from google import genai

def main():
    load_dotenv()
    try:
        client = genai.Client()
        print("Available models supporting generateContent:")
        for m in client.models.list():
            print(f" - {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    main()
