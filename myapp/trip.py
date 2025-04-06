from concurrent.futures import ThreadPoolExecutor
import requests
import json
import time
import json
import requests
import re
from typing import Dict
from ninja_extra import api_controller, http_post, NinjaExtraAPI
from myapp.schema import TripAdvisorQuery
import base64
from googletrans import Translator
from myapp.dbOperations import InsertRestaurantDetailsForTripadvisor, InsertRestaurantReviewsForTripAdvisor
import sys


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

######################### location data extraction ###############################
def extract_restaurant_data(response_data):
    """Extract location ID and location name from the response data"""
    restaurant_data = []
    try:
        if response_data and len(response_data) > 0:
            # First check the resolved items section
            resolved_items = response_data[0].get("data", {}).get("SERP_getResultSections", {}).get("clusters", [])
            
            for cluster in resolved_items:
                sections = cluster.get("sections", [])
                for section in sections:
                    if section.get("__typename") in ["SERP_ResolvedItemsSection", "SERP_PagedSearchResultsSections"]:
                        # Handle the PagedSearchResultsSections differently
                        if section.get("__typename") == "SERP_PagedSearchResultsSections":
                            for subsection in section.get("sections", []):
                                for result in subsection.get("results", []):
                                    if "locationId" in result:
                                        loc_id = result.get("locationId")
                                        loc_name = result.get("details", {}).get("locationV2", {}).get("names", {}).get("longOnlyHierarchyTypeaheadV2", "")
                                        restaurant_data.append({
                                            "locationId": loc_id,
                                            "locationName": loc_name
                                        })
                                    
                        # Handle ResolvedItemsSection
                        else:
                            for result in section.get("results", []):
                                if "locationId" in result:
                                    loc_id = result.get("locationId")
                                    loc_name = result.get("details", {}).get("locationV2", {}).get("names", {}).get("longOnlyHierarchyTypeaheadV2", "")
                                    restaurant_data.append({
                                        "locationId": loc_id,
                                        "locationName": loc_name
                                    })
    except Exception as e:
        print(f"Error extracting restaurant data: {str(e)}")
    
    return restaurant_data

def send_request_location_data(query="shakey's pizza parlor"):
    # Read cookies from cookies.txt
    try:
        with open('cookies.txt', 'r') as f:
            cookie_string = f.read()
        cookies = parse_cookies(cookie_string)
    except Exception as e:
        print(f"Error reading cookies: {str(e)}")
        return
    
    url = "https://www.tripadvisor.com/data/graphql/ids"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json"
    }
    
    # Current timestamp
    timestamp = int(time.time() * 1000)
    
    # Construct the payload
    payload = [
        {
            "variables": {
                "request": {
                    "additionalFields": [
                        "SNIPPET",
                        "MENTION_COUNT"
                    ],
                    "filters": {
                        "dataTypes": [
                            "LOCATION"
                        ],
                        "locationTypes": [
                            "GEO",
                            "ACCOMMODATION",
                            "AIRLINE",
                            "ATTRACTION",
                            "ATTRACTION_PRODUCT",
                            "EATERY",
                            "NEIGHBORHOOD",
                            "FLIGHT",
                            "VACATION_RENTAL"
                        ]
                    },
                    "geoId": 29092,
                    "includeTopInSearch": True,
                    "limit": 30,
                    "locale": "en-US",
                    "query": query,
                    "userContext": {
                        "coordinates": {
                            "latitude": 31.408397,
                            "longitude": 73.103523
                        }
                    }
                }
            },
            "extensions": {
                "preRegisteredQueryId": "24076282f3106d7f"
            }
        },
        {
            "variables": {
                "request": {
                    "clientRequestTimestampMs": timestamp,
                    "request": [
                        {
                            "pageUid": "aef848f9-c1a8-4817-80e5-5f0bc44acf5d",
                            "userId": None,
                            "sessionId": "1C1E9FC37C6749EDB7A7939DE28144FF",
                            "page": "Search",
                            "userAgent": "DESKTOP",
                            "eventTimestampMs": timestamp,
                            "team": "Other",
                            "itemType": "Currency_Dropdown",
                            "itemName": "Currency_DropdownImp",
                            "customData": "{\"defaultCurrency\":\"USD\"}"
                        }
                    ]
                }
            },
            "extensions": {
                "preRegisteredQueryId": "b682df01eec3e82a"
            }
        },
        {
            "variables": {
                "request": {
                    "clientRequestTimestampMs": timestamp,
                    "request": [
                        {
                            "pageUid": "aef848f9-c1a8-4817-80e5-5f0bc44acf5d",
                            "userId": None,
                            "sessionId": "1C1E9FC37C6749EDB7A7939DE28144FF",
                            "page": "Search",
                            "userAgent": "DESKTOP",
                            "eventTimestampMs": timestamp,
                            "team": "Other",
                            "itemType": "POS_Dropdown",
                            "itemName": "POS_DropdownImp",
                            "customData": "{\"defaultPos\":\"en-US\"}"
                        }
                    ]
                }
            },
            "extensions": {
                "preRegisteredQueryId": "b682df01eec3e82a"
            }
        }
    ]
    
    # Send the request
    try:
        print(f"Sending request for query: {query}")
        response = requests.post(url, headers=headers, cookies=cookies, json=payload)
        
        if response.status_code == 200:
            response_data = response.json()
            restaurants_data = extract_restaurant_data(response_data)
            return restaurants_data
            
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(response.text)
            return []
    except Exception as e:
        print(f"Error sending request: {str(e)}")
        return []

############################location data extraction end ############################

############################# review data extraction #################################
def send_request_for_reviews(location_id, location_name, query):
    
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
    
    # Clean location name for filename
    safe_location_name = location_name.replace(" ", "_")
    safe_location_name = safe_location_name.replace(",", "_")
    
    # Check if file already exists, and load existing data if it does
    filename = f"{location_id}_{safe_location_name}_{query}.json"
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            # Load existing reviews into our dictionary using id as key
            for review in existing_data.get("reviews", []):
                if 'id' in review:
                    all_reviews[str(review['id'])] = review
            restaurant_info = existing_data.get("restaurant", {})
            location_info = existing_data.get("location", {})
            print(f"Loaded {len(all_reviews)} existing reviews from {filename}")
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"No existing file found or invalid JSON. Starting fresh collection for {location_id}")
    
    # Fetch reviews in batches until we've retrieved all of them
    while True:
        print(f"Fetching reviews for location {location_id} - Offset: {offset}, Batch size: {batch_size}")
        
        # Construct the payload for this batch
        
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
            # Send the request with proper JSON serialization
            response = requests.post(
                url, 
                headers=headers, 
                cookies=cookies, 
                json=payload  # Use json parameter for automatic serialization
            )
            
            if response.status_code != 200:
                print(f"Error fetching reviews: Status code {response.status_code}")
                print(f"Response: {response.text[:200]}...")  # Print first 200 chars of response
                break
            
            # Parse the response
            try:
                response_data = response.json()
                
                # Add diagnostic logging for the specific location ID
                
                
                print(f"Response has {len(response_data)} items")
                if len(response_data) > 0:
                    print(f"First item keys: {list(response_data[0].keys() if isinstance(response_data[0], dict) else [])}")
                    data_obj = response_data[0].get('data', {})
                    print(f"Data keys: {list(data_obj.keys() if isinstance(data_obj, dict) else [])}")
                    
                    locations = data_obj.get('locations', [])
                    print(f"Locations length: {len(locations) if locations else 0}")
                    if locations and len(locations) > 0:
                        first_loc = locations[0]
                        print(f"First location keys: {list(first_loc.keys() if isinstance(first_loc, dict) else [])}")
                        if 'reviewListPage' in first_loc:
                            review_page = first_loc.get('reviewListPage', {})
                            print(f"ReviewListPage keys: {list(review_page.keys() if isinstance(review_page, dict) else [])}")
                            print(f"Total count: {review_page.get('totalCount', 'N/A')}")
                            reviews = review_page.get('reviews', [])
                            print(f"Reviews length: {len(reviews) if reviews else 0}")
                        else:
                            print("No reviewListPage found in first location")
                    else:
                        print("No locations found in data object")
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON response")
                print(f"Response text: {response.text[:200]}...")  # Print first 200 chars
                break
                
            # Validate response structure
            if not response_data or not isinstance(response_data, list) or len(response_data) == 0:
                print(f"Error: Invalid response data format: {response_data}")
                break
            
            # Extract restaurant info with additional details (only once)
            if restaurant_info is None and len(response_data) > 1:
                try:
                    restaurant_section = response_data[1].get("data", {})
                    restaurants_key = None
                    
                    # Try to find the restaurant data using common keys
                    for key in restaurant_section.keys():
                        if "Restaurant" in key and isinstance(restaurant_section[key], dict) and "restaurants" in restaurant_section[key]:
                            restaurants_key = key
                            break
                    
                    if restaurants_key:
                        restaurants = restaurant_section[restaurants_key].get("restaurants", [])
                        if restaurants and len(restaurants) > 0:
                            restaurant_data = restaurants[0]
                            
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
                                "restaurant_url": restaurant_url,
                                "restaurant_decoded_url": decoded_restaurant_url,
                                "dining_options": dining_options,
                                "cuisines": cuisines, 
                                "meal_types": meal_types,
                                "menu": menu_info
                            }
                        else:
                            print(f"No restaurant data found for location {location_id}")
                    else:
                        print(f"No restaurant section found in response for location {location_id}")
                except Exception as resto_error:
                    print(f"Error extracting restaurant data: {str(resto_error)}")
                    
            # Extract location info with additional details (only once)
            if location_info is None and len(response_data) > 1:
                try:
                    location_section = response_data[1].get("data", {})
                    location_data = None
                    
                    # Try to find location data in different possible keys
                    if "locations" in location_section and location_section["locations"]:
                        location_data = location_section["locations"][0]
                    elif "location" in location_section:
                        location_data = location_section["location"]
                    
                    if location_data:
                        # Extract first location data from first response for additional details
                        first_location = None
                        if len(response_data) > 0:
                            first_location = response_data[0].get("data", {}).get("locations", [{}])[0]
                        
                        # Extract thumbnail with custom size
                        thumbnail = None
                        if "thumbnail" in location_data and location_data["thumbnail"] is not None and "photoSizeDynamic" in location_data["thumbnail"]:
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
                            "placeType": first_location.get("placeType", "") if first_location else "",
                            "url": first_location.get("url", "") if first_location else "",
                            "topicCount": first_location.get("topicCount", 0) if first_location else 0,
                        }
                        
                        # Extract review summary from the first location data (matching new.json structure)
                        review_summary = None
                        if first_location and "reviewSummary" in first_location:
                            summary_data = first_location["reviewSummary"]
                            if summary_data is not None:  # Add check to ensure summary_data is not None
                                review_summary = {
                                    "alertStatusCount": summary_data.get("alertStatusCount", 0),
                                    "rating": summary_data.get("rating"),
                                    "count": summary_data.get("count")
                                }
                            else:
                                review_summary = {
                                    "alertStatusCount": 0,
                                    "rating": None,
                                    "count": 0
                                }
                        
                        # Add review summary to location details
                        location_details["reviewSummary"] = review_summary
                        
                        # Extract review aggregations (including language counts)
                        review_aggregations = None
                        if first_location and "reviewAggregations" in first_location:
                            agg_data = first_location["reviewAggregations"]
                            if agg_data is not None:  # Add check to ensure agg_data is not None
                                review_aggregations = {
                                    "ratingCounts": agg_data.get("ratingCounts", []),
                                    "languageCounts": agg_data.get("languageCounts", {})
                                }
                            else:
                                review_aggregations = {
                                    "ratingCounts": [],
                                    "languageCounts": {}
                                }
                        
                        # Add review aggregations to location details
                        location_details["reviewAggregations"] = review_aggregations
                        
                        # Process potentially problematic fields
                        try:
                            parent_info = {}
                            if "parent" in location_data and location_data["parent"] is not None:
                                parent_data = location_data["parent"]
                                parent_info = {
                                    "locationId": parent_data.get("locationId") if isinstance(parent_data, dict) else None,
                                    "localizedName": parent_data.get("localizedName", "") if isinstance(parent_data, dict) else ""
                                }
                                
                            neighborhoods = []
                            if "neighborhoods" in location_data and location_data["neighborhoods"] is not None:
                                neighborhoods_data = location_data["neighborhoods"]
                                if isinstance(neighborhoods_data, list):
                                    for neighborhood in neighborhoods_data:
                                        if isinstance(neighborhood, dict) and "name" in neighborhood:
                                            neighborhoods.append({"name": neighborhood["name"]})
                                
                            # Add additional location info
                            location_info = {
                                **location_details,
                                "localizedStreetAddress": location_data.get("localizedStreetAddress", ""),
                                "isoCountryCode": location_data.get("isoCountryCode", ""),
                                "parent": parent_info,
                                "email": location_data.get("email", ""),
                                "thumbnail": thumbnail,
                                "neighborhoods": neighborhoods
                            }
                        except Exception as inner_error:
                            print(f"Error processing special fields: {str(inner_error)}")
                            # Create a basic location_info if inner processing fails
                            location_info = {
                                **location_details,
                                "localizedStreetAddress": "",
                                "isoCountryCode": "",
                                "parent": {},
                                "email": "",
                                "thumbnail": thumbnail
                            }
                    else:
                        print(f"No location data found in response for {location_id}")
                except Exception as loc_error:
                    print(f"Error extracting location data: {str(loc_error)}")
                    # Create minimal location info to avoid further errors
                    if not location_info:
                        location_info = {
                            "locationId": location_id,
                            "name": safe_location_name.replace("_", " ")
                        }
            
            # Extract reviews and determine total count for pagination
            if response_data and len(response_data) > 0:
                location_data = response_data[0].get("data", {}).get("locations", [])
                
                # Check if location data is valid
                if not location_data or len(location_data) == 0:
                    print(f"Warning: No locations found in response data")
                    break
                    
                # Get the first location 
                first_location = location_data[0]
                if not first_location:
                    print(f"Warning: First location is empty")
                    break
                    
                # Try to get review list page
                review_list_page = first_location.get("reviewListPage", {})
                if not review_list_page:
                    print(f"Warning: No reviewListPage found for location")
                    break
                
                # Get the total count if we don't have it yet
                if total_count is None:
                    total_count = review_list_page.get("totalCount", 0)
                    print(f"Total reviews for location {location_id}: {total_count}")
                    if total_count == 0:
                        print("Warning: totalCount is 0, there may be an issue with the response structure")
                        # Save what we have so far even if there are no reviews
                        break
                
                # Process current batch of reviews
                reviews_batch = review_list_page.get("reviews", [])
                if reviews_batch is None:
                    reviews_batch = []
                    print("Warning: reviews is None, treating as empty list")
                    
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
                        
                        # Extract additional ratings
                        additional_ratings = []
                        if "additionalRatings" in review and review["additionalRatings"]:
                            additional_ratings = review["additionalRatings"]
                        
                        # Extract avatar 
                        avatar = None
                        if "userProfile" in review and review["userProfile"] and "avatar" in review["userProfile"] and review["userProfile"]["avatar"]:
                            avatar_data = review["userProfile"]["avatar"]
                            if "photoSizeDynamic" in avatar_data and "urlTemplate" in avatar_data["photoSizeDynamic"]:
                                avatar_url = avatar_data["photoSizeDynamic"]["urlTemplate"].replace("{width}", "800").replace("{height}", "600")
                                avatar = {
                                    "id": avatar_data.get("id"),
                                    "url": avatar_url,
                                    "width": 800,
                                    "height": 600
                                }
                        
                        # Extract contribution counts
                        contribution_counts = {}
                        helpful_votes = review.get("helpfulVotes", 0)
                        if "userProfile" in review and review["userProfile"] and "contributionCounts" in review["userProfile"]:
                            contribution_counts = review["userProfile"]["contributionCounts"]
                            # Add helpfulVotes if not present in contributionCounts
                            if "helpfulVote" not in contribution_counts:
                                contribution_counts["helpfulVote"] = helpful_votes
                        else:
                            # Create minimal contribution counts with just helpful votes
                            contribution_counts = {
                                "helpfulVote": helpful_votes
                            }
                        
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
                            "is_translated": False,  # Default to not translated
                            "additionalRatings": additional_ratings,
                            "avatar": avatar,
                            "contributionCounts": contribution_counts,
                            "helpfulVotes": helpful_votes
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
    return filtered_data


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

########################################################

def FetchAndStoreRestaurantData(restaurant_query):
    """
    Fetches restaurant data from TripAdvisor and stores it in the database.
    
    This function:
    1. Uses the trip.py module's send_request_location_data function to get restaurant location data
    2. Uses send_request_for_reviews to fetch reviews for each restaurant
    3. Processes and stores the data in the database
    
    Args:
        restaurant_query (str): The restaurant name to search for
        
    Returns:
        list: List of dictionaries containing processed restaurant IDs and review counts
    """
    
    results = []
    
    try:
        # Step 1: Get restaurant location data
        print(f"Searching for restaurant: {restaurant_query}")
        locations = send_request_location_data(restaurant_query)
        original_restaurant_query = restaurant_query
        if not locations or len(locations) == 0:
            print(f"No restaurants found for query: {restaurant_query}")
            return results
            
        # Step 2: Process each restaurant
        for location in locations:
            location_id = location.get("locationId")
            location_name = location.get("locationName")
            
            if not location_id:
                print(f"Missing location ID for restaurant: {location_name}")
                continue
                
            print(f"Processing restaurant: {location_name} (ID: {location_id})")
            
            # Step 3: Fetch detailed data including reviews
            restaurant_data = send_request_for_reviews(location_id, location_name, restaurant_query)
            
            if not restaurant_data:
                print(f"Failed to get reviews for restaurant: {location_name}")
                continue
            
            
            print('orignal resturant',original_restaurant_query)
            # Step 4: Insert restaurant details
            restaurant_query = restaurant_query.replace(" ", "_")
            restaurant_query = restaurant_query.replace("'", "")
            stored_location_id = InsertRestaurantDetailsForTripadvisor(restaurant_data, original_restaurant_query.lower())
            
            if not stored_location_id:
                print(f"Failed to store restaurant details for: {location_name}")
                continue
                
            # Step 5: Insert reviews
            location = restaurant_data["location"]
            parent_location_name = ""
            if "parent" in location and location["parent"] is not None and isinstance(location["parent"], dict):
                parent_location_name = location["parent"].get("localizedName", "")
            details = restaurant_data.get("restaurant", {})
            localized_address = details.get("localizedRealtimeAddress")
            address = location.get("localizedStreetAddress", {})
            ####################################################
             # If we didn't get values from localizedRealtimeAddress, use localizedStreetAddress
            street = ""
            city = ""
            state = ""
            postal_code = ""
            if not street and address.get("street1"):
                street = address.get("street1", "")
                if address.get("street2"):
                    street += ", " + address.get("street2")
            
            if not city:
                city = address.get("city")
                
            if not state:
                state = address.get("state")
                
            if not postal_code:
                postal_code = address.get("postalCode")
            complete_address = f"{street}, {city}, {state} {postal_code}"
            ####################################################
            
            restaurant_key = (parent_location_name or '') + ' ' + (complete_address or '') + ' ' + (restaurant_query or '')
            restaurant_key = restaurant_key.replace(" ", "_")
            restaurant_key = restaurant_key.replace("'", "")
            restaurant_key = restaurant_key.replace(",", "_")
            print('restaurant key',restaurant_key)
            review_count = InsertRestaurantReviewsForTripAdvisor(restaurant_data, stored_location_id ,restaurant_key)
            
            # Record results
            results.append({
                "location_id": stored_location_id,
                "name": location_name,
                "reviews_inserted": review_count
            })
            
            print(f"Successfully processed restaurant: {location_name} - Inserted {review_count} reviews")
    
    except Exception as e:
        import traceback
        print(f"Error in FetchAndStoreRestaurantData: {str(e)}", file=sys.stderr)
        error_line = traceback.extract_tb(sys.exc_info()[2])[-1].lineno
        print(f"Error occurred at line: {error_line}", file=sys.stderr)
        print(f"Error type: {type(e).__name__}", file=sys.stderr)
        print(f"Full traceback:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
    
    return results


########################################################


@api_controller("", tags=["TripAdvisor"])
class TripAdvisorController:
    
    
    @http_post('/restaurant_details', response={200: Dict, 400: Dict})
    def restaurant_details(self,request, data: TripAdvisorQuery):
        """Return restaurant details for a specific ID"""
        try:
           query = data.query
           print(query)
           executor = ThreadPoolExecutor()
           future = executor.submit(FetchAndStoreRestaurantData,query )
           return 200, {
               "message": "Success",
           }
        except (FileNotFoundError, json.JSONDecodeError):
            return {"error": "Restaurant not found"}
    

# Register controllers
api.register_controllers(TripAdvisorController)
