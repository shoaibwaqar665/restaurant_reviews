# import requests
# import json

# url = "https://www.tripadvisor.com/data/graphql/ids"

# payload = json.dumps([
#   {
#     "variables": {
#       "locationId": 4648969,
#       "offset": 0,
#       "limit": 15,
#       "keywordVariant": "location_keywords_v2_llr_order_30_en",
#       "language": "en",
#       "userId": "",
#       "filters": [],
#       "prefs": {},
#       "initialPrefs": {}
#     },
#     "extensions": {
#       "preRegisteredQueryId": "aaff0337570ed0aa"
#     }
#   },
#   {
#     "variables": {
#       "rssId": "ta-4648969",
#       "locationId": 4648969,
#       "geoId": 32655,
#       "locale": "en-US",
#       "currency": "USD",
#       "distanceUnitHotelsAndRestaurants": "MILES",
#       "distanceUnitAttractions": "MILES",
#       "numTimeslots": 6
#     },
#     "extensions": {
#       "preRegisteredQueryId": "e50473638bca81f5"
#     }
#   }
# ])
# headers = {
#   'accept': '*/*',
#   'accept-language': 'en-US,en;q=0.9',
#   'content-type': 'application/json',
  
# }
# def parse_cookies(cookie_string):
#     cookie_dict = {}
#     for cookie in cookie_string.split('; '):
#         if '=' in cookie:
#             name, value = cookie.split('=', 1)
#             cookie_dict[name] = value
#     return cookie_dict

# # read cookies from cookies.txt
# with open('cookies.txt', 'r') as f:
#     cookie_string = f.read()

# # Parse cookies into dictionary
# cookies = parse_cookies(cookie_string)
# response = requests.request("POST", url, headers=headers,cookies=cookies, data=payload)

# # print(response.json())

# # save response to json file
# with open('test_response.json', 'w') as f:
#     json.dump(response.json(), f)


import json

# Load the complete response file
complete_response_path = "346378_El_Monte__California_complete_response.json"
with open(complete_response_path, "r", encoding="utf-8") as f:
    complete_response = json.load(f)

# Extract relevant data from the complete response
location_data = complete_response[0].get("data", {}).get("locations", [{}])[0]
review_summary = location_data.get("reviewSummary", {})
email = location_data.get("email", None)

# Load the incomplete JSON file
incomplete_file_path = "346378_El_Monte__California.json"
with open(incomplete_file_path, "r", encoding="utf-8") as f:
    incomplete_data = json.load(f)

# Update the incomplete data with missing fields
if "restaurant" in incomplete_data:
    incomplete_data["restaurant"]["email"] = email

if "location" in incomplete_data:
    incomplete_data["location"]["reviewSummary"] = review_summary

# Save the corrected JSON file
corrected_file_path = "346378_El_Monte__California_fixed.json"
with open(corrected_file_path, "w", encoding="utf-8") as f:
    json.dump(incomplete_data, f, ensure_ascii=False, indent=4)

corrected_file_path
