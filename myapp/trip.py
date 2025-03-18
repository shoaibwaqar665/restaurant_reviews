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
import base64
from googletrans import Translator

# Initialize the Ninja API
api = NinjaExtraAPI(urls_namespace='Tripadvisor')

# Initialize translator
try:
    translator = Translator(service_urls=[
        'translate.google.com',
        'translate.google.co.jp',  # Japanese Google Translate
    ])
except Exception as e:
    print(f"Error initializing translator: {str(e)}")
    translator = Translator()  # Fallback to default

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
                    menu_url = menu_data.get("menu_url", "")
                    decoded_menu_url = decode_and_clean_url(menu_url) if menu_url else ""
                    menu_info = {
                        "has_provider": menu_data.get("has_provider", False),
                        "menu_url": menu_url,
                        "decoded_menu_url": decoded_menu_url
                    }
                
                # Get and decode restaurant URL
                restaurant_url = restaurant_data.get("url", "")
                decoded_restaurant_url = decode_and_clean_url(restaurant_url) if restaurant_url else ""
                
                restaurant_info = {
                    "name": restaurant_data.get("name"),
                    "description": restaurant_data.get("description"),
                    "telephone": restaurant_data.get("telephone"),
                    "localizedRealtimeAddress": restaurant_data.get("localizedRealtimeAddress"),
                    "schedule": restaurant_data.get("open_hours", {}).get("schedule"),
                    "url": restaurant_url,
                    "decoded_url": decoded_restaurant_url,
                    "dining_options": dining_options,
                    "cuisines": cuisines, 
                    "meal_types": meal_types,
                    "menu": menu_info
                }
            
            # Extract location info with additional details (only once)
            if location_info is None and len(response_data) > 1:
                location_data = response_data[1].get("data", {}).get("locations", [{}])[0]
                
                # Extract first location data from first response for additional details
                first_location = None
                if len(response_data) > 0:
                    first_location = response_data[0].get("data", {}).get("locations", [{}])[0]
                
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
                
                # Get basic location details
                location_details = {
                    "locationId": location_data.get("locationId"),
                    "name": location_data.get("name", ""),
                    "placeType": first_location.get("placeType", ""),
                    "url": first_location.get("url", ""),
                    "topicCount": first_location.get("topicCount", 0),
                }
                
                # Extract review summary from the first location data (matching new.json structure)
                review_summary = None
                if first_location and "reviewSummary" in first_location:
                    review_summary = {
                        "alertStatusCount": first_location["reviewSummary"].get("alertStatusCount", 0),
                        "rating": first_location["reviewSummary"].get("rating"),
                        "count": first_location["reviewSummary"].get("count")
                    }
                
                # Add review summary to location details
                location_details["reviewSummary"] = review_summary
                
                # Extract review aggregations (including language counts)
                review_aggregations = None
                if first_location and "reviewAggregations" in first_location:
                    agg_data = first_location["reviewAggregations"]
                    review_aggregations = {
                        "ratingCounts": agg_data.get("ratingCounts", []),
                        "languageCounts": agg_data.get("languageCounts", {})
                    }
                
                # Add review aggregations to location details
                location_details["reviewAggregations"] = review_aggregations
                
                # Add additional location info
                location_info = {
                    **location_details,
                    "localizedStreetAddress": location_data.get("localizedStreetAddress"),
                    "isoCountryCode": location_data.get("isoCountryCode"),
                    "parent": location_data.get("parent"),
                    "email": location_data.get("email"),
                    "thumbnail": thumbnail,
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
                        review_language = review.get("language", "en")
                        review_title = review.get("title", "")
                        
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
                        
                        # Prepare the review data structure
                        review_data = {
                            "userId": review.get("userId"),
                            "id": review_id,
                            "text": review_text,
                            "locationId": review.get("locationId"),
                            "title": review_title,
                            "rating": review.get("rating"),
                            "publishedDate": review.get("publishedDate"),
                            "username": review.get("username"),
                            "photos": photos,
                            "language": review_language,
                            "is_translated": False  # Default to not translated
                        }
                        
                        # Translate review if not in English
                        if review_language and review_language != "en":
                            try:
                                # Create a translation object within the review data
                                translation = {
                                    "language": "en"  # Target language
                                }
                                
                                # Translate text
                                if review_text:
                                    translated_text = translate_text(review_text, source_lang=review_language, dest_lang='en')
                                    if translated_text and translated_text != review_text:
                                        translation["text"] = translated_text
                                
                                # Translate title if available
                                if review_title:
                                    print(f"Attempting to translate title: '{review_title}' from {review_language}")
                                    try:
                                        translated_title = translate_text(review_title, source_lang=review_language, dest_lang='en')
                                        print(f"Title translation result: '{translated_title}'")
                                        if translated_title and translated_title != review_title:
                                            translation["title"] = translated_title
                                            print(f"Added title translation for review {review_id}")
                                    except Exception as e:
                                        print(f"Error translating title for review {review_id}: {str(e)}")
                                else:
                                    print(f"No title to translate for review {review_id}")
                                
                                # Add the translation to the review data if we have any translated content
                                if "text" in translation or "title" in translation:
                                    review_data["translation"] = translation
                                    review_data["is_translated"] = True
                                    print(f"Translated review {review_id} from {review_language} to English")
                                    
                            except Exception as e:
                                print(f"Error translating review {review_id}: {str(e)}")
                        
                        all_reviews[review_id] = review_data
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

def decode_and_clean_url(encoded_url):
    if not encoded_url:
        return ""
        
    try:
        # Decode Base64
        decoded_bytes = base64.b64decode(encoded_url)
        decoded_str = decoded_bytes.decode("utf-8")

        # Remove redundant prefix (e.g., "5zh_" or "dEp_") using regex
        cleaned_url = re.sub(r'^[a-zA-Z0-9]+_', '', decoded_str)

        # Remove everything after the last "/"
        cleaned_url = re.sub(r'/[^/]+/?$', '/', cleaned_url)

        return cleaned_url
    except Exception as e:
        print(f"Error decoding URL {encoded_url}: {str(e)}")
        return encoded_url

def translate_text(text, source_lang='auto', dest_lang='en'):
    """Translate text from source language to destination language."""
    if not text:
        print("No text to translate")
        return text
        
    if source_lang == dest_lang:
        print(f"Source language {source_lang} is the same as destination language, skipping translation")
        return text
    
    # Special handling for Japanese text
    if source_lang == 'ja' or (source_lang == 'auto' and any(ord(c) > 0x3000 for c in text)):
        print("Detected Japanese text, using special handling")
        try:
            # Try using a Japanese-specific service URL
            temp_translator = Translator(service_urls=['translate.google.co.jp'])
            translation = temp_translator.translate(text, dest=dest_lang)
            if translation and hasattr(translation, 'text') and translation.text:
                result = translation.text
                print(f"Japanese translation result: '{result[:50]}{'...' if len(result) > 50 else ''}'")
                return result
        except Exception as jp_error:
            print(f"Japanese-specific translation failed: {str(jp_error)}")
            
        # Fallback: Try direct request to Google Translate API
        try:
            print("Trying direct request method for Japanese text")
            session = requests.Session()
            session.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                "client": "gtx",
                "sl": "ja",
                "tl": "en",
                "dt": "t",
                "q": text
            }
            response = session.get(url, params=params)
            if response.status_code == 200:
                json_data = response.json()
                if json_data and len(json_data) > 0 and len(json_data[0]) > 0:
                    result = ''.join([t[0] for t in json_data[0] if t])
                    print(f"Direct API translation result: '{result[:50]}{'...' if len(result) > 50 else ''}'")
                    return result
        except Exception as direct_api_error:
            print(f"Direct API translation failed: {str(direct_api_error)}")
    
    # Try multiple methods to handle different translation issues
    try:
        print(f"Translating from {source_lang} to {dest_lang}: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
        # Method 1: Direct translation with specified language
        try:
            translation = translator.translate(text, src=source_lang, dest=dest_lang)
            if translation and hasattr(translation, 'text') and translation.text:
                result = translation.text
                print(f"Translation result: '{result[:50]}{'...' if len(result) > 50 else ''}'")
                return result
            else:
                print("Translation returned None or invalid response")
        except Exception as e:
            print(f"First translation attempt failed: {str(e)}")
        
        # Method 2: Try with 'auto' language detection
        try:
            print("Trying with auto language detection")
            translation = translator.translate(text, src='auto', dest=dest_lang)
            if translation and hasattr(translation, 'text') and translation.text:
                result = translation.text
                print(f"Auto detection translation result: '{result[:50]}{'...' if len(result) > 50 else ''}'")
                return result
            else:
                print("Auto detection translation returned None or invalid response")
        except Exception as e:
            print(f"Auto detection translation failed: {str(e)}")
            
        # Method 3: Try creating a new translator instance (sometimes helps)
        try:
            print("Trying with new translator instance")
            new_translator = Translator()
            translation = new_translator.translate(text, dest=dest_lang)
            if translation and hasattr(translation, 'text') and translation.text:
                result = translation.text
                print(f"New translator instance result: '{result[:50]}{'...' if len(result) > 50 else ''}'")
                return result
            else:
                print("New translator instance returned None or invalid response")
        except Exception as e:
            print(f"New translator instance failed: {str(e)}")
            
        # If everything fails, return original text
        print("All translation methods failed, returning original text")
        return text
            
    except Exception as main_error:
        print(f"Main translation error: {str(main_error)}")
        return text  # Return original text if all translation attempts fail

def translate_existing_reviews(location_id):
    """Translate any non-English reviews in an existing JSON file."""
    filename = f"{location_id}.json"
    
    try:
        # Load existing data
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        reviews = data.get("reviews", [])
        total_reviews = len(reviews)
        translated_count = 0
        
        print(f"Processing translations for {total_reviews} reviews in {filename}")
        
        for i, review in enumerate(reviews):
            review_id = review.get("id")
            language = review.get("language")
            
            # Skip English reviews and already translated reviews
            if not language or language == "en" or review.get("is_translated", False):
                continue
                
            # Get review text and title
            review_text = review.get("text", "")
            review_title = review.get("title", "")
            
            # Create translation object
            translation = {
                "language": "en"
            }
            
            # Translate text if available
            if review_text:
                try:
                    translated_text = translate_text(review_text, source_lang=language, dest_lang='en')
                    if translated_text and translated_text != review_text:
                        translation["text"] = translated_text
                except Exception as e:
                    print(f"Error translating text for review {review_id}: {str(e)}")
            
            # Translate title if available
            if review_title:
                print(f"Attempting to translate title: '{review_title}' from {language}")
                try:
                    translated_title = translate_text(review_title, source_lang=language, dest_lang='en')
                    print(f"Title translation result: '{translated_title}'")
                    if translated_title and translated_title != review_title:
                        translation["title"] = translated_title
                        print(f"Added title translation for review {review_id}")
                except Exception as e:
                    print(f"Error translating title for review {review_id}: {str(e)}")
            
            # Add translation to review if we have any translated content
            if "text" in translation or "title" in translation:
                review["translation"] = translation
                review["is_translated"] = True
                translated_count += 1
                print(f"[{i+1}/{total_reviews}] Translated review {review_id} from {language}")
            
            # Add a brief delay to avoid API rate limits
            if i % 5 == 0 and i > 0:
                time.sleep(1)
        
        # Save updated data
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print(f"Translation complete. Added translations for {translated_count} reviews.")
        return True
    
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error processing file {filename}: {str(e)}")
        return False

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
    
    @http_post('/translate/{restaurant_id}', response={200: Dict, 400: Dict})
    def translate_reviews(self, request, restaurant_id: str):
        """Translate all non-English reviews for a specific restaurant ID"""
        try:
            result = translate_existing_reviews(restaurant_id)
            if result:
                return 200, {
                    "message": f"Successfully translated reviews for restaurant {restaurant_id}",
                }
            else:
                return 400, {
                    "error": f"Failed to translate reviews for restaurant {restaurant_id}"
                }
        except Exception as e:
            return 400, {
                "error": f"Error: {str(e)}"
            }

# Register controllers
api.register_controllers(TripAdvisorController)
