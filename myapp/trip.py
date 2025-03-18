from concurrent.futures import ThreadPoolExecutor
import requests
import json
from patchright.sync_api import sync_playwright
import time
import json
from datetime import datetime
import requests
import re
from typing import Dict
from ninja_extra import api_controller, http_get, http_post, NinjaExtraAPI
from myapp.schema import TripAdvisorQuery

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
    
    # Initial batch size for reviews
    batch_size = 15
    offset = 0
    
    # Dictionary to store all reviews and avoid duplicates
    all_reviews = {}
    restaurant_info = None
    location_info = None
    total_count = None
    
    # Check if file already exists, and load existing data if it does
    filename = f"{location_id}.json"
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            # Load existing reviews into our dictionary using id as key
            for review in existing_data.get("reviews", []):
                if 'id' in review:
                    all_reviews[str(review['id'])] = review
            restaurant_info = existing_data.get("restaurant", {})
            location_info = existing_data.get("location", {})
    except (FileNotFoundError, json.JSONDecodeError):
        pass  # File doesn't exist or is invalid, start fresh
    
    # Fetch reviews in batches until we've retrieved all of them
    while True:
        print(f"Fetching reviews for location {location_id} - Offset: {offset}, Batch size: {batch_size}")
        
        payload = [
            {
                "variables": {
                    "locationId": int(location_id),
                    "offset": offset,
                    "limit": batch_size,
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
        
        try:
            response = requests.post(url, headers=headers, cookies=cookies, data=json.dumps(payload))
            
            if response.status_code != 200:
                print(f"Error fetching reviews: Status code {response.status_code}")
                break
                
            response_data = response.json()
            
            # Debug: Save the first response for inspection
            # if offset == 0:
            #     with open(f"response_debug_{location_id}.json", 'w', encoding='utf-8') as f:
            #         json.dump(response_data, f, indent=4, ensure_ascii=False)
            #     print(f"Saved debug response to response_debug_{location_id}.json")
            
            # Extract restaurant info with additional details (only once)
            if restaurant_info is None and len(response_data) > 1:
                restaurant_data = response_data[1].get("data", {}).get("RestaurantPresentation_searchRestaurantsById", {}).get("restaurants", [{}])[0]
                
                # Extract dining options
                dining_options = []
                if "dining_options" in restaurant_data and "items" in restaurant_data["dining_options"]:
                    for item in restaurant_data["dining_options"]["items"]:
                        if "tag" in item and "localizedName" in item["tag"]:
                            dining_options.append(item["tag"]["localizedName"])
                
                # Extract cuisines
                cuisines = []
                if "cuisines" in restaurant_data and "items" in restaurant_data["cuisines"]:
                    for item in restaurant_data["cuisines"]["items"]:
                        if "tag" in item and "localizedName" in item["tag"]:
                            cuisines.append(item["tag"]["localizedName"])
                
                # Extract meal types
                meal_types = []
                if "meal_types" in restaurant_data and "items" in restaurant_data["meal_types"]:
                    for item in restaurant_data["meal_types"]["items"]:
                        if "tag" in item and "localizedName" in item["tag"]:
                            meal_types.append(item["tag"]["localizedName"])
                
                # Extract menu info
                menu_info = None
                if "menu" in restaurant_data:
                    menu_data = restaurant_data["menu"]
                    menu_info = {
                        "has_provider": menu_data.get("has_provider", False),
                        "menu_url": menu_data.get("menu_url", "")
                    }
                
                restaurant_info = {
                    "name": restaurant_data.get("name"),
                    "description": restaurant_data.get("description"),
                    "telephone": restaurant_data.get("telephone"),
                    "localizedRealtimeAddress": restaurant_data.get("localizedRealtimeAddress"),
                    "schedule": restaurant_data.get("open_hours", {}).get("schedule"),
                    "url": restaurant_data.get("url", ""),
                    "dining_options": dining_options,
                    "cuisines": cuisines, 
                    "meal_types": meal_types,
                    "menu": menu_info
                }
            
            # Extract location info with additional details (only once)
            if location_info is None and len(response_data) > 1:
                location_data = response_data[1].get("data", {}).get("locations", [{}])[0]
                
                # Extract thumbnail with custom size
                thumbnail = None
                if "thumbnail" in location_data and "photoSizeDynamic" in location_data["thumbnail"]:
                    photo_data = location_data["thumbnail"]["photoSizeDynamic"]
                    if "urlTemplate" in photo_data:
                        # Replace {width} and {height} with desired dimensions
                        thumbnail_url = photo_data["urlTemplate"].replace("{width}", "800").replace("{height}", "600")
                        thumbnail = {
                            "url": thumbnail_url,
                            "width": 800,
                            "height": 600,
                            "original_width": photo_data.get("maxWidth"),
                            "original_height": photo_data.get("maxHeight")
                        }
                
                # Extract review summary in correct format
                review_summary = None
                if "reviewSummary" in location_data:
                    review_summary = {
                        "alertStatusCount": location_data["reviewSummary"].get("alertStatusCount", 0),
                        "rating": location_data["reviewSummary"].get("rating"),
                        "count": location_data["reviewSummary"].get("count")
                    }
                
                # Extract review aggregations (including language counts)
                review_aggregations = None
                if len(response_data) > 0:
                    first_location = response_data[0].get("data", {}).get("locations", [{}])[0]
                    if "reviewAggregations" in first_location:
                        agg_data = first_location["reviewAggregations"]
                        review_aggregations = {
                            "ratingCounts": agg_data.get("ratingCounts", []),
                            "languageCounts": agg_data.get("languageCounts", {})
                        }
                
                location_info = {
                    "localizedStreetAddress": location_data.get("localizedStreetAddress"),
                    "isoCountryCode": location_data.get("isoCountryCode"),
                    "parent": location_data.get("parent"),
                    "email": location_data.get("email"),
                    "thumbnail": thumbnail,
                    "reviewSummary": review_summary,
                    "reviewAggregations": review_aggregations
                }
            
            # Extract reviews and determine total count for pagination
            if response_data and len(response_data) > 0:
                location_data = response_data[0].get("data", {}).get("locations", [{}])[0]
                review_list_page = location_data.get("reviewListPage", {})
                
                # Get the total count if we don't have it yet
                if total_count is None:
                    total_count = review_list_page.get("totalCount", 0)
                    print(f"Total reviews for location {location_id}: {total_count}")
                    if total_count == 0:
                        print("Warning: totalCount is 0, there may be an issue with the response structure")
                        break
                
                # Process current batch of reviews
                reviews_batch = review_list_page.get("reviews", [])
                new_reviews_count = 0
                
                if not reviews_batch:
                    print("Warning: No reviews found in this batch")
                    if offset == 0:
                        print("Failed to find any reviews, check the response structure")
                        break
                
                for review in reviews_batch:
                    review_id = str(review.get("id", ""))
                    if review_id and review_id not in all_reviews:
                        # Add only new reviews
                        review_text = review.get("text", "")
                        
                        # Extract review photos if available
                        photos = []
                        if "photos" in review and review["photos"]:
                            for photo in review["photos"]:
                                if "photoSizeDynamic" in photo and "urlTemplate" in photo["photoSizeDynamic"]:
                                    photo_url = photo["photoSizeDynamic"]["urlTemplate"].replace("{width}", "800").replace("{height}", "600")
                                    photos.append({
                                        "id": photo.get("id"),
                                        "url": photo_url,
                                        "width": 800,
                                        "height": 600
                                    })
                        
                        all_reviews[review_id] = {
                            "userId": review.get("userId"),
                            "id": review_id,
                            "text": review_text,
                            "locationId": review.get("locationId"),
                            "title": review.get("title"),
                            "rating": review.get("rating"),
                            "publishedDate": review.get("publishedDate"),
                            "username": review.get("username"),
                            "photos": photos,
                            "language": review.get("language")
                        }
                        new_reviews_count += 1
                
                print(f"Added {new_reviews_count} new reviews in this batch")
                
                if reviews_batch and new_reviews_count == 0:
                    print("Received reviews but all were duplicates, stopping pagination")
                    break
                
                # Increment offset for next batch
                offset += len(reviews_batch)
                
                # If we've fetched all reviews or this batch was empty, exit the loop
                if len(reviews_batch) < batch_size or offset >= total_count:
                    print(f"Reached the end of reviews at offset {offset}/{total_count}")
                    break
            else:
                print("No location data in response, stopping pagination")
                break
        except Exception as e:
            print(f"Error processing batch: {str(e)}")
            break
    
    # Prepare the final data structure
    filtered_data = {
        "reviews": list(all_reviews.values()),
        "restaurant": restaurant_info or {},
        "location": location_info or {}
    }
    
    # Save the filtered response to a file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, indent=4, ensure_ascii=False)
    
    print(f"Saved {len(all_reviews)} total reviews to {filename}")

def run_scraper(query: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Navigate to Google
            print("Navigating to Google")
            page.goto("https://www.google.com")
            
            # Wait for the search box to be visible and type the search query
            search_box = page.locator('textarea[name="q"]')
            search_box.wait_for()
            search_box.fill(f"{query} tripadvisor usa")
            
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
    
    @http_post('/restaurant_details', response={200: Dict, 400: Dict})
    def restaurant_details(self,request, data: TripAdvisorQuery):
        """Return restaurant details for a specific ID"""
        try:
           query = data.query
           print(query)
           executor = ThreadPoolExecutor()
           future = executor.submit(run_scraper,query )
           return 200, {
               "message": "Success",
           }
        except (FileNotFoundError, json.JSONDecodeError):
            return {"error": "Restaurant not found"}
    

# Register controllers
api.register_controllers(TripAdvisorController)
