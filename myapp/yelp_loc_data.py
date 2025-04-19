import subprocess
import json
from myapp.dbOperations import fetch_yelp_data, select_name_from_trip_business_details
from myapp.yelp_location_clean import yelp_loc_clean
from concurrent.futures import ThreadPoolExecutor
from ninja_extra import api_controller, http_post, NinjaExtraAPI,http_get
yelp_api = NinjaExtraAPI(urls_namespace='Yelp')
from myapp.schema import Yelp
from typing import Dict
import os
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
import time
import nodriver as uc  
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
# def execute_bash_script(restaurant_slug):
#     # Define the bash script file path
#     bash_script = 'myapp/run_curl.sh'

#     # Run the bash script with the restaurant_slug argument
#     result = subprocess.run([bash_script, restaurant_slug], capture_output=True, text=True)

#     # Print the output and error (if any)
#     if result.returncode == 0:
#         print("Script executed successfully!")
#         print("Output:", result.stdout)
#     else:
#         print("Error executing the script.")
#         print("Error:", result.stderr)

# --------------------- nodriver ----------------------
async def extract_location_html(restaurant_slug):
    browser = await uc.start()
    url = f"https://www.yelp.com/biz/{restaurant_slug}"
    page = await browser.get(url)
    time.sleep(20)
    page_content = await page.get_content()
    browser.stop()
    return page_content
    # cleaned_data = parse_yelp_html(page_content)
# --------------------- nodriver ----------------------


# Pass the restaurant slug as an argument
# restaurant_slug = 'shakeys-pizza-parlor-burbank'
async def FetchYelpData(query):
    location_names = select_name_from_trip_business_details(query)
    print(f"Location names: {location_names}")
    res_slug = query.replace("'", "")
    for location in location_names:
        try:
            restaurant_slug = res_slug + "-" + location.replace(" ", "-").lower()
            restaurant_slug = restaurant_slug.replace(" ", "-")

            print(f"🚀 Executing script for restaurant slug: {restaurant_slug}")

            html_content = await extract_location_html(restaurant_slug)

            # input_file = input_file = os.path.join(base_dir, restaurant_slug + ".html")
            output_file = restaurant_slug + ".json"

            yelp_loc_clean(html_content, output_file, query, location)

        # except FileNotFoundError as e:
        #     print(f"❌ File not found for location '{location}': {e}")
        except ValueError as ve:
            print(f"⚠️ Value error for location '{location}': {ve}")
        except Exception as e:
            print(f"❌ Unexpected error occurred for location '{location}': {e}")

def run_async_main(query):
    return asyncio.run(FetchYelpData(query))
@api_controller("", tags=["Yelp"])
class YelpController:
    
    
    @http_post('/restaurant_details', response={200: Dict, 400: Dict})
    async def restaurant_details_for_yelp(self,request, data: Yelp):
        """Return restaurant details for a specific ID"""
        try:
           query = data.query
           print(query)
        #    executor = ThreadPoolExecutor()
        #    future = executor.submit(FetchYelpData,query )
           loop = asyncio.get_event_loop()
           executor = ThreadPoolExecutor()
           result = loop.run_in_executor(executor, run_async_main, query)  
           return 200, {
               "message": "Success",
           }
        except (json.JSONDecodeError):
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
