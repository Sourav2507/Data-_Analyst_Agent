import os

class Settings:
    API_TITLE = "Data Analyst Agent"
    API_VERSION = "1.0.0"
    HOST = "0.0.0.0"
    PORT = int(os.getenv("PORT", 8000))
    REQUEST_TIMEOUT = 180  # seconds

settings = Settings()
