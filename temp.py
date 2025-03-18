import requests
import json
import time
import re

def parse_cookies(cookie_string):
    """Parse cookie string into a dictionary"""
    cookie_dict = {}
    for cookie in cookie_string.split('; '):
        if '=' in cookie:
            name, value = cookie.split('=', 1)
            cookie_dict[name] = value
    return cookie_dict

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
            restaurants = extract_restaurant_data(response_data)
            
            if restaurants:
                # Save only the extracted data to a file
                filename = "restaurants.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(restaurants, f, indent=4, ensure_ascii=False)
                
                print(f"Extracted restaurant data saved to {filename}")
                
                # Optional: Also save the first restaurant ID to a separate file
                # first_loc_id = str(restaurants[0]["locationId"]) if restaurants else "unknown"
                filename_loc = f"unknown.json"
                with open(filename_loc, 'w', encoding='utf-8') as f:
                    json.dump(restaurants, f, indent=4, ensure_ascii=False)
                
                print(f"Data also saved to {filename_loc}")
                # return first_loc_id
            else:
                print("No restaurant data found in the response")
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error sending request: {str(e)}")

if __name__ == "__main__":
    # You can pass a different query as an argument
    import sys
    query = "shakey's pizza parlor"
    if len(sys.argv) > 1:
        query = sys.argv[1]
    
    send_request_location_data(query)
