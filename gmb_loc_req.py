import requests
import json

url = "https://www.google.com/search?tbm=map&authuser=0&hl=en&q=Shakey%27s%20Pizza%20Parlor%20Brea"

payload = {}
headers = {
  'accept': '*/*',
  'accept-language': 'en-US,en;q=0.9',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
}

response = requests.request("GET", url, headers=headers, data=payload)

def clean_and_parse_google_response(response_text):
    try:
        # Remove the anti-scraping prefix (first 4 characters: ")]}'")
        if response_text.startswith(")]}'"):
            response_text = response_text[4:].strip()
        
        # Convert to JSON
        data = json.loads(response_text)
        print("Successfully parsed JSON data.")
        
        # Save cleaned JSON to a file
        with open('cleaned_google_response.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print("Cleaned data saved to cleaned_google_response.json")
        
        return data
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
    except Exception as e:
        print(f"Error: {e}")

# Example: Pass the response text as a string to this function
response_text = response.text
cleaned_data = clean_and_parse_google_response(response_text)
