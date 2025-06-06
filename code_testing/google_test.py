import json
from datetime import datetime
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
def get_food_quality(content):
    if safe_get(content, 6, 2, 5)=="Food" and safe_get(content, 6, 2, 11, 0) != None:
        return safe_get(content, 6, 2, 11, 0)
    if safe_get(content, 6, 0, 5)=="Food" and safe_get(content, 6, 0, 11, 0) != None:
        return safe_get(content, 6, 0, 11, 0)
    if safe_get(content, 6, 3, 5)=="Food" and safe_get(content, 6, 3, 11, 0) != None:
        return safe_get(content, 6, 3, 11, 0)
    if safe_get(content, 6, 3, 5)=="Food" and safe_get(content, 6, 3, 11, 0) != None:
        return safe_get(content, 6, 3, 11, 0)
    if safe_get(content, 6, 1, 5)=="Food" and safe_get(content, 6, 1, 11, 0) != None:
        return safe_get(content, 6, 1, 11,0)
    if safe_get(content, 6, 4, 5)=="Food" and safe_get(content, 6, 4, 11, 0) != None:
        return safe_get(content, 6, 4, 11,0)
    if safe_get(content, 6, 4, 5)=="Food" and safe_get(content, 6, 4, 11, 0) != None:
        return safe_get(content, 6, 4, 11, 0)
    if safe_get(content, 6, 2, 5)=="Food" and safe_get(content, 6, 2, 11, 0) != None:
        return safe_get(content, 6, 2, 11,0)
    if safe_get(content, 6, 5, 5)=="Food" and safe_get(content, 6, 5, 11, 0) != None:
        return safe_get(content, 6, 5, 11,0)
    else:
        return None
    
def get_service(content):
   
    if safe_get(content, 6, 2, 5)=="Service" and safe_get(content, 6, 2, 11, 0) != None:
        return safe_get(content, 6, 2, 11, 0)
    if safe_get(content, 6, 0, 5)=="Service" and safe_get(content, 6, 0, 11, 0) != None:
        return safe_get(content, 6, 0, 11, 0)
    if safe_get(content, 6, 3, 5)=="Service" and safe_get(content, 6, 3, 11, 0) != None:
        return safe_get(content, 6, 3, 11, 0)
    if safe_get(content, 6, 3, 5)=="Service" and safe_get(content, 6, 3, 11, 0) != None:
        return safe_get(content, 6, 3, 11, 0)
    if safe_get(content, 6, 1, 5)=="Service" and safe_get(content, 6, 1, 11, 0) != None:
        return safe_get(content, 6, 1, 11,0)
    if safe_get(content, 6, 4, 5)=="Service" and safe_get(content, 6, 4, 11, 0) != None:
        return safe_get(content, 6, 4, 11,0)
    if safe_get(content, 6, 4, 5)=="Service" and safe_get(content, 6, 4, 11, 0) != None:
        return safe_get(content, 6, 4, 11, 0)
    if safe_get(content, 6, 2, 5)=="Service" and safe_get(content, 6, 2, 11, 0) != None:
        return safe_get(content, 6, 2, 11,0)
    if safe_get(content, 6, 5, 5)=="Service" and safe_get(content, 6, 5, 11, 0) != None:
        return safe_get(content, 6, 5, 11,0)
    else:
        return None
def get_atmosphere(content):
    if safe_get(content, 6, 4, 5)=="Atmosphere" and safe_get(content, 6, 4, 11, 0) != None:
        return safe_get(content, 6, 4, 11, 0)
    if safe_get(content, 6, 2, 5)=="Atmosphere" and safe_get(content, 6, 2, 11, 0) != None:
        return safe_get(content, 6, 2, 11,0)
    if safe_get(content, 6, 5, 5)=="Atmosphere" and safe_get(content, 6, 5, 11, 0) != None:
        return safe_get(content, 6, 5, 11,0)
    if safe_get(content, 6, 2, 5)=="Atmosphere" and safe_get(content, 6, 2, 11, 0) != None:
        return safe_get(content, 6, 2, 11, 0)
    if safe_get(content, 6, 0, 5)=="Atmosphere" and safe_get(content, 6, 0, 11, 0) != None:
        return safe_get(content, 6, 0, 11, 0)
    if safe_get(content, 6, 3, 5)=="Atmosphere" and safe_get(content, 6, 3, 11, 0) != None:
        return safe_get(content, 6, 3, 11, 0)
    if safe_get(content, 6, 3, 5)=="Atmosphere" and safe_get(content, 6, 3, 11, 0) != None:
        return safe_get(content, 6, 3, 11, 0)
    if safe_get(content, 6, 1, 5)=="Atmosphere" and safe_get(content, 6, 1, 11, 0) != None:
        return safe_get(content, 6, 1, 11,0)
    if safe_get(content, 6, 4, 5)=="Atmosphere" and safe_get(content, 6, 4, 11, 0) != None:
        return safe_get(content, 6, 4, 11,0)
    if safe_get(content, 6, 4, 5)=="Atmosphere" and safe_get(content, 6, 4, 11, 0) != None:
        return safe_get(content, 6, 4, 11, 0)
    if safe_get(content, 6, 2, 5)=="Atmosphere" and safe_get(content, 6, 2, 11, 0) != None:
        return safe_get(content, 6, 2, 11,0)
    if safe_get(content, 6, 5, 5)=="Atmosphere" and safe_get(content, 6, 5, 11, 0) != None:
        return safe_get(content, 6, 5, 11,0)
    
    else:
        return None
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
            "food_quality": get_food_quality(review_content),
            "service": get_service(review_content),
            "atmosphere": get_atmosphere(review_content),
            "photos": [],
            "response_text": safe_get(review_entry, 3, 14, 0, 0) if safe_get(review_entry, 3) else None,
            "translated_text": safe_get(review_content, 15, 1, 0),
            "is_translated": True if safe_get(review_content, 15, 1, 0) is not None else False
        }
        # print('Review content: ', safe_get(review_content,9))

        print('Review content: ',review_entry[2][14][0])
        # ### the response is in [3][14][0][0]
        # print('Review content:-'+review_entry[2][6][0][5]+'-')
        
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

def main():
    try:
        # Read the source JSON file
        with open('responses/ugcposts_1743875918.json', 'r', encoding='utf-8') as f:
            source_data = json.load(f)
            print("Successfully loaded JSON file")
        
        # Find and extract all reviews
        reviews = []
        
        # The reviews are in source_data[2][0]
        if (isinstance(source_data, list) and len(source_data) > 2 and 
            isinstance(source_data[2], list) and len(source_data[2]) > 0):
            
            review_entries = source_data[2][9]
            # print('Review entries: ', review_entries)
            if isinstance(review_entries, list):
                for entry in review_entries:
                    if isinstance(entry, list) and len(entry) > 0:
                        review_data = extract_review_data(entry)
                        if review_data:
                            reviews.append(review_data)
                            print(f"Successfully extracted review {len(reviews)}")
        
        # Write extracted reviews to output file
        with open('gmb_reviews.json', 'w', encoding='utf-8') as f:
            json.dump({
                "reviews": reviews,
                "total_reviews": len(reviews),
                "extraction_date": datetime.now().isoformat()
            }, f, indent=4, ensure_ascii=False)
            
        print(f"Successfully extracted {len(reviews)} reviews to gmb_reviews.json")
        
    except Exception as e:
        print(f"Error processing reviews: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main() 