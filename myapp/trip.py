import requests
import json
from patchright.sync_api import sync_playwright
import time
import json
from datetime import datetime
import requests
import re
from ninja_extra import api_controller, http_get, NinjaExtraAPI

# Initialize the Ninja API
api = NinjaExtraAPI(urls_namespace='Tripadvisor')

def extract_location_id(url):
    # Extract the location ID from the URL using regex
    match = re.search(r'-d(\d+)-', url)
    if match:
        return match.group(1)
    return None

def parse_cookies(cookie_string):
    cookie_dict = {}
    for cookie in cookie_string.split('; '):
        if '=' in cookie:
            name, value = cookie.split('=', 1)
            cookie_dict[name] = value
    return cookie_dict

# read cookies from cookies.txt
with open('cookies.txt', 'r') as f:
    cookie_string = f.read()

# Parse cookies into dictionary
cookies = parse_cookies(cookie_string)

def send_request(location_id):
    url = "https://www.tripadvisor.com/data/graphql/ids"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json"
    }
    
    payload = [
        {
            "variables": {
                "locationId": int(location_id),
                "offset": 0,
                "limit": 500,
                "keywordVariant": "location_keywords_v2_llr_order_30_en",
                "language": "en",
                "userId": "",
                "filters": [],
                "prefs": {},
                "initialPrefs": {}
            },
            "extensions": {
                "preRegisteredQueryId": "aaff0337570ed0aa"
            }
        },
        {
            "variables": {
                "rssId": f"ta-{location_id}",
                "locationId": int(location_id),
                "geoId": 32655,
                "locale": "en-US",
                "currency": "USD",
                "distanceUnitHotelsAndRestaurants": "MILES",
                "distanceUnitAttractions": "MILES",
                "numTimeslots": 6
            },
            "extensions": {
                "preRegisteredQueryId": "e50473638bca81f5"
            }
        }
    ]
    
    response = requests.post(url, headers=headers, cookies=cookies, data=json.dumps(payload))
    
    print(f"Status Code for location {location_id}:", response.status_code)
    
    # Parse the response
    response_data = response.json()
    
    # Extract required data
    filtered_data = {
        "reviews": [],
        "restaurant": {},
        "location": {}
    }
    
    # Extract reviews data
    if response_data and len(response_data) > 0:
        reviews_data = response_data[0].get("data", {}).get("locations", [{}])[0].get("reviewListPage", {}).get("reviews", [])
        for review in reviews_data:
            filtered_data["reviews"].append({
                "userId": review.get("userId"),
                "id": review.get("id"),
                "text": review.get("text"),
                "locationId": review.get("locationId"),
                "title": review.get("title"),
                "rating": review.get("rating"),
                "publishedDate": review.get("publishedDate"),
                "username": review.get("username")
            })
    
    # Extract restaurant data
    if response_data and len(response_data) > 1:
        restaurant_data = response_data[1].get("data", {}).get("RestaurantPresentation_searchRestaurantsById", {}).get("restaurants", [{}])[0]
        filtered_data["restaurant"] = {
            "name": restaurant_data.get("name"),
            "description": restaurant_data.get("description"),
            "telephone": restaurant_data.get("telephone"),
            "localizedRealtimeAddress": restaurant_data.get("localizedRealtimeAddress"),
            "schedule": restaurant_data.get("open_hours", {}).get("schedule")
        }
    
    # Extract location data
    if response_data and len(response_data) > 1:
        location_data = response_data[1].get("data", {}).get("locations", [{}])[0]
        filtered_data["location"] = {
            "localizedStreetAddress": location_data.get("localizedStreetAddress"),
            "isoCountryCode": location_data.get("isoCountryCode"),
            "parent": location_data.get("parent"),
            "email": location_data.get("email")
        }
    
    # Save the filtered response to a file named with the location ID
    filename = f"{location_id}.json"
    with open(filename, 'w') as f:
        json.dump(filtered_data, f, indent=4)
    print(f"Filtered response saved to {filename}")

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Navigate to Google
            page.goto("https://www.google.com")
            
            # Wait for the search box to be visible and type the search query
            search_box = page.locator('textarea[name="q"]')
            search_box.wait_for()
            search_box.fill("shakey's pizza parlor tripadvisor usa")
            
            # Press Enter to search
            search_box.press("Enter")
            
            # Wait for search results to load
            page.wait_for_load_state("networkidle")
            
            # Find all TripAdvisor links in the search results
            tripadvisor_links = page.locator("a[href*='tripadvisor.com']")
            
            # Get all TripAdvisor URLs
            urls = tripadvisor_links.evaluate_all("elements => elements.map(el => el.href)")
            
            # Process each URL
            print("\nProcessing TripAdvisor URLs:")
            for url in urls:
                print(f"Found URL: {url}")
                location_id = extract_location_id(url)
                if location_id:
                    print(f"Extracted location ID: {location_id}")
                    send_request(location_id)
                else:
                    print("Could not extract location ID from URL")
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            raise
        finally:
            browser.close()

# if __name__ == "__main__":
#     run()



@api_controller("", tags=["TripAdvisor"])
class TripAdvisorController:
    
    @http_get('/restaurants')
    def get_restaurants(self):
        """Return a list of all restaurant IDs"""
        import glob
        json_files = glob.glob('*.json')
        restaurant_ids = [f.split('.')[0] for f in json_files if f[0].isdigit()]
        return {"restaurant_ids": restaurant_ids}
    
    @http_get('/restaurants/{restaurant_id}')
    def get_restaurant(self, restaurant_id: str):
        """Return restaurant details for a specific ID"""
        try:
            with open(f'{restaurant_id}.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"error": "Restaurant not found"}

# Register controllers
api.register_controllers(TripAdvisorController)
