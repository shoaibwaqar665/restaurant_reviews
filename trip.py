import requests
import json
from patchright.sync_api import sync_playwright
import time
import json
from datetime import datetime
import requests
import re

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
                "limit": 15,
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
    
    # Save the response to a file named with the location ID
    filename = f"{location_id}.json"
    with open(filename, 'w') as f:
        json.dump(response.json(), f, indent=4)
    print(f"Response saved to {filename}")

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

if __name__ == "__main__":
    run()



