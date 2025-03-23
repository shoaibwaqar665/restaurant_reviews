import requests
import json

url = "https://www.google.com/search?tbm=map&authuser=0&hl=en&q=Shakey%27s%20Pizza%20Parlor%20Upland"

payload = {}
headers = {
  'accept': '*/*',
  'accept-language': 'en-US,en;q=0.9',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
}

response = requests.request("GET", url, headers=headers, data=payload)
if response.headers.get('Content-Type') == 'application/json':
    print(response.json())
else:
    print("Received non-JSON response. Check the content.")
    print(response.text[:500])  # Print first 500 characters for a quick look
import json

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

# # write response content to a json file
# with open('response_maps.json', 'w', encoding='utf-8') as f:
#     f.write(response.json())


# # ########################################################
# # '''DATA CLEANING Section'''
# # ########################################################
# import json

# def load_data(json_file='cleaned_google_response.json'):
#     """Load restaurant data from JSON file"""
#     try:
#         with open(json_file, 'r', encoding='utf-8') as f:
#             return json.load(f)
#     except (FileNotFoundError, json.JSONDecodeError) as e:
#         print(f"Error: {e}")
#         return {}

# def get_basic_info(restaurant):
#     """Return basic restaurant information"""
#     if not restaurant:
#         return None

#     return {
#         'name': restaurant.get('name'),
#         'address': restaurant.get('address'),
#         'phone': restaurant.get('phone'),
#         'website': restaurant.get('website'),
#         'rating': restaurant.get('rating'),
#         'reviews': restaurant.get('reviews'),
#         'price_level': restaurant.get('price_level'),
#         'description': restaurant.get('description'),
#         'categories': restaurant.get('categories', [])
#     }

# def get_hours(restaurant):
#     """Return restaurant hours"""
#     return restaurant.get('hours', {})

# def get_features(restaurant):
#     """Return restaurant features"""
#     return restaurant.get('features', {})

# def save_to_json(data, output_file='restaurant_output.json'):
#     """Save the restaurant information to JSON file"""
#     try:
#         with open(output_file, 'w', encoding='utf-8') as f:
#             json.dump(data, f, indent=4, ensure_ascii=False)
#         print(f"Output saved to {output_file}")
#     except IOError as e:
#         print(f"Error saving to file: {e}")

# def main():
#     data = load_data()
#     restaurant = data.get('restaurant', {})

#     output_data = {
#         'basic_info': get_basic_info(restaurant),
#         'hours': get_hours(restaurant),
#         'features': get_features(restaurant)
#     }

#     save_to_json(output_data)

# if __name__ == "__main__":
#     main()
