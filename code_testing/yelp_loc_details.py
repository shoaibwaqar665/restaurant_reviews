import subprocess
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from myapp.dbOperations import select_name_from_trip_restaurants_details
from yelp_clean import yelp_loc_clean
# getting the slug from the trip table
query = "shakey's pizza parlor"

location_names = select_name_from_trip_restaurants_details(query)
print(f"Location names: {location_names}")
res_slug = query.replace("'", "")

def execute_bash_script(restaurant_slug):
    # Define the bash script file path
    bash_script = './run_curl.sh'

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
restaurant_slug = 'shakeys-pizza-parlor-burbank'

for location in location_names:
    restaurant_slug = res_slug+"-"+location.replace(" ", "-").lower()
    restaurant_slug = restaurant_slug.replace(" ", "-")
    print(f"Executing script for restaurant slug: {restaurant_slug}")
    execute_bash_script(restaurant_slug)
    yelp_loc_clean(restaurant_slug+".txt", restaurant_slug+".json", query, location)
    
    # Execute the bash script with the restaurant slug

# wait for the script to finish