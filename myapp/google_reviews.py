from patchright.sync_api import sync_playwright
import time
import json
from dotenv import load_dotenv
import os
load_dotenv()

from myapp.google_reviews_extraction import extract_google_reviews
from myapp.dbOperations import select_restaurant_name_and_review_count_from_google_business_details
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
def store_bucket_credentials():
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        response = s3.list_buckets()
        print("Buckets:", response['Buckets'])
    except NoCredentialsError:
        print("Credentials are not available.")

def upload_to_s3(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket and return the presigned URL"""
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    try:
        # Upload file
        s3_client.upload_file(file_name, bucket, object_name or file_name)

        s3_client.put_object_acl(ACL='public-read', Bucket=bucket, Key=object_name or file_name)

        url = f"https://{bucket}.s3.amazonaws.com/{object_name or file_name}"
        print(f"File {file_name} uploaded to {bucket}, URL: {url}")

        return url
    except Exception as e:

        print(f"Failed to upload {file_name} to S3: {str(e)}")
        return None

def search_and_log_reviews(address,review_count,folder_name,restaurant_name):
    with sync_playwright() as p:
        # Launch the browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        # Log all requests and capture response for specific URL
        def log_request(request):
            print(f"Request URL: {request.url}")

        def capture_response(response):
            if 'https://www.google.com/maps/rpc/listugcposts' in response.url:
                print(f"Captured Response URL: {response.url}")
                print(f"Status: {response.status}")
                try:
                    # Get the response as text
                    response_data = response.text()

                    # Remove Google Maps prefix if it exists
                    if response_data.startswith(")]}'\n"):
                        response_data = response_data[5:]

                    # Parse it as JSON
                    parsed_data = json.loads(response_data)

                    # Save it as a formatted JSON file
                    if not os.path.exists(f"responses_{folder_name}"):
                        os.makedirs(f"responses_{folder_name}")

                    file_name = os.path.join(f"responses_{folder_name}", f"{folder_name}_{int(time.time())}.json")
                    with open(file_name, 'w', encoding='utf-8') as f:
                        json.dump(parsed_data, f, ensure_ascii=False, indent=4)

                    print(f"Response saved to {file_name}")

                except Exception as e:
                    print(f"Error processing response: {e}")

        page.on('request', log_request)
        page.on('response', capture_response)

        # Navigate to Google Maps
        page.goto('https://maps.google.com')
        page.wait_for_load_state('networkidle')

        # Accept cookies if present
        if page.locator('text="Accept all"').is_visible():
            page.click('text="Accept all"')

        search_data = restaurant_name+" "+address
        # Perform search
        search_box = page.locator('input[name="q"]')
        search_box.click()
        search_box.fill(search_data)
        page.keyboard.press('Enter')
        page.wait_for_load_state('networkidle')
        print("Search results loaded")

        time.sleep(10)
        # Click on reviews
        reviews_selector = ['button:has-text("reviews")', 'a:has-text("reviews")', '[aria-label*="reviews"]']
        clicked_reviews = False

        for selector in reviews_selector:
            if page.locator(selector).count() > 0:
                print(f"Found reviews element with selector: {selector}")
                page.locator(selector).first.click()
                clicked_reviews = True
                break

        if not clicked_reviews:
            print("Could not find reviews selector. Taking screenshot.")
            page.screenshot(path="no_reviews_found.png")
        else:
            time.sleep(10)
            try:
                samole_click = page.query_selector('div[class*="cVwbnc IlRKB"]')
                samole_click.click()
            except Exception as e:
                screenshot_path = "end.png"
                page.screenshot(path=screenshot_path)
                url = upload_to_s3(screenshot_path, 's3teaconnect')
                if url:
                    print(f"Presigned URL for screenshot: {url}")
                try:
                    samole_click = page.query_selector('div[class*="YTkVxc"]')
                    samole_click.click()
                except Exception as e:
                    screenshot_path = "end.png"
                    page.screenshot(path=screenshot_path)
                    url = upload_to_s3(screenshot_path, 's3teaconnect')
                    if url:
                        print(f"Presigned URL for screenshot: {url}")
                    print(f"Error clicking lower review: {e}")
                print(f"Error clicking  uper review: {e}")

            print("Pressing 'End' key to load reviews...")
            # total_reviews = int(review_count)  # Convert to integer
            total_reviews = 360  # Convert to integer
            const_val = 0.0873
            end_btn_range = round(total_reviews * const_val)
            print('end_btn_range:', end_btn_range)


            for i in range(end_btn_range):
                print(i)
                page.keyboard.press('End')
                time.sleep(2)

        time.sleep(5)  # Additional wait for requests
        print("Review capture completed.")
        
        browser.close()

def google_reviews_data(restaurant_name):

    restaurant_name_and_review_count = select_restaurant_name_and_review_count_from_google_business_details(restaurant_name)
    for restaurant in restaurant_name_and_review_count:
        print(restaurant)
        address = restaurant["name"]
        business_key = restaurant["business_key"]
        folder_name = address.replace(" ", "_")
        folder_name = folder_name.replace("'", "")
        search_and_log_reviews(address,business_key,folder_name,restaurant_name)
        loc_reviews = address.replace(" ","_")
        loc_reviews = loc_reviews.replace("'","")
        extract_google_reviews(folder_name,loc_reviews,business_key)
