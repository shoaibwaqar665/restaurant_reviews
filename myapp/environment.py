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

env = {
    'current': os.getenv("Enviornment")
}