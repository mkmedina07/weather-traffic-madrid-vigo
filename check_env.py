from dotenv import load_dotenv
import os

load_dotenv()

print("API Key:", os.getenv("OPENWEATHER_API_KEY"))