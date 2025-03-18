from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

Scraping = {
    "Database": os.getenv("DB_DATABASE"),
    "Username": os.getenv("DB_USERNAME"),
    "Password": os.getenv("DB_PASSWORD"),
    "Host": os.getenv("DB_HOST"),
    "Port": os.getenv("DB_PORT")
}

Omni = {
    "Database": os.getenv("OMNI_DATABASE"),
    "Username": os.getenv("OMNI_USERNAME"),
    "Password": os.getenv("OMNI_PASSWORD"),
    "Host": os.getenv("OMNI_HOST"),
    "Port": os.getenv("OMNI_PORT")
}

WebhookURL = {
    "WebhookURL": os.getenv("WEBHOOK_URL")
}

env = {
    'current': os.getenv("Enviornment")
}