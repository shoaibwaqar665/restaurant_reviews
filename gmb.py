from patchright.sync_api import sync_playwright
import time
import json
import os
import math
query = "D'Amores Famous Pizza Anaheim"
folder_name = query.replace(" ", "_")

def search_and_log_reviews():
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

                    file_name = f"responses_{folder_name}/{folder_name}_{int(time.time())}.json"
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

        # Perform search
        search_box = page.locator('input[name="q"]')
        search_box.click()
        search_box.fill(query)
        page.keyboard.press('Enter')
        page.wait_for_load_state('networkidle')
        print("Search results loaded")

        # Wait for the place's info panel
        # page.wait_for_selector(f'h1:has-text("{query}")', state='visible', timeout=10000)
        # print(f"Found {query} in results")
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
            time.sleep(5)
            samole_click = page.query_selector('div[class*="cVwbnc IlRKB"]')
            samole_click.click()

            print("Pressing 'End' key to load reviews...")
            total_reviews = 378
            const_val = 0.0873
            end_btn_range = round(total_reviews * const_val)
            print('end_btn_range: ', end_btn_range)

            for i in range(end_btn_range):
                print(i)
                page.keyboard.press('End')
                time.sleep(2)

        time.sleep(5)  # Additional wait for requests
        print("Review capture completed.")
        
        browser.close()

if __name__ == "__main__":
    search_and_log_reviews()
