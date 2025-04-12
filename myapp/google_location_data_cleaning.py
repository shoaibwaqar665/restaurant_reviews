import json
import re

from myapp.dbOperations import InsertRestaurantDetailsForGoogle

def safe_get(data, *indices, default=None):
    """Safely access nested elements in a dictionary or list.
    
    Args:
        data: The data structure to access
        *indices: A sequence of keys or indices to access nested elements
        default: The value to return if the path is not found
        
    Returns:
        The value at the specified path or the default value if not found
    """
    try:
        result = data
        for idx in indices:
            if isinstance(result, (list, tuple)) and isinstance(idx, int) and 0 <= idx < len(result):
                result = result[idx]
            elif isinstance(result, dict) and idx in result:
                result = result[idx]
            else:
                return default
        return result
    except (IndexError, KeyError, TypeError):
        return default

def find_in_nested_data(data, pattern_func, max_depth=10, path=None, results=None, current_depth=0):
    """Search through nested data for items matching a pattern function.
    
    Args:
        data: The data structure to search
        pattern_func: A function that returns True when the target pattern is found
        max_depth: Maximum depth to search
        path: Current path (for recursion)
        results: Results list (for recursion)
        current_depth: Current depth (for recursion)
    
    Returns:
        List of (path, value) tuples for matching items
    """
    if current_depth >= max_depth:
        return results
    
    if path is None:
        path = []
    if results is None:
        results = []
    
    if pattern_func(data):
        results.append((path, data))
    
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                find_in_nested_data(v, pattern_func, max_depth, path + [k], results, current_depth + 1)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                find_in_nested_data(item, pattern_func, max_depth, path + [i], results, current_depth + 1)
    
    return results

def is_address(data):
    """Check if an item might be an address."""
    if not isinstance(data, str):
        return False
    
    # Look for common address patterns
    address_keywords = ['Ave', 'Blvd', 'St', 'Road', 'Dr', 'Street', 'Avenue', 'Boulevard', 'Drive', 'Ln', 'Lane', 'Hwy', 'Highway']
    
    # More specific address pattern matching
    has_street_number = bool(re.search(r'\d+\s+[A-Za-z]', data))
    has_address_keyword = any(keyword in data for keyword in address_keywords)
    has_zip = bool(re.search(r'\b\d{5}\b', data))
    has_state = bool(re.search(r'\b[A-Z]{2}\b', data))
    country_pattern = r",\s*(United States|USA|Canada|UK|Australia|India)$" 
    has_country = bool(re.search(country_pattern, data))
    # Exclude common false positives
    false_positives = ['Pacific Standard Time', 'http', 'www', '.com', '.org', '.net']
    if any(fp in data for fp in false_positives):
        return False
    
    return (has_street_number and has_address_keyword and has_state and has_zip and has_country) or (has_zip and has_state)

def is_phone_number(data):
    """Check if an item might be a phone number."""
    if not isinstance(data, str):
        return False
    
    # Clean the string
    cleaned = re.sub(r'[^\d]', '', data)
    
    # Valid phone numbers should be 10 or 11 digits (with country code)
    if len(cleaned) not in [10, 11]:
        return False
    
    # Look for common phone number patterns
    phone_patterns = [
        r'\(?[2-9]\d{2}\)?[-.\s]?[2-9]\d{2}[-.\s]?\d{4}',  # (555) 555-5555 or similar
        r'\+?1[-.\s]?[2-9]\d{2}[-.\s]?[2-9]\d{2}[-.\s]?\d{4}'  # +1 555-555-5555 or similar
    ]
    
    return any(re.match(pattern, data) for pattern in phone_patterns)

def is_website(data):
    """Check if an item might be a website URL."""
    if not isinstance(data, str):
        return False
    
    # Exclude common false positives
    false_positives = [
        'google.com',
        'gstatic.com',
        'googleapis.com',
        '/images/',
        '/icons/',
        '.png',
        '.jpg',
        '.gif',
        'local guide program'
    ]
    
    if any(fp in data.lower() for fp in false_positives):
        return False
    
    # Look for common URL patterns using simpler approach
    has_url_pattern = ('http' in data or 'www' in data or '.com' in data or '.org' in data or '.net' in data)
    
    # Additional validation to ensure it's a real website
    if has_url_pattern:
        # Check if it's a direct restaurant website (not a search or maps URL)
        if '/search' in data.lower() or '/maps' in data.lower() or '/place' in data.lower():
            return False
        return True
    
    return False

def is_menu_url(data):
    """Check if an item might be a menu URL."""
    if not isinstance(data, str):
        return False
    
    # Exclude common false positives
    false_positives = [
        'google.com/maps',
        'google.com/search',
        'gstatic.com',
        'googleapis.com',
        '/images/',
        '/icons/',
        '.png',
        '.jpg',
        '.gif'
    ]
    
    if any(fp in data.lower() for fp in false_positives):
        return False
    
    # Look for menu-specific patterns
    menu_keywords = ['menu', 'menus', 'food', 'order', 'ordering']
    if not any(keyword in data.lower() for keyword in menu_keywords):
        return False
    
    # Look for common URL patterns
    url_pattern = r'https?://(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?'
    return bool(re.match(url_pattern, data))

def is_review_count(item):
    """Check if an item might be a review count."""
    if not isinstance(item, (int, str)):
        return False
    
    # Convert to string for consistent handling
    item_str = str(item)
    
    # Remove any commas from the string
    item_str = item_str.replace(',', '')
    
    # Check if it's a reasonable number (between 1 and 1 million)
    try:
        num = int(item_str)
        return 1 <= num <= 1000000
    except ValueError:
        return False

def find_review_count(data, depth=0):
    """Find the review count in the data structure."""
    if depth > 10:
        return None
    
    if isinstance(data, (int, str)):
        if is_review_count(data):
            return int(str(data).replace(',', ''))
    
    if isinstance(data, list):
        for i, item in enumerate(data):
            # Check if current item is a rating and next item is a review count
            if isinstance(item, (int, float)) and 1 <= item <= 5:
                if i + 1 < len(data) and is_review_count(data[i + 1]):
                    return int(str(data[i + 1]).replace(',', ''))
            
            result = find_review_count(item, depth + 1)
            if result:
                return result
    elif isinstance(data, dict):
        for v in data.values():
            result = find_review_count(v, depth + 1)
            if result:
                return result
    
    return None

def extract_metadata(data):
    """Extract metadata like rating, review count, etc."""
    metadata = {}
    
    
    def process_item(item, context=None):
        nonlocal metadata
        
        if isinstance(item, (list, tuple)):
           
            # Process each item in the list
            for i, subitem in enumerate(item):
                process_item(subitem, context=item)
        
        elif isinstance(item, dict):
            for value in item.values():
                process_item(value)
        
        elif isinstance(item, str):
            # Look for address
            if is_address(item) and ('address' not in metadata or len(item) > len(metadata['address'])):
                metadata['address'] = item
            
            # Look for phone number
            if is_phone_number(item) and ('phone' not in metadata or len(item) > len(metadata['phone'])):
                # Format phone number consistently
                cleaned = re.sub(r'[^\d]', '', item)
                if len(cleaned) == 10:
                    metadata['phone'] = f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
                elif len(cleaned) == 11 and cleaned[0] == '1':
                    metadata['phone'] = f"+1 ({cleaned[1:4]}) {cleaned[4:7]}-{cleaned[7:]}"
            
            # Look for website (prioritize non-menu URLs)
            if is_website(item) and 'website' not in metadata:
                metadata['website'] = item
            
            # Look for menu URL (prefer main menu URLs)
            if is_menu_url(item):
                if 'menu_url' not in metadata or '/menu/' in item.lower():
                    metadata['menu_url'] = item
            
            # Look for price level
            if all(c == '$' for c in item) and 1 <= len(item) <= 4:
                metadata['price_level'] = len(item)
    
    process_item(data)
    return metadata

def extract_restaurant_data(restaurant_data, index):
    """Extract data from a restaurant entry."""
    result = {}
    
    # If the entry is not a list or is empty, skip it
    if not isinstance(restaurant_data, list) or len(restaurant_data) == 0:
        return None
    
    # Extract name from the first element if it's a string
    name = restaurant_data[0]
    if isinstance(name, str):
        result["name"] = name
    else:
        # If name is not a string, this may not be a valid restaurant entry
        return None

    # Extract basic metadata (rating, review count, etc.)
    metadata = extract_metadata(restaurant_data)
    result.update(metadata)


    # Extract schedule
    def extract_schedule(data):
        schedule = {}
        if isinstance(data, list):
            for item in data:
                if isinstance(item, list) and len(item) >= 4:
                    day = item[0]
                    if isinstance(day, str) and day in ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]:
                        time_data = item[3]
                        if isinstance(time_data, list) and len(time_data) > 0:
                            if isinstance(time_data[0], list) and len(time_data[0]) > 0:
                                time_str = time_data[0][0]
                                if isinstance(time_str, str):
                                    # Format: Day: Open Time - Close Time
                                    schedule[day] = time_str
        return schedule

    # Extract features by category
    def extract_features(data):
        features = {}
        if isinstance(data, list):
            for item in data:
                if isinstance(item, list) and len(item) >= 3:
                    category = item[0]
                    if isinstance(category, str) and isinstance(item[2], list):
                        feature_list = set()  # Use set to store unique values
                        for feature in item[2]:
                            if isinstance(feature, list) and len(feature) >= 2:
                                feature_name = feature[1]
                                if isinstance(feature_name, str):
                                    feature_list.add(feature_name)
                        if feature_list:
                            features[category] = sorted(list(feature_list))  # Convert back to sorted list
        return features

    # Recursively search through the data structure
    def search_data(data, depth=0):
        if depth > 10:  # Prevent infinite recursion
            return
            
        if isinstance(data, list):
            # First, try to extract metadata at this level
            metadata = extract_metadata(data)
            result.update(metadata)
            
            for item in data:
                if isinstance(item, list):
                    # Extract schedule
                    schedule = extract_schedule(item)
                    if schedule:
                        if "schedule" not in result:
                            result["schedule"] = {}
                        result["schedule"].update(schedule)
                    
                    # Extract features
                    features = extract_features(item)
                    if features:
                        if "features" not in result:
                            result["features"] = {}
                        for category, feature_list in features.items():
                            if category not in result["features"]:
                                result["features"][category] = []
                            result["features"][category].extend(feature_list)
                            # Remove duplicates while preserving order
                            result["features"][category] = list(dict.fromkeys(result["features"][category]))
                    
                    # Recursively search nested lists
                    search_data(item, depth + 1)
        elif isinstance(data, dict):
            for value in data.values():
                search_data(value, depth + 1)

    # Start the recursive search
    search_data(restaurant_data)

    # Format schedule for better readability
    if "schedule" in result:
        formatted_schedule = {}
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            if day in result["schedule"]:
                formatted_schedule[day] = result["schedule"][day]
        result["schedule"] = formatted_schedule

    # Clean up and organize the data
    grouped_features = {}  # Initialize to avoid UnboundLocalError
    if "features" in result:
        # Group similar features together
        grouped_features = {}
        
        for category, features in result["features"].items():
            # Skip raw category paths and use cleaned up versions
            if category.startswith("/geo/type/"):
                clean_category = category.split("/")[-1].replace("_", " ").title()
            else:
                clean_category = category
            
            grouped_features[clean_category] = features
        
    result["features"] = grouped_features

    return result


def extract_rating_and_reviews(json_string):
    # Ensure input is a string
    if not isinstance(json_string, str):
        try:
            json_string = json.dumps(json_string)
        except (TypeError, ValueError):
            return None

    simple_pattern = r'(\d+\.\d+)\s*,\s*(\d+)\s*,\s*null\s*,\s*"Moderately expensive"'
    simple_match = re.search(simple_pattern, json_string)
    if simple_match:
        print("Found match with simpler pattern!")
        rating = simple_match.group(1)
        reviews = simple_match.group(2)
        return {
            'rating': float(rating),
            'reviews': int(reviews)
        }
    return None

def find_tel_links(obj):
    tel_links = []
    if isinstance(obj, dict):
        for value in obj.values():
            tel_links.extend(find_tel_links(value))
    elif isinstance(obj, list):
        for item in obj:
            tel_links.extend(find_tel_links(item))
    elif isinstance(obj, str) and obj.startswith("tel:"):
        tel_links.append(obj.replace("tel:", ""))
    return tel_links

def fallback_extract_details(entry):
    try:
        hotel_data = entry[1][0]
    except (IndexError, TypeError):
        return {}

    details = {}

    # Address
    try:
        address_parts = hotel_data[14][2]
        details["address"] = ', '.join(address_parts)
    except (IndexError, TypeError):
        details["address"] = "N/A"

    # Rating
    try:
        details["rating"] = hotel_data[14][4][8]
    except (IndexError, TypeError):
        details["rating"] = "N/A"

    # Review Count
    try:
        details["reviews"] = hotel_data[14][4][7]
    except (IndexError, TypeError):
        details["reviews"] = "N/A"

    return details

def location_data_cleaning(unclean_json_data, output_file,restaurant_name,location_name):
  
    # # Read the input JSON file
    # # try:
    # #     with open(input_file, 'r', encoding='utf-8') as f:
    # #         data = json.load(f)
    # # except Exception as e:
    # #     print(f"Error reading input file: {e}")
    # #     return
    # print('unclean_json_data',unclean_json_data)
    restaurant_data = []
    
    # Process and insert each restaurant entry directly
    for i, entry in enumerate(unclean_json_data):
        restaurant_info = extract_restaurant_data(entry, i)
        if restaurant_info and "name" in restaurant_info:
            # Extract and update rating and reviews directly
            result = extract_rating_and_reviews(entry)
            if result:
                restaurant_info.update(result)
            # Fallback: if address/rating/review_count is missing
            if "address" not in restaurant_info or \
               "rating" not in restaurant_info or \
               "reviews" not in restaurant_info:
                fallback_data = fallback_extract_details(entry)
                for k, v in fallback_data.items():
                    restaurant_info.setdefault(k, v)

            # Optional: extract phone numbers
            tel_numbers = find_tel_links(entry)
            if tel_numbers:
                restaurant_info["phone"] = tel_numbers
            # Insert into database
            InsertRestaurantDetailsForGoogle(restaurant_info,restaurant_name,location_name)
            
            # Save to list for writing to a file
            restaurant_data.append(restaurant_info)
    
    # Write cleaned data to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(restaurant_data, f, indent=2, ensure_ascii=False)
        print(f"Successfully wrote data for {len(restaurant_data)} restaurants to {output_file}")
    except Exception as e:
        print(f"Error writing to output file: {e}")
    
    print("Data insertion and file writing completed.")
