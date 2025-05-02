import subprocess
import json
from urllib.parse import unquote, urlparse
from myapp.dbOperations import fetch_yelp_data, select_name_from_trip_business_details
from myapp.yelp_location_clean import yelp_loc_clean
from concurrent.futures import ThreadPoolExecutor
from ninja_extra import api_controller, http_post, NinjaExtraAPI,http_get
yelp_api = NinjaExtraAPI(urls_namespace='Yelp')
from myapp.schema import Yelp
from typing import Dict
import os
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
from googlesearch import search
import re

def clean_address(address: str) -> str:
    # Pattern matches a 5-digit ZIP followed by a dash and more digits (e.g. 98058-8905)
    return re.sub(r'\b(\d{5})-\d{4}\b', r'\1', address)


 
def get_unique_yelp_urls(query, num_results=10):
    urls = list(search(query, num_results=num_results))
    yelp_urls = set()
    
    for url in urls:
        if "yelp.com/biz/" in url:
            parsed = urlparse(url)
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            yelp_urls.add(clean_url)
    
    return list(yelp_urls)


def slugify_path(restaurant_url):
    parsed = urlparse(restaurant_url)
    path = parsed.path  # e.g., "/biz/the-sheung-wan-by-ovolo-%E9%A6%99%E6%B8%AF"
    decoded_path = unquote(path)  # → "/biz/the-sheung-wan-by-ovolo-香港"
    cleaned = decoded_path.strip("/").replace("/", "-")  # → "biz-the-sheung-wan-by-ovolo-香港"
    
    if not cleaned.startswith("biz-"):
        cleaned = "biz-" + cleaned

    return f"{cleaned}.html"

def execute_bash_script(restaurant_url):
    output_filename = slugify_path(restaurant_url)

    result = subprocess.run(
        ['myapp/run_curl.sh', restaurant_url, output_filename],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("Script executed successfully!")
        print("Output:", result.stdout)
    else:
        print("Error executing the script.")
        print("Error:", result.stderr)


def FetchYelpData(query):
    print('FetchYelpData')
    location_names = select_name_from_trip_business_details(query)
    # if len(location_names) == 0:
    #     print("No restaurant name found")
    #     data_flag = FetchAndStoreRestaurantData(query)
    #     if data_flag:
    #         print('data_flag is true')
    #         location_names = select_name_from_trip_business_details(query)
    #         print('restaurant names',location_names)
    # else:
    #     print("Restaurant names found")
    print(f"Location names: {location_names}")
    
    for location in location_names:
        try:
           
            print(f"🚀 Executing script for restaurant slug: {location}")
            results = get_unique_yelp_urls(f"yelp {query.lower()} {location.lower()}")
            for result in results:
                print('working on ',result)
                execute_bash_script(result)
                slug_path = re.sub(r"^https?://(www\.)?yelp\.com/", "", result)
                # Replace remaining slashes with dashes
                restaurant_slug = slug_path.replace("/", "-")

                input_file = os.path.join(base_dir, restaurant_slug + ".html")
                print('the inputfile is ' ,input_file)
                output_file = restaurant_slug + ".json"

                yelp_loc_clean(input_file, output_file, query, location)

        except FileNotFoundError as e:
            print(f"❌ File not found for location '{location}': {e}")
        except ValueError as ve:
            print(f"⚠️ Value error for location '{location}': {ve}")
        except Exception as e:
            print(f"❌ Unexpected error occurred for location '{location}': {e}")
    print('🚀🚀🚀🚀FetchYelpData completed 🚀🚀🚀🚀')
    return True


@api_controller("", tags=["Yelp"])
class YelpController:
    
    
    @http_post('/restaurant_details', response={200: Dict, 400: Dict})
    def restaurant_details_for_yelp(self,request, data: Yelp):
        """Return restaurant details for a specific ID"""
        try:
           query = data.query
           print(query)
           executor = ThreadPoolExecutor()
           future = executor.submit(FetchYelpData,query )
           return 200, {
               "message": "Success",
           }
        except (FileNotFoundError, json.JSONDecodeError):
            return {"error": "Restaurant not found"}
        
    @http_get('/restaurant_details', response={200: Dict, 400: Dict})
    def get_restaurant_details(self,request):
        """Return restaurant details for a specific ID"""
        try:
            print("Fetching data from yelp")
            data = fetch_yelp_data()
            return 200, data
        except Exception as e:
            return 400, {"error": str(e)}

# Register controllers
yelp_api.register_controllers(YelpController)