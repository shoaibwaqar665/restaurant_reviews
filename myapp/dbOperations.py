import uuid
import psycopg2  
import psycopg2.extras  
import sys 
import requests

from myapp.environment import  Scraping , Omni ,WebhookURL

Scraping = Scraping
Omni = Omni
webhookUrl = WebhookURL.get("WebhookURL")

def InsertTripadvisorReviews(
    review_text, 
    reviewer, 
    rating_value, 
    review_id,
    time_created_date, 
    time_created_time, 
    venue,
    venue_name,
):
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

        check_query = """
            SELECT COUNT(*)
            FROM tripadvisor_reviews
            WHERE review_text = %s 
              AND reviewer = %s 
              AND rating = %s
              AND review_id = %s
              AND time_created_date = %s
              AND time_created_time = %s
              AND venue=%s
              AND venue_name = %s
        """
        cursor.execute(check_query, (review_text, reviewer, rating_value , review_id,time_created_date,time_created_time,venue,venue_name))
        existing_count = cursor.fetchone()[0]

        if existing_count == 0:
            insert_query = """
                INSERT INTO tripadvisor_reviews (
                    review_text, 
                    reviewer, 
                    rating, 
                    review_id,
                    time_created_date,
                    time_created_time, 
                    venue,
                    venue_name
                ) 
                VALUES (%s, %s, %s, %s,%s, %s, %s, %s)
            """
            cursor.execute(
                insert_query,
                (
                    review_text, 
                    reviewer, 
                    rating_value,
                    review_id, 
                    time_created_date, 
                    time_created_time,
                    venue,
                    venue_name,
                )
            )
            conn.commit()
            print("review added to the database.")
        else:
            print("reviews already exists in the database. Skipping insertion.")
        
        return existing_count
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

 
def integration_sse(error, valid,locations):
    """Sends extracted data to a webhook."""
    webhook_url = f'{webhookUrl}integration/trigger/update'
    try:
        if not valid:
            payload = {
                "status": "false",
                "error": error,
                "platform": "Doordash",
                "closescreen": True
            }
        else:
            payload = {
                "status": "true",
                "locations": locations,
                "platform": "Doordash",
                "imageurl": "",
                "closescreen": True
            }
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 200:
            print(f"Data sent to webhook: {payload}")
        else:
            print(f"Payload: {payload}")
            print(f"Failed to send data to webhook. Status code: {response.status_code}")
            print(f"the webhookurl: {webhook_url}")
    except requests.RequestException as e:
        print(f"Failed to send data to webhook: {str(e)}")
        raise

# ------------------- getting the location from database ------------------------


def fetch_venue(location_guid):
    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(
            dbname=Omni["Database"],
            user=Omni["Username"],
            password=Omni["Password"],
            host=Omni["Host"],
            port=Omni["Port"]
        )
        cursor = conn.cursor()

        # SQL query
        print(location_guid,"location_guid in fetch venue")
        query = "SELECT venue FROM doordash_credentials WHERE location_guid = %s AND is_deleted ='0'"
        cursor.execute(query, (location_guid,))
        print
        
        # Fetching the first row
        record = cursor.fetchone()

        if record is None:
            print("No data found for the provided location_guid.")
            return None
        
        # Closing the cursor and connection
        print("The db data:", record[0])
        return record[0]
    
    except psycopg2.DatabaseError as error:
        print("Database error:", error)
    except Exception as ex:
        print("An error occurred:", ex)
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

def fetch_all_location_guids():
    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(
            dbname=Omni["Database"],
            user=Omni["Username"],
            password=Omni["Password"],
            host=Omni["Host"],
            port=Omni["Port"]
        )
        cursor = conn.cursor()

        # SQL query to fetch all location_guids where is_deleted is 0
        query = "SELECT location_guid FROM doordash_credentials WHERE is_deleted = '0'"
        cursor.execute(query)
        
        # Fetching all rows
        records = cursor.fetchall()

        # Extracting location_guids from the fetched records
        location_guids = [record[0] for record in records]

        # Closing the cursor and connection
        return location_guids
    
    except psycopg2.DatabaseError as error:
        print("Database error:", error)
    except Exception as ex:
        print("An error occurred:", ex)
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()




def GetPinByEmail(email,platform):
    conn = None
    cursor = None
    pin = None

    try:
        conn = psycopg2.connect(
            dbname=Scraping["Database"],
            user=Scraping["Username"],
            password=Scraping["Password"],
            host=Scraping["Host"],
            port=Scraping["Port"]
        )
        cursor = conn.cursor()

        query = """
            SELECT pin 
            FROM tbl_2fa 
            WHERE email = %s AND platform = %s
            LIMIT 1
        """
        cursor.execute(query, (email,platform,))
        pin = cursor.fetchone()

        if pin:
            return pin[0]  # Return the pin value
        else:
            print("No record found for the given email.")
            return None

    except Exception as e:
        print(f"Error retrieving PIN from DB: {str(e)}", file=sys.stderr)
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def sendImgUrlToWebHook(url, valid):
    """Sends extracted data to a webhook."""
    try:
        if not valid:
            payload = {
                "status": "false",
                "error": '',
                "platform": "Doordash"
            }
            print(f"Location Not Found: {payload}")

        else:
            # formatted_locations = [{'location': loc} for loc in locations]
            # locations_json = json.dumps(formatted_locations)
            payload = {
                "status": "true",
                "locations": '',
                "imageurl": url,
                "platform": "Doordash",
                "closescreen": False
            }
            print(f"Image Url sent to webhook: {payload}")
        
        response = requests.post(f"{webhookUrl}integration/trigger/update", json=payload)
        return response
    except requests.RequestException as e:
        print(f"Failed to send data to webhook: {str(e)}")
        raise


def fetch_credentials(location_guid):
    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(
            dbname=Omni["Database"],
            user=Omni["Username"],
            password=Omni["Password"],
            host=Omni["Host"],
            port=Omni["Port"]
        )
        cursor = conn.cursor()

        # SQL query with join and additional location_id column
        query = """
        SELECT email,password,venue FROM doordash_credentials
        WHERE location_guid = %s  AND is_deleted = '0'
        """
        cursor.execute(query, (location_guid,))
        
        # Fetching the first row
        record = cursor.fetchone()

        if record is None:
            # print("No data found for the provided location_guid.")
            return None
        
        # Closing the cursor and connection
        print(f"The db data: email={record[0]}, password={record[1]}, venue={record[2]}")
        return {
            "email": record[0],
            "password": record[1],
            "venue": record[2],
            
        }
    
    except psycopg2.DatabaseError as error:
        print("Database error:", error)
    except Exception as ex:
        print("An error occurred:", ex)
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
