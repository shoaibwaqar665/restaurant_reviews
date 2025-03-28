import requests
import json

from gmb_loc_clean import location_data_cleaning
from myapp.dbOperations import select_name_from_trip_restaurants_details

query = "Shakey's Pizza Parlor"
restaurant_name = select_name_from_trip_restaurants_details(query)
for name in restaurant_name:
    url = "https://www.google.com/search?tbm=map&authuser=0&hl=en&q=" + query+" "+name
    payload = {}
    headers = {
      'accept': '*/*',
      'accept-language': 'en-US,en;q=0.9',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    }
    file_name = query.replace(" ", "_")
    file_name = file_name.replace("'", "")
    input_file = f'{file_name}_{name}_google_loc_response.json'
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
            with open(input_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            print(f"Cleaned data saved to {input_file}")
            
            return data
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e}")
        except Exception as e:
            print(f"Error: {e}")
    
    # Example: Pass the response text as a string to this function
    response_text = response.text
    cleaned_data = clean_and_parse_google_response(response_text)
    output_file = f'{file_name}_{name}_google_loc_cleaned.json'
    location_data_cleaning(input_file, output_file)
