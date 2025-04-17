import subprocess
import json
from myapp.dbOperations import select_name_from_trip_business_details
from myapp.yelp_location_clean import yelp_loc_clean
from concurrent.futures import ThreadPoolExecutor
from ninja_extra import api_controller, http_post, NinjaExtraAPI
yelp_api = NinjaExtraAPI(urls_namespace='Yelp')
from myapp.schema import Yelp
from typing import Dict

def execute_bash_script(restaurant_slug):
    # Define the bash script file path
    bash_script = 'myapp/run_curl.sh'

    # Run the bash script with the restaurant_slug argument
    result = subprocess.run([bash_script, restaurant_slug], capture_output=True, text=True)

    # Print the output and error (if any)
    if result.returncode == 0:
        print("Script executed successfully!")
        print("Output:", result.stdout)
    else:
        print("Error executing the script.")
        print("Error:", result.stderr)

# Pass the restaurant slug as an argument
# restaurant_slug = 'shakeys-pizza-parlor-burbank'
def FetchYelpData(query):
    location_names = select_name_from_trip_business_details(query)
    print(f"Location names: {location_names}")
    res_slug = query.replace("'", "")
    for location in location_names:
        try:
            restaurant_slug = res_slug + "-" + location.replace(" ", "-").lower()
            restaurant_slug = restaurant_slug.replace(" ", "-")

            print(f"🚀 Executing script for restaurant slug: {restaurant_slug}")

            execute_bash_script(restaurant_slug)

            input_file = restaurant_slug + ".html"
            output_file = restaurant_slug + ".json"

            yelp_loc_clean(input_file, output_file, query, location)

        except FileNotFoundError as e:
            print(f"❌ File not found for location '{location}': {e}")
        except ValueError as ve:
            print(f"⚠️ Value error for location '{location}': {ve}")
        except Exception as e:
            print(f"❌ Unexpected error occurred for location '{location}': {e}")


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
    

# Register controllers
yelp_api.register_controllers(YelpController)
