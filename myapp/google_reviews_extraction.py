import json
from datetime import datetime
import os

from myapp.dbOperations import InsertRestaurantReviewsForGoogle
def convert_timestamp(timestamp):
    if timestamp:
        try:
            return datetime.fromtimestamp(timestamp / 1e6).strftime('%Y-%m-%d')
        except Exception as e:
            print(f"Error converting timestamp: {e}")
            return None
    return None

def safe_get(data, *indices, default=None):
    """Safely get nested data from a structure, returning default if any index is invalid."""
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
    # review_entry[2][6][0][5]
def get_attribute_value(content, attribute_name):
    for i in range(6):
        if safe_get(content, 6, i, 5) == attribute_name and safe_get(content, 6, i, 11, 0) is not None:
            return safe_get(content, 6, i, 11, 0)
    return None

def get_food_quality(content):
    return get_attribute_value(content, "Food")

def get_service(content):
    return get_attribute_value(content, "Service")

def get_atmosphere(content):
    return get_attribute_value(content, "Atmosphere")

def extract_review_data(review_entry):
    """Extract review data from a single review entry."""
    try:
        if not isinstance(review_entry, list) or len(review_entry) < 2:
            print(f"Invalid review entry format: {review_entry}")
            return None
            
        # Extract review ID and metadata
        review_id = review_entry[0]
        print(f"Processing review ID: {review_id}")
        
        # Extract reviewer information from [1][4][5]
        review_metadata = review_entry[1]
        reviewer_info = safe_get(review_metadata, 4, 5, default=[])
        
        reviewer_data = {
            "name": safe_get(reviewer_info, 0),
            "profile_image": safe_get(reviewer_info, 1),
            "profile_url": safe_get(reviewer_info, 2, 0) if safe_get(reviewer_info, 2) else None,
            "user_id": safe_get(reviewer_info, 3),
            "total_reviews": safe_get(reviewer_info, 5),
            "total_photos": safe_get(reviewer_info, 6),
            "local_guide_info": safe_get(reviewer_info, 10, 0) if safe_get(reviewer_info, 10) else None
        }
        
        # Extract review content from [2]
        review_content = review_entry[2]
        review_data = {
            "rating": safe_get(review_content, 0, 0),  # Rating is in [2][0][0]
            "timestamp": {
                "created": convert_timestamp(safe_get(review_metadata, 2)),
                "modified": convert_timestamp(safe_get(review_metadata, 3))
            },
            "review_text": safe_get(review_content, 15, 0, 0),  # Review text is in [2][1][0][0][0]
            "translated_text": safe_get(review_content, 15, 1, 0),
            "food_quality": get_food_quality(review_content),
            "service": get_service(review_content),
            "atmosphere": get_atmosphere(review_content),
            "photos": [],
            "response_text": safe_get(review_entry, 3, 14, 0, 0) if safe_get(review_entry, 3) else None,
            "is_translated": True if safe_get(review_content, 15, 1, 0) is not None else False
        }
        
        # Extract photos if they exist
        photos = safe_get(review_content, 2)
        if isinstance(photos, list):
            for photo in photos:
                photo_data = safe_get(photo, 1)
                if photo_data:
                    photo_url = safe_get(photo_data, 6, 0)
                    photo_dimensions = safe_get(photo_data, 6, 2)
                    if photo_url:
                        review_data["photos"].append({
                            "url": photo_url,
                            "dimensions": photo_dimensions
                        })
        
        # Extract review attributes if they exist
        attributes = safe_get(review_content, 4)
        if isinstance(attributes, list):
            for attr in attributes:
                if isinstance(attr, list) and len(attr) > 2:
                    attr_name = safe_get(attr, 1)
                    attr_values = safe_get(attr, 2)
                    if attr_values and isinstance(attr_values, list) and len(attr_values) > 0:
                        attr_value = safe_get(attr_values, 0, 1) or safe_get(attr_values, 0, 0)
                        if attr_name and attr_value:
                            review_data["attributes"][attr_name] = attr_value
        
        # Extract business response
        business_response = safe_get(review_entry, 3)
        response_data = {
            "date": safe_get(business_response, 3),
            "text": safe_get(business_response, 13, 0, 0) if safe_get(business_response, 13) else None
        }
        
        # Combine all data
        return {
            "review_id": review_id,
            "reviewer": reviewer_data,
            "review": review_data,
            "business_response": response_data,
            "metadata": {
                "extracted_date": datetime.now().isoformat()
            }
        }
    except Exception as e:
        print(f"Error extracting review data: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

def extract_google_reviews(folder_path,loc_reviews):
    try:
        # Read the source JSON file
        reviews = []
        folder_path = f'responses_{folder_path}/'
        for filename in os.listdir(folder_path):
            if filename.endswith('.json'):
                file_path = os.path.join(folder_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source_data = json.load(f)
                        print(f"Successfully loaded {filename}")

                    # Find and extract all reviews

                    # The reviews are in source_data[2][0]
                    if (isinstance(source_data, list) and len(source_data) > 2 and 
                        isinstance(source_data[2], list) and len(source_data[2]) > 0):
                        print('source data length: ', len(source_data[2]))
                        for i in range(len(source_data[2])):
                            review_entries = source_data[2][i]

                        # print('Review entries: ', review_entries)
                            if isinstance(review_entries, list):
                                for entry in review_entries:
                                    if isinstance(entry, list) and len(entry) > 0:
                                        review_data = extract_review_data(entry)
                                        if review_data:
                                            reviews.append(review_data)
                                            print(f"Successfully extracted review {len(reviews)}")

                    
                        
                    print(f"Successfully extracted {len(reviews)} reviews to gmb_reviews.json")
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
                    import traceback
                    print(traceback.format_exc())
        # Write extracted reviews to output file
        [extract_review_data_to_insert(review) for review in reviews]

        with open(loc_reviews+'.json', 'w', encoding='utf-8') as f:
            json.dump({
                "reviews": reviews,
                "total_number_of_reviews": len(reviews),
                "extraction_date": datetime.now().isoformat()
            }, f, indent=4, ensure_ascii=False)
        
    except Exception as e:
        print(f"Error processing reviews: {str(e)}")
        import traceback
        print(traceback.format_exc())


#### storing data in database #####

def extract_review_data_to_insert(data):
    extracted_data = {
        "review_id": data.get("review_id"),
        "reviewer_name": data.get("reviewer", {}).get("name"),
        "profile_image": data.get("reviewer", {}).get("profile_image"),
        "profile_url": data.get("reviewer", {}).get("profile_url"),
        "user_id": data.get("reviewer", {}).get("user_id"),
        "total_reviews": data.get("reviewer", {}).get("total_reviews"),
        "total_photos": data.get("reviewer", {}).get("total_photos"),
        "local_guide_info": data.get("reviewer", {}).get("local_guide_info"),
        "rating": data.get("review", {}).get("rating"),
        "created_timestamp": data.get("review", {}).get("timestamp", {}).get("created"),
        "modified_timestamp": data.get("review", {}).get("timestamp", {}).get("modified"),
        "review_text": data.get("review", {}).get("review_text"),
        "translated_text": data.get("review", {}).get("translated_text"),
        "is_translated": data.get("review", {}).get("is_translated"),
        "food_quality": data.get("review", {}).get("food_quality"),
        "service": data.get("review", {}).get("service"),
        "atmosphere": data.get("review", {}).get("atmosphere"),
        "photos": [{
            "url": photo.get("url"),
            "dimensions": photo.get("dimensions")
        } for photo in data.get("review", {}).get("photos", [])],
        "response_text": data.get("review", {}).get("response_text"),
        "business_response_date": data.get("business_response", {}).get("date"),
        "business_response_text": data.get("business_response", {}).get("text"),
        "extracted_date": data.get("metadata", {}).get("extracted_date")
    }
    InsertRestaurantReviewsForGoogle(extracted_data)
    return extracted_data
