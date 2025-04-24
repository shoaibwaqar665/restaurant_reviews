import requests
import json

# Input
query = "shakey's pizza parlor"
location_name = "5105 Torrance Blvd, Torrance, 90503"
url = "https://www.google.com/search?tbm=map&authuser=0&hl=en&q=" + query + " " + location_name

# Headers
headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
}

# File name formatting
file_name = query.replace(" ", "_").replace("'", "")
new_location_name = location_name.replace(" ", "_")
input_file = f'{file_name}_{new_location_name}_google_loc_response.json'
output_file = f'{file_name}_{new_location_name}_google_loc_cleaned.json'

# Request
print("Query: ", query)
print("Location Name: ", location_name)

response = requests.get(url, headers=headers)

def clean_and_parse_google_response(response_text):
    try:
        # Remove the anti-scraping prefix (first 4 characters: ")]}'")
        if response_text.startswith(")]}'"):
            response_text = response_text[4:].strip()
        
        # Convert to JSON
        data = json.loads(response_text)
        print("Successfully parsed JSON data.")

        # Save cleaned JSON to a file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Cleaned data saved to {output_file}")
        
        return data

    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
    except Exception as e:
        print(f"Error: {e}")

# Clean and parse the response
response_text = response.text
cleaned_data = clean_and_parse_google_response(response_text)
