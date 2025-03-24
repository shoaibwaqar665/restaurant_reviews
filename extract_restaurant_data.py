import json
import re
from typing import Dict, List, Any, Optional

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
    return any(keyword in data for keyword in address_keywords) or re.search(r'\b[A-Z]{2}\s+\d{5}\b', data)

def is_phone_number(data):
    """Check if an item might be a phone number."""
    if not isinstance(data, str):
        return False
    
    # Look for common phone number patterns
    return re.search(r'(?:\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', data) is not None

def is_website(data):
    """Check if an item might be a website URL."""
    if not isinstance(data, str):
        return False
    
    # Look for common URL patterns
    return ('http' in data or 'www' in data or '.com' in data or '.org' in data or '.net' in data)

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
    
    # Helper function to recursively search for patterns
    def search_for_pattern(data, pattern_func, key_name, limit=None):
        found_items = []
        
        def _search(item, depth=0):
            if depth > 10:  # Limit recursion depth
                return
            
            if pattern_func(item):
                found_items.append(item)
                if limit and len(found_items) >= limit:
                    return
            
            if isinstance(item, list):
                for subitem in item:
                    _search(subitem, depth + 1)
            elif isinstance(item, dict):
                for subitem in item.values():
                    _search(subitem, depth + 1)
        
        _search(data)
        
        if found_items:
            if limit == 1:
                result[key_name] = found_items[0]
            else:
                result[key_name] = found_items
    
    # Search for address (strings containing address-like patterns)
    def is_address(item):
        if not isinstance(item, str):
            return False
        address_patterns = [
            r'\d+\s+[A-Za-z0-9\s]+(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Lane|Ln|Court|Ct|Place|Pl|Terrace|Ter)',
            r'[A-Za-z\s]+,\s*[A-Z]{2}\s*\d{5}'
        ]
        return any(re.search(pattern, item) for pattern in address_patterns) or "Blvd" in item or "Ave" in item or "St " in item

    # Search for phone numbers (improved pattern)
    def is_phone(item):
        if not isinstance(item, str):
            return False
        # Pattern to match standard US phone numbers
        phone_pattern = r'(?:\+1\s?)?\(?(?:(?:9\d\d)|(?:(?:[2-9]\d\d)))\)?[-.\s]?[2-9]\d\d[-.\s]?\d{4}'
        return re.search(phone_pattern, item) is not None and not item.startswith('http')

    # Search for websites
    def is_website(item):
        if not isinstance(item, str):
            return False
        # Only consider actual websites, not Google Maps URLs
        return ((item.startswith('http') or item.startswith('www.')) and
                '.' in item and
                'google.com/maps' not in item and
                'google.com/local' not in item)

    # Search for menu links
    def is_menu(item):
        if not isinstance(item, str):
            return False
        return ((item.startswith('http') or item.startswith('www.')) and
                'menu' in item.lower())

    # Search for ratings
    def is_rating(item):
        if not isinstance(item, (int, float)):
            return False
        return 1 <= item <= 5 and (isinstance(item, float) or (isinstance(item, str) and '.' in item))

    # Search for review texts
    def is_review(item):
        if not isinstance(item, str):
            return False
        return len(item) > 20 and item.startswith('"') and item.endswith('"')

    # Search for hours of operation (improved pattern)
    def is_hours(item):
        if not isinstance(item, str):
            return False
        hours_patterns = [
            r'\d{1,2}(?::\d{2})?\s*(?:AM|PM)\s*[-–]\s*\d{1,2}(?::\d{2})?\s*(?:AM|PM)',
            r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)[:-].*\d{1,2}\s*(?:AM|PM)'
        ]
        return any(re.search(pattern, item, re.IGNORECASE) for pattern in hours_patterns)

    # Search for weekly schedule
    def is_schedule(item):
        if not isinstance(item, str):
            return False
        return any(day in item for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])

    # Search for features/categories
    def is_feature(item):
        if not isinstance(item, str):
            return False
        # Consider common restaurant features
        features = ['Restaurant', 'Bar', 'Diner', 'Cafe', 'Bistro', 'Pizza', 'Italian', 'Mexican', 
                   'Chinese', 'Indian', 'Thai', 'Japanese', 'Fast Food', 'Fine Dining', 'Casual',
                   'Buffet', 'Takeout', 'Delivery', 'Family']
        
        # Exclude URLs, long descriptions, and irrelevant data
        if (item.startswith('http') or 
            len(item) > 100 or 
            item.startswith('Search') or 
            item.startswith('/geo') or
            item == name or  # Skip the restaurant name
            'TYPE_' in item):
            return False
            
        return any(feature.lower() in item.lower() for feature in features)

    # Search for descriptions/about sections
    def is_description(item):
        if not isinstance(item, str):
            return False
        return len(item) > 100 and len(item.split()) > 20 and not item.startswith('http')

    # Search for accessibility information
    def is_accessibility(item):
        if not isinstance(item, str):
            return False
        accessibility_keywords = [
            'wheelchair', 'accessible', 'accessibility', 'disabled', 'elevator',
            'ramp', 'restroom', 'service animal', 'parking', 'entrance'
        ]
        return any(keyword in item.lower() for keyword in accessibility_keywords)

    # Search for parking information
    def is_parking(item):
        if not isinstance(item, str):
            return False
        parking_keywords = ['parking', 'lot', 'garage', 'valet', 'street parking', 'free parking']
        return any(keyword in item.lower() for keyword in parking_keywords)

    # Search for review counts
    def find_review_count(data, depth=0):
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

    # Extract all the different types of data
    search_for_pattern(restaurant_data, is_address, "address", 1)
    search_for_pattern(restaurant_data, is_phone, "phone", 1)
    search_for_pattern(restaurant_data, is_website, "website", 1)
    search_for_pattern(restaurant_data, is_menu, "menu_url", 1)
    search_for_pattern(restaurant_data, is_rating, "rating", 1)
    search_for_pattern(restaurant_data, is_review, "reviews", 5)  # Get up to 5 reviews
    search_for_pattern(restaurant_data, is_hours, "hours", 1)
    search_for_pattern(restaurant_data, is_schedule, "schedule", 7)  # Up to 7 days
    search_for_pattern(restaurant_data, is_feature, "features")
    search_for_pattern(restaurant_data, is_description, "description", 1)
    search_for_pattern(restaurant_data, is_accessibility, "accessibility_features", 5)
    search_for_pattern(restaurant_data, is_parking, "parking_info", 3)

    # Extract review count
    review_count = find_review_count(restaurant_data)
    if review_count:
        result["review_count"] = review_count

    # Try to find specific data structures
    if len(restaurant_data) > 1 and isinstance(restaurant_data[1], list):
        subdata = restaurant_data[1]
        
        # Look for nested structures that might contain useful data
        for item in subdata:
            if isinstance(item, list) and len(item) > 0:
                # Look for address data
                for subitem in item:
                    if isinstance(subitem, list) and len(subitem) >= 3:
                        # Check for a sequence of strings that look like address parts
                        address_parts = [part for part in subitem if isinstance(part, str) and len(part) > 5]
                        if len(address_parts) >= 2:
                            if "address" not in result:
                                result["address"] = ", ".join(address_parts)
                
                # Look for rating and review count
                for i, subitem in enumerate(item):
                    if isinstance(subitem, (int, float)) and 1 <= subitem <= 5:
                        if i+1 < len(item) and isinstance(item[i+1], int) and item[i+1] > 10:
                            if "rating" not in result:
                                result["rating"] = subitem
                            if "review_count" not in result:
                                result["review_count"] = item[i+1]
                
                # Look for operating hours (daily)
                days_of_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                weekly_hours = {}
                
                for subitem in item:
                    if isinstance(subitem, list) and len(subitem) >= 2:
                        day = safe_get(subitem, 0)
                        hours = safe_get(subitem, 1, 0)
                        
                        if isinstance(day, str) and day in days_of_week and hours:
                            if isinstance(hours, list) and len(hours) > 0:
                                weekly_hours[day] = hours[0] if isinstance(hours[0], str) else None
                
                if weekly_hours and len(weekly_hours) > 0:
                    result["weekly_hours"] = weekly_hours
    
    # Special handler for menu data
    # Since menu URLs often require specific pattern matching
    menu_patterns = [
        r'https?://(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+(?:/[^/]+)*?/menu/?',
        r'https?://(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+/[^/]*menu[^/]*'
    ]
    
    for pattern in menu_patterns:
        menu_urls = []
        for item in restaurant_data:
            if isinstance(item, list):
                for subitem in item:
                    if isinstance(subitem, str) and re.search(pattern, subitem):
                        menu_urls.append(subitem)
        
        if menu_urls and "menu_url" not in result:
            result["menu_url"] = menu_urls[0]
    
    # Find the correct phone number - highest priority is a properly formatted US phone number
    if "description" in result:
        # Look for phone numbers in the description
        phone_matches = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', result["description"])
        if phone_matches:
            result["phone"] = phone_matches[0]
    
    # If we still don't have a phone, look more broadly
    if "phone" not in result or not re.match(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', str(result["phone"])):
        def find_phone(data, depth=0):
            if depth > 10:
                return None
            
            if isinstance(data, str):
                match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', data)
                if match:
                    return match.group(0)
            
            if isinstance(data, list):
                for item in data:
                    result = find_phone(item, depth + 1)
                    if result:
                        return result
            elif isinstance(data, dict):
                for v in data.values():
                    result = find_phone(v, depth + 1)
                    if result:
                        return result
            
            return None
        
        phone = find_phone(restaurant_data)
        if phone:
            result["phone"] = phone
    
    # Clean up the extracted data
    
    # If we found string reviews, clean them up
    if "reviews" in result and isinstance(result["reviews"], list):
        cleaned_reviews = []
        for review in result["reviews"]:
            # Remove quotes and clean extra whitespace
            cleaned_review = review.strip('"').strip()
            if cleaned_review and not cleaned_review.startswith('http'):
                cleaned_reviews.append(cleaned_review)
        result["reviews"] = cleaned_reviews
    
    # Clean up features to remove duplicates and irrelevant items
    if "features" in result and isinstance(result["features"], list):
        # Remove duplicates while preserving order
        unique_features = []
        seen = set()
        
        # Preprocess features
        for feature in result["features"]:
            if isinstance(feature, str):
                # Skip duplicates, URLs, and exact name matches
                feature_lower = feature.lower()
                if (feature_lower not in seen and 
                    not feature.startswith('http') and 
                    not feature.startswith('/') and
                    not feature.startswith('See') and
                    feature.lower() != name.lower() and
                    'type_' not in feature_lower and
                    '\"' not in feature):
                    
                    # Clean up some common prefixes
                    if feature.startswith('pizza_'):
                        feature = feature.replace('pizza_', '')
                    if feature.startswith('buffet_'):
                        feature = feature.replace('buffet_', '')
                    if feature.startswith('family_'):
                        feature = feature.replace('family_', '')
                    
                    # Change underscore to space and capitalize
                    if '_' in feature:
                        feature = feature.replace('_', ' ').title()
                    
                    seen.add(feature_lower)
                    unique_features.append(feature)
        
        # Categorize features more clearly
        cuisine_types = ["Pizza", "Italian", "Mexican", "Chinese", "Japanese", "Thai", "Indian", "American"]
        establishment_types = ["Restaurant", "Bar", "Diner", "Cafe", "Bistro", "Buffet"]
        service_types = ["Takeout", "Delivery", "No-contact", "Dine-in"]
        
        categories = []
        cuisines = []
        services = []
        amenities = []
        
        for feature in unique_features:
            lower_feature = feature.lower()
            
            # Categorize by type
            if any(cuisine.lower() in lower_feature for cuisine in cuisine_types):
                cuisines.append(feature)
            elif any(estab.lower() in lower_feature for estab in establishment_types):
                categories.append(feature)
            elif any(service.lower() in lower_feature for service in service_types):
                services.append(feature)
            else:
                amenities.append(feature)
        
        if categories:
            result["restaurant_type"] = categories
        if cuisines:
            result["cuisine"] = cuisines
        if services:
            result["services"] = services
        if amenities:
            result["amenities"] = amenities
        
        # Remove the original mixed features list
        del result["features"]
    
    # Clean up the description
    if "description" in result:
        result["description"] = result["description"].strip()
        
        # If we haven't found "about" but there's a description, use it
        if "about" not in result:
            result["about"] = result["description"]
    
    # Format weekly hours into a more readable format
    if "weekly_hours" in result:
        formatted_hours = []
        for day, hours in result["weekly_hours"].items():
            formatted_hours.append(f"{day}: {hours}")
        result["formatted_hours"] = formatted_hours
    
    # Extract price level if present (usually shown as $ symbols)
    def is_price_level(item):
        if not isinstance(item, str):
            return False
        return re.match(r'^[\$]{1,4}$', item) is not None
    
    price_levels = find_in_nested_data(restaurant_data, is_price_level)
    if price_levels:
        result["price_level"] = price_levels[0][1]
    
    return result

def main():
    # Input and output file paths
    input_file = "cleaned_google_response.json"
    output_file = "extracted_restaurant_data.json"
    
    # Read the input JSON file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return
    
    # Process each restaurant entry
    restaurant_data = []
    for i, entry in enumerate(data):
        restaurant_info = extract_restaurant_data(entry, i)
        if restaurant_info and "name" in restaurant_info:
            restaurant_data.append(restaurant_info)
    
    # Write the extracted data to the output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(restaurant_data, f, indent=2, ensure_ascii=False)
        print(f"Successfully extracted data for {len(restaurant_data)} restaurants to {output_file}")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    main() 