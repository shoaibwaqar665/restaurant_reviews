# import usaddress

# def split_us_address(address):
#     if not isinstance(address, str) or "Canada" in address:
#         return {}  # Skip non-US or explicitly Australian addresses
#     try:
#         parsed = usaddress.tag(address)[0]
#         return {
#             "street": parsed.get("AddressNumber", "") + " " + parsed.get("StreetName", ""),
#             "city": parsed.get("PlaceName", ""),
#             "state": parsed.get("StateName", ""),
#             "postal_code": parsed.get("ZipCode", ""),
#             "country": "United States"
#         }
#     except usaddress.RepeatedLabelError as e:
#         print(f"Error parsing address (likely non-US): {address}")
#         return {}
    
# # Example usage
# address = "NewActon Precinct, 25 Edinburgh Ave, Canberra ACT 2601, Australia"
# parsed_address = split_us_address(address)
# print(parsed_address)

import googlemaps

gmaps = googlemaps.Client(key="AIzaSyB9irjntPHdEJf024h7H_XKpS11OeW1Nh8")

def parse_address_google(address):
    try:
        result = gmaps.geocode(address)
        if not result:
            return {}

        components = result[0]["address_components"]
        parsed = {
            "street": "",
            "city": "",
            "state": "",
            "postal_code": "",
            "country": "",
        }

        for comp in components:
            types = comp["types"]
            if "street_number" in types:
                parsed["street"] = comp["long_name"] + " " + parsed["street"]
            elif "route" in types:
                parsed["street"] += comp["long_name"]
            elif "locality" in types:
                parsed["city"] = comp["long_name"]
            elif "administrative_area_level_1" in types:
                parsed["state"] = comp["short_name"]
            elif "postal_code" in types:
                parsed["postal_code"] = comp["long_name"]
            elif "country" in types:
                parsed["country"] = comp["long_name"]

        return {
            "street": parsed["street"],
            "city": parsed["city"],
            "state": parsed["state"],
            "postal_code": parsed["postal_code"],
            "country": parsed["country"]
            
        }
    except Exception as e:
        print(f"Error parsing address: {e}")
        return {}
    
address_data=parse_address_google("NewActon Precinct, 25 Edinburgh Ave, Canberra ACT 2601, Australia")
street = address_data.get("street", "")
city = address_data.get("city", "")
state = address_data.get("state", "")
postal_code = address_data.get("postal_code", "")
country = address_data.get("country", "")

print(f"Street: {street}")
print(f"City: {city}")
print(f"State: {state}")
print(f"Postal Code: {postal_code}")
print(f"Country: {country}")