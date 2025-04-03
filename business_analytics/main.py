import sys
import os
import json

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from myapp.dbOperations import fetch_trip_data  # Now Python can find 'myapp'

trip_data = fetch_trip_data('Inglewood_935_W_Arbor_Vitae_St__Inglewood__CA_90301_shakeys_pizza_parlor')

# Convert to JSON and save
with open("trip_data.json", "w", encoding="utf-8") as json_file:
    json.dump(trip_data, json_file, indent=4, default=str,ensure_ascii=False)

print("Data saved to trip_data.json successfully!")

# load the JSON data
with open("trip_data.json", "r", encoding="utf-8") as json_file:
    loaded_trip_data = json.load(json_file)
    print("Loaded data from trip_data.json:")
    print(loaded_trip_data)