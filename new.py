import usaddress

def split_us_address(address):
    try:
        parsed = usaddress.tag(address)[0]
        return {
            "street": parsed.get("AddressNumber", "") + " " + parsed.get("StreetName", ""),
            "city": parsed.get("PlaceName", ""),
            "state": parsed.get("StateName", ""),
            "postal_code": parsed.get("ZipCode", ""),
            "country": "United States"  # Since usaddress is US-specific
        }
    except usaddress.RepeatedLabelError:
        return {"error": "Could not parse address"}

address = "1406 S Fairview St, Santa Ana, CA 92704, United States"
print(split_us_address(address))
