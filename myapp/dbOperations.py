import uuid
import psycopg2  
import psycopg2.extras  
import sys 
import requests
import json
from datetime import datetime

from myapp.environment import Scraping

Scraping = Scraping

def InsertRestaurantDetails(restaurant_data):
    """
    Insert restaurant details from Tripadvisor JSON data into the trip_restaurants_details table.
    
    Args:
        restaurant_data (dict): The restaurant data from the Tripadvisor JSON
    
    Returns:
        str: The location_id of the inserted or existing restaurant
    """
    conn = None
    cursor = None
    
    try:
        conn = psycopg2.connect(
            dbname=Scraping["Database"],
            user=Scraping["Username"],
            password=Scraping["Password"],
            host=Scraping["Host"],
            port=Scraping["Port"]
        )
        cursor = conn.cursor()

        location = restaurant_data["location"]
        details = restaurant_data.get("restaurant", {})
        location_id = str(location["locationId"])
        
        # Check if restaurant already exists
        check_query = """
            SELECT COUNT(*)
            FROM trip_restaurants_details
            WHERE location_id = %s
        """
        cursor.execute(check_query, (location_id,))
        existing_count = cursor.fetchone()[0]
        
        if existing_count == 0:
            # Prepare data for insertion
            address = location.get("localizedStreetAddress", {})
            schedule_data = details.get("schedule", {})
            
            insert_query = """
                INSERT INTO trip_restaurants_details (
                    location_id,
                    name,
                    address,
                    city,
                    state,
                    country,
                    postal_code,
                    phone,
                    email,
                    website,
                    schedule,
                    thumbnail,
                    review_rating,
                    review_count,
                    dining_options,
                    cuisines,
                    meal_types,
                    diets,
                    menu_url
                    
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Handle case where address might be in a single string format
            street = ""
            city = ""
            state = ""
            postal_code = ""
            
            # First check if we have a localizedRealtimeAddress string to parse
            localized_address = details.get("localizedRealtimeAddress")
            if localized_address and isinstance(localized_address, str):
                # Try to parse address like "791 E Foothill Blvd, Upland, CA 91786"
                try:
                    # Split by commas
                    address_parts = [part.strip() for part in localized_address.split(',')]
                    
                    # First part is typically the street address
                    if len(address_parts) > 0:
                        street = address_parts[0]
                    
                    # Second part is typically the city
                    if len(address_parts) > 1:
                        city = address_parts[1]
                    
                    # Last part typically contains state and zip code
                    if len(address_parts) > 2:
                        last_part = address_parts[-1].split()
                        if len(last_part) > 0:
                            state = last_part[0]  # First element should be state code
                        if len(last_part) > 1:
                            postal_code = last_part[-1]  # Last element should be zip code
                            
                    print(f"Parsed address: Street={street}, City={city}, State={state}, Postal={postal_code}")
                except Exception as parse_error:
                    print(f"Error parsing localized address: {str(parse_error)}")
            
            # If we didn't get values from localizedRealtimeAddress, use localizedStreetAddress
            if not street and address.get("street1"):
                street = address.get("street1", "")
                if address.get("street2"):
                    street += ", " + address.get("street2")
            
            if not city:
                city = address.get("city")
                
            if not state:
                state = address.get("state")
                
            if not postal_code:
                postal_code = address.get("postalCode")
                
            # Get thumbnail URL
            thumbnail = None
            if "thumbnail" in location and location["thumbnail"] is not None and isinstance(location["thumbnail"], dict) and "url" in location["thumbnail"]:
                thumbnail = location["thumbnail"]["url"]
                
            # Get review stats
            review_rating = None
            review_count = None
            if "reviewSummary" in location:
                review_rating = location["reviewSummary"].get("rating")
                review_count = location["reviewSummary"].get("count")
            print(f"Review rating: {review_rating}, Review count: {review_count}")        
            # Menu info
            menu_url = None
            has_menu_provider = False
            if "menu" in details:
                if "decoded_menu_url" in details["menu"]:
                    menu_url = details["menu"]["decoded_menu_url"]
                has_menu_provider = details["menu"].get("has_provider", False)

            website = None
            if "restaurant_decoded_url" in details:
                website = details["restaurant_decoded_url"]
            
           
            print(f"Email: {location.get('email')}")
            # Convert schedule to JSON
            schedule_json = json.dumps(schedule_data) if schedule_data else None
            
            cursor.execute(
                insert_query,
                (
                    location_id,
                    location.get("name") or f"{city} {state}".strip(),
                    street,
                    city,
                    state,
                    location.get("isoCountryCode") or "US",
                    postal_code,
                    details.get("telephone", ""),
                    location.get("email"),
                    website,
                    schedule_json,
                    thumbnail,
                    review_rating,
                    review_count,
                    details.get("dining_options", []),
                    details.get("cuisines", []),
                    details.get("meal_types", []),
                    details.get("diets", []),
                    menu_url
                )
            )
            conn.commit()
            print(f"Restaurant details added to the database for location_id: {location_id}")
        else:
            print(f"Restaurant already exists in the database for location_id: {location_id}")
        
        return location_id
    except Exception as e:
        import traceback
        error_line = traceback.extract_tb(sys.exc_info()[2])[-1].lineno
        print(f"Error inserting restaurant details: {str(e)}", file=sys.stderr)
        print(f"Error occurred at line: {error_line}", file=sys.stderr)
        print(f"Error type: {type(e).__name__}", file=sys.stderr)
        print(f"Full traceback:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        
        # Print the problematic data
        print('Restaurant data:', file=sys.stderr)
        try:
            print(f"Location ID: {restaurant_data['location'].get('locationId')}", file=sys.stderr)
            print(f"Name: {restaurant_data['location'].get('name')}", file=sys.stderr)
            if 'thumbnail' in restaurant_data['location']:
                print(f"Thumbnail type: {type(restaurant_data['location']['thumbnail'])}", file=sys.stderr)
                print(f"Thumbnail value: {restaurant_data['location']['thumbnail']}", file=sys.stderr)
            
            # Check array fields
            restaurant = restaurant_data.get('restaurant', {})
            print(f"dining_options type: {type(restaurant.get('dining_options'))}", file=sys.stderr)
            print(f"cuisines type: {type(restaurant.get('cuisines'))}", file=sys.stderr)
            print(f"meal_types type: {type(restaurant.get('meal_types'))}", file=sys.stderr)
            print(f"diets type: {type(restaurant.get('diets'))}", file=sys.stderr)
        except Exception as debug_error:
            print(f"Error while debugging: {str(debug_error)}", file=sys.stderr)
            
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def InsertRestaurantReviews(restaurant_data, location_id):
    """
    Insert reviews from Tripadvisor JSON data into the trip_reviews and trip_review_photos tables.
    Stops processing if 5 consecutive reviews already exist in the database.
    
    Args:
        restaurant_data (dict): The restaurant data from the Tripadvisor JSON
        location_id (str): The location_id of the restaurant
    
    Returns:
        int: The number of new reviews inserted
    """
    conn = None
    cursor = None
    new_reviews_count = 0
    consecutive_existing_count = 0
    
    try:
        conn = psycopg2.connect(
            dbname=Scraping["Database"],
            user=Scraping["Username"],
            password=Scraping["Password"],
            host=Scraping["Host"],
            port=Scraping["Port"]
        )
        cursor = conn.cursor()
        
        reviews = restaurant_data.get("reviews", [])
        
        for review in reviews:
            review_id = review.get("id")
            
            # Check if review already exists
            check_query = """
                SELECT COUNT(*)
                FROM trip_reviews
                WHERE review_id = %s
            """
            cursor.execute(check_query, (review_id,))
            existing_count = cursor.fetchone()[0]
            
            if existing_count == 0:
                # Reset consecutive counter when a new review is found
                consecutive_existing_count = 0
                
                # Prepare data for insertion
                is_translated = review.get("is_translated", False)
                translated_title = None
                translated_text = None
                
                if is_translated and "translation" in review:
                    translated_title = review["translation"].get("title")
                    translated_text = review["translation"].get("text")
                
                # Insert review
                insert_query = """
                    INSERT INTO trip_reviews (
                        review_id,
                        location_id,
                        user_id,
                        username,
                        title,
                        text,
                        translated_title,
                        translated_text,
                        is_translated,
                        rating,
                        published_date,
                        language
                    ) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """
                
                # Convert date string to date object if it exists
                published_date = None
                if "publishedDate" in review:
                    try:
                        published_date = datetime.strptime(review["publishedDate"], "%Y-%m-%d").date()
                    except ValueError:
                        published_date = None
                
                cursor.execute(
                    insert_query,
                    (
                        review_id,
                        location_id,
                        review.get("userId"),
                        review.get("username"),
                        review.get("title"),
                        review.get("text"),
                        translated_title,
                        translated_text,
                        is_translated,
                        review.get("rating"),
                        published_date,
                        review.get("language")
                    )
                )
                
                # Insert photos if they exist
                photos = review.get("photos", [])
                if photos:
                    for photo in photos:
                        if "url" in photo:
                            photo_query = """
                                INSERT INTO trip_review_photos (
                                    review_id,
                                    photo_url
                                ) 
                                VALUES (%s, %s)
                            """
                            cursor.execute(photo_query, (review_id, photo["url"]))
                
                new_reviews_count += 1
            else:
                # Increment consecutive existing reviews counter
                consecutive_existing_count += 1
                print(f"Review {review_id} already exists. Consecutive existing reviews: {consecutive_existing_count}")
                
                # Break the loop if 5 consecutive existing reviews are found
                if consecutive_existing_count >= 5:
                    print(f"Found 5 consecutive existing reviews. Stopping review processing.")
                    break
                
        conn.commit()
        print(f"Inserted {new_reviews_count} new reviews for location_id: {location_id}")
        return new_reviews_count
    except Exception as e:
        print(f"Error inserting reviews: {str(e)}", file=sys.stderr)
        return 0
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def ProcessTripadvisorData(json_file_path):
    """
    Process a Tripadvisor JSON file and insert the data into the database.
    
    Args:
        json_file_path (str): The path to the JSON file
    
    Returns:
        tuple: (location_id, number of reviews inserted)
    """
    try:
        # Load the JSON data
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Insert restaurant details
        location_id = InsertRestaurantDetails(data)
        
        if location_id:
            # Insert reviews
            review_count = InsertRestaurantReviews(data, location_id)
            return location_id, review_count
        else:
            return None, 0
            
    except Exception as e:
        print(f"Error processing JSON file: {str(e)}", file=sys.stderr)
        return None, 0

