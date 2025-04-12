import psycopg2  
import sys 
import json
from datetime import datetime
from decimal import Decimal
import usaddress
from myapp.environment import Scraping

Scraping = Scraping
def split_us_address(address):
    if not isinstance(address, str) or "Australia" in address:
        return {}  # Skip non-US or explicitly Australian addresses
    try:
        parsed = usaddress.tag(address)[0]
        return {
            "street": parsed.get("AddressNumber", "") + " " + parsed.get("StreetName", ""),
            "city": parsed.get("PlaceName", ""),
            "state": parsed.get("StateName", ""),
            "postal_code": parsed.get("ZipCode", ""),
            "country": "United States"
        }
    except usaddress.RepeatedLabelError as e:
        print(f"Error parsing address (likely non-US): {address}")
        return {}
def InsertRestaurantDetailsForTripadvisor(restaurant_data, restaurant_query):
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
                    menu_url,
                    restaurant_name,
                    business_key
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            parent_location_name = ""
            if "parent" in location and location["parent"] is not None and isinstance(location["parent"], dict):
                parent_location_name = location["parent"].get("localizedName", "")
                print(f"Parent location: {parent_location_name}")
                
            # Convert schedule to JSON
            schedule_json = json.dumps(schedule_data) if schedule_data else None
            complete_address = f"{street}, {city}, {state} {postal_code}"
            # Prepare the values tuple
            city_name = parent_location_name or location.get("name") or f"{city} {state}"
            restaurant_key = (parent_location_name or '') + ' ' + (complete_address or '') + ' ' + (restaurant_query or '')
            restaurant_key = restaurant_key.replace(" ", "_")
            restaurant_key = restaurant_key.replace("'", "")
            restaurant_key = restaurant_key.replace(",", "_")
            values = (
                location_id,
                parent_location_name or location.get("name") or f"{city} {state}".strip(),
                complete_address,
                city_name,
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
                menu_url,
                restaurant_query,
                restaurant_key
            )
            
            cursor.execute(insert_query, values)
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


def InsertRestaurantReviewsForTripAdvisor(restaurant_data, location_id,restaurant_key):
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
                
                # Use original title as fallback for translated_title if it's null
                if translated_title is None:
                    translated_title = review.get("title", "")
                
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
                        language,
                        value_rating,
                        service_rating,
                        food_rating,
                        atmosphere_rating,
                        contribution,
                        likes,
                        avatar,
                        business_key,
                        room_rating,
                        sleep_rating,
                        location_rating,
                        cleanliness_rating
                    ) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """
                
                # Convert date string to date object if it exists
                published_date = None
                if "publishedDate" in review:
                    try:
                        published_date = datetime.strptime(review["publishedDate"], "%Y-%m-%d").date()
                    except ValueError:
                        published_date = None
                
                # Extract individual ratings from additionalRatings
                value_rating = None
                service_rating = None
                food_rating = None
                atmosphere_rating = None
                room_rating = None
                sleep_rating = None
                location_rating = None
                cleanliness_rating = None

                
                if review.get("additionalRatings"):
                    for rating_item in review["additionalRatings"]:
                        if rating_item.get("ratingLabel") == "Value":
                            value_rating = rating_item.get("rating")
                        elif rating_item.get("ratingLabel") == "Service":
                            service_rating = rating_item.get("rating")
                        elif rating_item.get("ratingLabel") == "Food":
                            food_rating = rating_item.get("rating")
                        elif rating_item.get("ratingLabel") == "Atmosphere":
                            atmosphere_rating = rating_item.get("rating")
                        elif rating_item.get("ratingLabel") == "Rooms":
                            room_rating = rating_item.get("rating")
                        elif rating_item.get("ratingLabel") == "Sleep Quality":
                            sleep_rating = rating_item.get("rating")
                        elif rating_item.get("ratingLabel") == "Location":
                            location_rating = rating_item.get("rating")
                        elif rating_item.get("ratingLabel") == "Cleanliness":
                            cleanliness_rating = rating_item.get("rating")
                
                # Prepare other data for insert
                contribution_counts = review.get("contributionCounts", {})
                sum_all_ugc = None
                helpful_votes = review.get("helpfulVotes", 0)
                
                # Extract sumAllUgc from contributionCounts
                if contribution_counts and isinstance(contribution_counts, dict):
                    sum_all_ugc = contribution_counts.get("sumAllUgc")
                

                avatar_url = None
                if review.get("avatar") and isinstance(review["avatar"], dict):
                    avatar_url = review["avatar"].get("url")
                
                cursor.execute(
                    insert_query,
                    (
                        review_id,
                        location_id,
                        review.get("userId") or None,
                        review.get("username"),
                        review.get("title"),
                        review.get("text"),
                        translated_title,
                        translated_text,
                        is_translated,
                        review.get("rating"),
                        published_date,
                        review.get("language"),
                        value_rating,
                        service_rating,
                        food_rating,
                        atmosphere_rating,
                        sum_all_ugc,
                        helpful_votes,
                        avatar_url,
                        restaurant_key,
                        room_rating,
                        sleep_rating,
                        location_rating,
                        cleanliness_rating
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
        import traceback
        print(f"Error inserting reviews: {str(e)}", file=sys.stderr)
        error_line = traceback.extract_tb(sys.exc_info()[2])[-1].lineno
        print(f"Error inserting reviews: {str(e)}", file=sys.stderr)
        print(f"Error occurred at line: {error_line}", file=sys.stderr)
        print(f"Error type: {type(e).__name__}", file=sys.stderr)
        print(f"Full traceback:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 0
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()





def InsertRestaurantDetailsForGoogle(restaurant_data,restaurant_name,location_name):
    """
    Insert restaurant details from Google JSON data into the google_restaurant_details table.

    Args:
        restaurant_data (dict): The restaurant data extracted from Google
    """
    conn = None
    cursor = None

    try:
        # Database connection
        conn = psycopg2.connect(
            dbname=Scraping["Database"],
            user=Scraping["Username"],
            password=Scraping["Password"],
            host=Scraping["Host"],
            port=Scraping["Port"]
        )
        cursor = conn.cursor()

        # Extract data from restaurant_data
        name = restaurant_data.get("name")
        address = restaurant_data.get("address")
        website = restaurant_data.get("website")
        menu_url = restaurant_data.get("menu_url")
        phone = restaurant_data.get("phone")
        if isinstance(phone, list) and len(phone) > 0:
            phone = phone[0]  # Take the first phone number
        elif phone is None:
            phone = ""  # Default to empty string if no phone
        rating = str(restaurant_data.get("rating", ""))
        reviews = str(restaurant_data.get("reviews", ""))

        # Extract features
        features = restaurant_data.get("features", {})
        service_options = features.get("service_options", [])
        parking = features.get("parking", [])
        children = features.get("children", [])
        payments = features.get("payments", [])
        planning = features.get("planning", [])
        crowd = features.get("crowd", [])
        atmosphere = features.get("atmosphere", [])
        amenities = features.get("amenities", [])
        dining_options = features.get("dining_options", [])
        schedule = restaurant_data.get("schedule", {})


        google_review_name = restaurant_name + " " + location_name
        # address_key = address.replace(" ","_")
        real_returant_name = restaurant_name
        restaurant_name = restaurant_name.replace(" ","_")
        restaurant_name = restaurant_name.replace("'","")   
        location_name = location_name.replace(" ","_")
        
        address_data = split_us_address(address) or {}  # Ensure it's a dictionary
        street = address_data.get("street", "")
        city = address_data.get("city", "")
        state = address_data.get("state", "")
        postal_code = address_data.get("postal_code", "")
        country = address_data.get("country", "")

        business_key = location_name+"_"+street+"_"+city+"_"+state+"_"+postal_code+"_"+restaurant_name
        business_key = business_key.replace(",","")
       
        check_query = """
                    SELECT COUNT(*) FROM google_restaurant_details 
                    WHERE phone = %s AND address = %s
                """
        cursor.execute(check_query, (phone, address))
        existing_count = cursor.fetchone()[0]

        if existing_count > 0:
            print(f"Restaurant already exists: {name}")
            return

        # Insert data into table
        insert_query = """
            INSERT INTO google_restaurant_details (
                name, address, website, menu_url, phone, 
                service_options, parking, children, payments, planning, 
                crowd, atmosphere, amenities, dining_options, schedule, 
                review_rating, review_count,restaurant_name,business_key,city,state,country,postal_code
            ) VALUES (
                %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, 
                %s,%s,%s,%s,%s,%s,%s
            )
        """

        cursor.execute(insert_query, (
            google_review_name, address, website, menu_url, phone,
            service_options, parking, children, payments, planning,
            crowd, atmosphere, amenities, dining_options, json.dumps(schedule),
            rating, reviews,real_returant_name,business_key,
            city, state, country,postal_code
        ))
        conn.commit()
        print(f"Inserted data for restaurant: {name}")

    except Exception as e:
        print(f"Error inserting restaurant details: {e}")
    # delete the record from google_restaurant_details table 
        import traceback
        print(traceback.format_exc())  # Print full traceback for debuggingwhere address is null
    try:
        cursor.execute("DELETE FROM google_restaurant_details WHERE address IS NULL or address='N/A'")
        conn.commit()
    except Exception as e:
        print(f"Error deleting records: {e}")
        import traceback
        print(traceback.format_exc())  # Print full traceback for debugging

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def InsertRestaurantReviewsForGoogle(review_data,business_key):
    try:
        conn = psycopg2.connect(
            dbname=Scraping["Database"],
            user=Scraping["Username"],
            password=Scraping["Password"],
            host=Scraping["Host"],
            port=Scraping["Port"]
        )
        cursor = conn.cursor()
         # Check for existing review by review_id
        cursor.execute("SELECT 1 FROM google_reviews WHERE review_id = %s", (review_data['review_id'],))
        if cursor.fetchone():
            print(f"Review with ID {review_data['review_id']} already exists. Skipping insertion.")
            return
        # Insert review data
        review_data['business_key'] = business_key
        cursor.execute("""
            INSERT INTO google_reviews (
                review_id, user_id, username, text, rating, published_date,
                created_at, avatar, service_rating, food_rating, atmosphere_rating, response_text,contribution,is_translated,translated_text,business_key, language
            ) VALUES (
                %(review_id)s, %(user_id)s, %(reviewer_name)s, %(review_text)s,
                %(rating)s, %(created_timestamp)s, %(extracted_date)s, %(profile_image)s,
                %(service)s, %(food_quality)s, %(atmosphere)s, %(response_text)s, %(total_reviews)s, %(is_translated)s, %(translated_text)s, %(business_key)s, %(language)s
            )
        """, review_data)

        # Insert photos
        for photo in review_data['photos']:
            cursor.execute("""
                INSERT INTO google_reviews_photos (
                    review_id, photo_url
                ) VALUES (
                    %(review_id)s, %(photo_url)s
                )
            """, {'review_id': review_data['review_id'], 'photo_url': photo['url']})

        conn.commit()
        print("Data inserted successfully.", review_data)
    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()


# write code to select name from trip_restaurants_details table
def select_name_from_trip_restaurants_details(query):
    conn = psycopg2.connect(
        dbname=Scraping["Database"],
        user=Scraping["Username"],
        password=Scraping["Password"],
        host=Scraping["Host"],
        port=Scraping["Port"]
    )
    cursor = conn.cursor()
    query = query.lower()
    cursor.execute("SELECT name FROM trip_restaurants_details WHERE restaurant_name = %s", (query,))
    
    results = cursor.fetchall()
    names = [row[0] for row in results]  # Extract names from tuples
    
    cursor.close()
    conn.close()
    
    return names  # Return a clean list

def select_restaurant_name_and_review_count_from_google_restaurant_details(query):
    """Fetch restaurant name and review count from the database."""
    try:
        # Connect to the database
        conn = psycopg2.connect(
            dbname=Scraping["Database"],
            user=Scraping["Username"],
            password=Scraping["Password"],
            host=Scraping["Host"],
            port=Scraping["Port"]
        )
        cursor = conn.cursor()
        
        # query = query.lower()  # Normalize query string
        
        # Execute the query
        cursor.execute("SELECT name, business_key FROM google_restaurant_details WHERE restaurant_name = %s", (query,))
        
        # Fetch results
        results = cursor.fetchall()
        print(results)
        # Return list of tuples (name, review_count)
        return [{"name": row[0], "business_key": row[1]} for row in results]

    except Exception as e:
        print(f"Database error: {e}")
        return []
    
    finally:
        # Ensure resources are always released
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()




def fetch_trip_data():
    """Fetch restaurant details separately and join reviews with their photos."""
    try:
        conn = psycopg2.connect(
            dbname=Scraping["Database"],
            user=Scraping["Username"],
            password=Scraping["Password"],
            host=Scraping["Host"],
            port=Scraping["Port"]
        )
        cursor = conn.cursor()

        # Fetch restaurant details with explicit column names
        cursor.execute("""
            SELECT id, location_id, name, address, city, state, country, postal_code, phone,
                   email, website, schedule, thumbnail, review_rating, review_count, dining_options,
                   cuisines, meal_types, diets, menu_url, has_menu_provider, restaurant_name,
                   business_key, service_options, parking, children, payments, planning, crowd,
                   atmosphere, amenities
            FROM trip_restaurants_details
        """,)

        details_columns = [desc[0] for desc in cursor.description]
        restaurant_details = cursor.fetchone()
        restaurant_details_dict = dict(zip(details_columns, restaurant_details)) if restaurant_details else {}

        # Fetch reviews and their associated photos using a JOIN with explicit column names
        cursor.execute("""
            SELECT tr.id, tr.review_id, tr.location_id, tr.user_id, tr.username, tr.title, tr.text,
                   tr.translated_title, tr.translated_text, tr.is_translated, tr.rating, tr.published_date,
                   tr.language, tr.created_at, tr.avatar, tr.contribution, tr.value_rating, tr.service_rating,
                   tr.food_rating, tr.atmosphere_rating, tr.likes, tr.business_key, tr.response_text,
                   tr.room_rating, tr.sleep_rating, tr.cleanliness_rating, tr.location_rating,
                   trp.photo_url
            FROM trip_reviews tr
            LEFT JOIN trip_review_photos trp ON tr.review_id = trp.review_id
           
        """,)

        reviews_dict = {}

        # Process review results
        for row in cursor.fetchall():
            review_id = row[1]
            photo_url = row[27]
            
            # If this is the first time seeing this review_id, create the entry
            if review_id not in reviews_dict:
                reviews_dict[review_id] = {
                    "id": row[0],
                    "review_id": review_id,
                    "location_id": row[2],
                    "user_id": row[3],
                    "username": row[4],
                    "title": row[5],
                    "text": row[6],
                    "translated_title": row[7],
                    "translated_text": row[8],
                    "is_translated": row[9],
                    "rating": float(row[10]) if isinstance(row[10], Decimal) else row[10],
                    "published_date": row[11],
                    "language": row[12],
                    "created_at": row[13],
                    "avatar": row[14],
                    "contribution": row[15],
                    "value_rating": row[16],
                    "service_rating": row[17],
                    "food_rating": row[18],
                    "atmosphere_rating": row[19],
                    "likes": row[20],
                    "business_key": row[21],
                    "response_text": row[22],
                    "room_rating": row[23],
                    "sleep_rating": row[24],
                    "cleanliness_rating": row[25],
                    "location_rating": row[26],
                    "photo_url": []
                }
            
            # Add the photo URL if it exists
            if photo_url:
                reviews_dict[review_id]["photo_url"].append(photo_url)

        # Convert dictionary to list of reviews
        reviews_list = list(reviews_dict.values())

        return {
            "restaurant_details": restaurant_details_dict,
            "reviews": reviews_list
        }

    except Exception as e:
        print(f"Database error: {e}")
        import traceback
        traceback.print_exc()
        return {}

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


def fetch_google_data():
    """Fetch restaurant details separately and join reviews with their photos."""
    try:
        conn = psycopg2.connect(
            dbname=Scraping["Database"],
            user=Scraping["Username"],
            password=Scraping["Password"],
            host=Scraping["Host"],
            port=Scraping["Port"]
        )
        cursor = conn.cursor()

        # Fetch restaurant details with explicit column names
        cursor.execute("""
            SELECT id, location_id, name, address, city, state, country, postal_code, phone,
                   email, website, schedule, thumbnail, review_rating, review_count, dining_options,
                   cuisines, meal_types, diets, menu_url, has_menu_provider, restaurant_name,
                   business_key, service_options, parking, children, payments, planning, crowd,
                   atmosphere, amenities
            FROM google_restaurant_details
        """,)

        details_columns = [desc[0] for desc in cursor.description]
        restaurant_details = cursor.fetchone()
        restaurant_details_dict = dict(zip(details_columns, restaurant_details)) if restaurant_details else {}

        # Fetch reviews and their associated photos using a JOIN with explicit column names
        cursor.execute("""
            SELECT tr.id, tr.review_id, tr.location_id, tr.user_id, tr.username, tr.title, tr.text,
                   tr.translated_title, tr.translated_text, tr.is_translated, tr.rating, tr.published_date,
                   tr.language, tr.created_at, tr.avatar, tr.contribution, tr.value_rating, tr.service_rating,
                   tr.food_rating, tr.atmosphere_rating, tr.likes, tr.business_key, tr.response_text,
                   tr.room_rating, tr.sleep_rating, tr.cleanliness_rating, tr.location_rating,
                   trp.photo_url
            FROM google_reviews tr
            LEFT JOIN google_reviews_photos trp ON tr.review_id = trp.review_id
           
        """,)

        reviews_dict = {}

        # Process review results
        for row in cursor.fetchall():
            review_id = row[1]
            photo_url = row[27]
            
            # If this is the first time seeing this review_id, create the entry
            if review_id not in reviews_dict:
                reviews_dict[review_id] = {
                    "id": row[0],
                    "review_id": review_id,
                    "location_id": row[2],
                    "user_id": row[3],
                    "username": row[4],
                    "title": row[5],
                    "text": row[6],
                    "translated_title": row[7],
                    "translated_text": row[8],
                    "is_translated": row[9],
                    "rating": float(row[10]) if isinstance(row[10], Decimal) else row[10],
                    "published_date": row[11],
                    "language": row[12],
                    "created_at": row[13],
                    "avatar": row[14],
                    "contribution": row[15],
                    "value_rating": row[16],
                    "service_rating": row[17],
                    "food_rating": row[18],
                    "atmosphere_rating": row[19],
                    "likes": row[20],
                    "business_key": row[21],
                    "response_text": row[22],
                    "room_rating": row[23],
                    "sleep_rating": row[24],
                    "cleanliness_rating": row[25],
                    "location_rating": row[26],
                    "photo_url": []
                }
            
            # Add the photo URL if it exists
            if photo_url:
                reviews_dict[review_id]["photo_url"].append(photo_url)

        # Convert dictionary to list of reviews
        reviews_list = list(reviews_dict.values())

        return {
            "restaurant_details": restaurant_details_dict,
            "reviews": reviews_list
        }

    except Exception as e:
        print(f"Database error: {e}")
        import traceback
        traceback.print_exc()
        return {}

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()